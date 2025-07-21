import json
import openai
import os
from rapidfuzz import process, fuzz
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

load_dotenv()


# Hardcoded OpenAI API key (replace with your own later)
openai.api_key = os.getenv('OPENAI_API')

# OpenAI pricing for gpt-3.5-turbo (as of 2024): $0.50 per 1,000,000 tokens
OPENAI_PRICE_PER_1M = 0.50

# Paths to data files
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CATEGORIES_PATH = os.path.join(DATA_DIR, "categories.json")
CATEGORY_ID_PATH = os.path.join(DATA_DIR, "category_id.json")
CITIES_PATH = os.path.join(DATA_DIR, "cities.json")
LOCATION_ID_PATH = os.path.join(DATA_DIR, "location_id.json")

# Track OpenAI token usage
total_openai_tokens = 0


def load_data():
    with open(CATEGORIES_PATH, encoding="utf-8") as f:
        categories = json.load(f)
    with open(CATEGORY_ID_PATH, encoding="utf-8") as f:
        category_id = json.load(f)
    with open(CITIES_PATH, encoding="utf-8") as f:
        cities = json.load(f)
    with open(LOCATION_ID_PATH, encoding="utf-8") as f:
        location_id = json.load(f)
    return categories, category_id, cities, location_id


def ask_with_fuzzy(prompt, options, limit=5, show_hint=False):
    options = list(options)
    while True:
        print(prompt)
        if show_hint:
            print("Available options:")
            for i, opt in enumerate(options):
                print(f"  {i+1}. {opt}")
        user_input = input("Type your choice (name or number): ").strip()
        # Try number
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(options):
                return options[idx]
        # Fuzzy match
        matches = process.extract(
            user_input, options, scorer=fuzz.WRatio, limit=limit)
        print("Did you mean:")
        for i, (name, score, _) in enumerate(matches):
            print(f"{i+1}. {name} (score: {score})")
        print("0. None of these, retype")
        choice = input("Select the number of your choice: ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(matches):
                # Debug: print OpenAI token usage if any (for future LLM use)
                if total_openai_tokens > 0:
                    print(
                        f"[DEBUG] OpenAI tokens used so far: {total_openai_tokens}")
                return matches[idx-1][0]
            elif idx == 0:
                continue
        print("Invalid input. Please try again.")


def ask_price_range():
    while True:
        user_input = input(
            "Enter price range (e.g., '1 - 100') or '0' for free items: ").strip()
        if user_input == "0":
            return 0, 0
        # Accept formats like '1-100', '1 - 100', '  1- 100  '
        parts = user_input.replace(" ", "").split("-")
        if len(parts) == 2 and all(p.isdigit() for p in parts):
            price_min, price_max = map(int, parts)
            if price_min <= price_max:
                return price_min, price_max
            else:
                print("Start price must be less than or equal to end price.")
        else:
            print("Invalid input. Please enter as 'start - end' or '0' for free items.")


def timeframe_to_timestamp(timeframe):
    now = datetime.now()
    tf = timeframe.lower().strip()
    if tf.startswith("1 day"):
        earliest = now - timedelta(days=1)
    elif tf.startswith("3 days"):
        earliest = now - timedelta(days=3)
    elif tf.startswith("7 days"):
        earliest = now - timedelta(days=7)
    elif tf.startswith("14 days"):
        earliest = now - timedelta(days=14)
    elif tf.startswith("1 month"):
        earliest = now - timedelta(days=30)
    elif tf.startswith("3 months"):
        earliest = now - timedelta(days=90)
    else:
        earliest = now
    return int(earliest.timestamp())


def print_token_usage():
    price = total_openai_tokens / 1_000_000 * OPENAI_PRICE_PER_1M
    print(f"\n[OpenAI usage] Total tokens: {total_openai_tokens}")
    print(f"[OpenAI usage] Estimated price: ${price:.6f}")


def main():
    print("Welcome to the AI-powered User Preferences Setup!\n")
    categories, category_id, cities, location_id = load_data()

    # Step 1: Category
    category_names = list(categories.keys())
    category = ask_with_fuzzy(
        "Which main category are you interested in?", category_names, show_hint=True)
    category_id_val = categories[category]["id"]

    # Step 2: Subcategory
    subcat_dict = categories[category]["subcategories"]
    subcat_names = list(subcat_dict.keys())
    subcategory = ask_with_fuzzy(
        f"Which subcategory in '{category}'?", subcat_names, show_hint=True)
    subcategory_id_val = subcat_dict[subcategory]

    # Step 3: State
    state_names = list(cities.keys())
    state = ask_with_fuzzy("Which state are you in?",
                           state_names, show_hint=True)
    state_id_val = cities[state]["id"]

    # Step 4: City
    city_dict = cities[state]["cities"]
    city = ask_with_fuzzy(
        f"Please type your city name in '{state}':", city_dict.keys(), show_hint=False)
    city_id_val = city_dict[city]

    # Step 5: Timeframe
    timeframe_options = [
        "1 day",
        "3 days",
        "7 days",
        "14 days",
        "1 month",
        "3 months"
    ]
    timeframe = ask_with_fuzzy(
        "For which timeframe do you want to see ads? (e.g., 1 day, 7 days, 1 month)",
        timeframe_options
    )
    timeframe_timestamp = timeframe_to_timestamp(timeframe)

    # Step 6: Price Range
    price_min, price_max = ask_price_range()

    # Build structured JSON
    result = {
        "category": category,
        "category_id": category_id_val,
        "subcategory": subcategory,
        "subcategory_id": subcategory_id_val,
        "state": state,
        "state_id": state_id_val,
        "city": city,
        "city_id": city_id_val,
        "timeframe": timeframe,
        "timeframe_timestamp": timeframe_timestamp,
        "price_min": price_min,
        "price_max": price_max
    }
    print("\nYour structured preferences:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print_token_usage()


if __name__ == "__main__":
    main()
