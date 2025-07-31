"""Gemini client for LLM operations using LangChain."""

import json
import logging
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

from core.config import config
from core.constants import DATA_DIR, CATEGORIES_FILE, CITIES_FILE
from prompts.prompts import PREFERENCE_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self.api_key = config.GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY must be set in the .env file")
        
        logger.info("Initializing Gemini client")
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=self.api_key,
            temperature=config.GEMINI_TEMPERATURE
        )
        
        data_path = Path(DATA_DIR)
        self.categories = self._load_json_data(data_path / CATEGORIES_FILE)
        self.cities = self._load_json_data(data_path / CITIES_FILE)
        logger.info("Gemini client initialized successfully")

    def _load_json_data(self, file_path: Path) -> dict:
        """Load JSON data from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def extract_preference_data(self, user_input: str) -> dict:
        """Extract structured preference data from user input using Gemini."""
        logger.info(f"Extracting preference data from: {user_input}")
        
        categories_info = json.dumps(self.categories, indent=2, ensure_ascii=False)
        cities_sample = self._get_cities_sample()
        
        system_prompt = f"""{PREFERENCE_EXTRACTION_PROMPT}

Available categories:
{categories_info}

Sample cities (there are more available):
{cities_sample}"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            result = response.content.strip()
            logger.info(f"LLM response: {result}")
            
            try:
                parsed_data = json.loads(result)
                cleaned_data = self._validate_and_clean_data(parsed_data)
                logger.info(f"Cleaned extracted data: {cleaned_data}")
                return cleaned_data
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON, trying fallback extraction")
                
                # Handle markdown code blocks
                if '```json' in result:
                    start = result.find('```json') + 7
                    end = result.find('```', start)
                    if end > start:
                        json_str = result[start:end].strip()
                        try:
                            parsed_data = json.loads(json_str)
                            cleaned_data = self._validate_and_clean_data(parsed_data)
                            logger.info(f"Cleaned extracted data from markdown: {cleaned_data}")
                            return cleaned_data
                        except json.JSONDecodeError:
                            logger.error("Failed to parse JSON from markdown block")
                
                # Fallback: find JSON object
                if '{' in result and '}' in result:
                    start = result.find('{')
                    end = result.rfind('}') + 1
                    json_str = result[start:end]
                    try:
                        parsed_data = json.loads(json_str)
                        cleaned_data = self._validate_and_clean_data(parsed_data)
                        logger.info(f"Cleaned extracted data from fallback: {cleaned_data}")
                        return cleaned_data
                    except json.JSONDecodeError:
                        logger.error("Failed to parse JSON from fallback extraction")
                
                logger.error("No valid JSON found in response")
                return self._empty_preference_data()
                    
        except Exception as e:
            logger.error(f"Gemini extraction error: {e}")
            return self._empty_preference_data()

    def _get_cities_sample(self) -> str:
        """Get a sample of cities for the prompt."""
        sample_cities = []
        count = 0
        for state, state_data in self.cities.items():
            if count >= 3:
                break
            cities_list = list(state_data.get("cities", {}).keys())[:5]
            sample_cities.append(f"{state}: {', '.join(cities_list)}")
            count += 1
        return "\n".join(sample_cities)

    def _validate_and_clean_data(self, data: dict) -> dict:
        """Validate and clean extracted data."""
        cleaned = {
            "location": {},
            "category": {},
            "price": {"price_from": 0, "price_to": 0},
            "time_window": 604800
        }
        
        if "location" in data and data["location"]:
            loc = data["location"]
            if loc.get("city"):
                cleaned["location"]["city"] = loc["city"]
                city_id, state, state_id = self._find_city_details(loc["city"])
                if city_id:
                    cleaned["location"]["city_id"] = city_id
                if state:
                    cleaned["location"]["state"] = state
                if state_id:
                    cleaned["location"]["state_id"] = state_id
        
        if "category" in data and data["category"]:
            cat = data["category"]
            category_info = self._find_category_details(cat.get("category"), cat.get("subcategory"))
            cleaned["category"].update(category_info)
        
        if "price" in data and data["price"]:
            price = data["price"]
            if isinstance(price.get("price_from"), (int, float)):
                cleaned["price"]["price_from"] = int(price["price_from"])
            if isinstance(price.get("price_to"), (int, float)):
                cleaned["price"]["price_to"] = int(price["price_to"])
        
        if "time_window" in data and isinstance(data["time_window"], (int, float)):
            cleaned["time_window"] = int(data["time_window"])
        
        return cleaned

    def _find_city_details(self, city_name: str) -> tuple[str | None, str | None, str | None]:
        """Find city_id, state, and state_id for a given city name."""
        for state, state_data in self.cities.items():
            if "cities" in state_data:
                for city, city_id in state_data["cities"].items():
                    if city.lower() == city_name.lower():
                        return city_id, state, state_data.get("id")
        return None, None, None

    def _find_category_details(self, category_name: str | None, subcategory_name: str | None) -> dict:
        """Find category and subcategory IDs."""
        result = {}
        
        if category_name:
            for cat, cat_data in self.categories.items():
                if cat.lower() == category_name.lower():
                    result["category"] = cat
                    result["category_id"] = cat_data.get("id")
                    break
        
        if subcategory_name:
            for cat, cat_data in self.categories.items():
                if "subcategories" in cat_data:
                    for subcat, subcat_id in cat_data["subcategories"].items():
                        if subcat.lower() == subcategory_name.lower():
                            result["subcategory"] = subcat
                            result["subcategory_id"] = subcat_id
                            if not result.get("category"):
                                result["category"] = cat
                                result["category_id"] = cat_data.get("id")
                            break
        
        return result

    def _empty_preference_data(self) -> dict:
        """Return empty preference data structure."""
        return {
            "location": {},
            "category": {},
            "price": {"price_from": 0, "price_to": 0},
            "time_window": 604800
        }
