import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
from scraper.parse_data import parse_verschenken_offer, parse_priced_offer
from scraper.object_creator import create_category_object, create_location_object

BASE_URL = "https://www.kleinanzeigen.de"
CUTOFF_DATE = 90

def scrap_category_location(soup: BeautifulSoup) -> dict[str, str]:
    """Extract category and location from breadcrumb."""
    category, subcategory, state, city = None, None, None, None
    
    breadcrumb_tag = soup.find("div", class_="breadcrump")
    if breadcrumb_tag:
        links = breadcrumb_tag.find_all("a", class_="breadcrump-link")
        if len(links) >= 1:
            state_city_tag = breadcrumb_tag.find("h1").find("span", class_="breadcrump-summary")
            if state_city_tag and " in " in state_city_tag.text:
                state_city = state_city_tag.text.split(" in ")[1]
                if " - " in state_city:
                    city, state = state_city.split(" - ")
                else:
                    city, state = None, state_city
            else:
                city, state = None, None

            category_link = breadcrumb_tag.find("a", class_="breadcrump-link", title=False)
            if category_link:
                category = category_link.text
                category_tag = breadcrumb_tag.find("h1").find("span", class_="breadcrump-leaf")
                subcategory = category_tag.text.split(" in ")[0]
            else:
                category_tag = breadcrumb_tag.find("h1").find("span", class_="breadcrump-leaf")
                if category_tag:
                    category = category_tag.text.split(" in ")[0]
                    subcategory = None
                else:
                    category, subcategory = None, None
                    
    return {
        "category": category.strip() if category else None,
        "subcategory": subcategory.strip() if subcategory else None,
        "state": state.strip() if state else None,
        "city": city.strip() if city else None
    }

def find_offers(category_id: str = None, city_id: str = None, existing_offer_ids: set = None, max_price: float = 0) -> list[dict]:
    """Find offers based on category and city filters up to max_price."""
    if existing_offer_ids is None:
        existing_offer_ids = set()
        
    results = []
    page_number = 1
    
    while True:
        url = f"{BASE_URL}/sortierung:preis/seite:{page_number}/{category_id}{city_id}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {page_number}: {e}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        offers = soup.find_all("div", class_="aditem-main--middle--price-shipping")
        
        if not offers:
            break
            
        category_location_dict = scrap_category_location(soup)
        category = create_category_object(
            category_name=category_location_dict.get("category"),
            subcategory_name=category_location_dict.get("subcategory"),
        )
        
        location = create_location_object(
            state_name=category_location_dict.get("state"),
            city_name=category_location_dict.get("city"),
        )

        should_continue = False
        for offer in offers:
            price_element = offer.find("p", class_="aditem-main--middle--price-shipping--price")
            
            if not price_element:
                continue
                
            price_text = price_element.text.strip()
            offer_item = offer.find_parent("article", class_="aditem")
            
            if not offer_item:
                continue
            
            # Handle "Zu verschenken" (free) offers
            if "Zu verschenken" in price_text:
                parsed_offer = parse_verschenken_offer(offer_item, location, category)
                if parsed_offer and parsed_offer.id not in existing_offer_ids:
                    offer_date = date.fromisoformat(parsed_offer.offer_date)
                    if offer_date < date.today() - timedelta(days=CUTOFF_DATE):
                        return results
                    results.append(parsed_offer.model_dump(by_alias=True))
                should_continue = True
                
            # Handle priced offers
            elif "€" in price_text and "VB" not in price_text:
                # Extract price from text like "25 €" or "25,50 €"
                try:
                    price_value = float(price_text.replace("€", "").replace(",", ".").strip())
                    
                    # If we've reached our max_price limit, stop scraping
                    if max_price != float('inf') and price_value > max_price:
                        return results
                    
                    # Parse priced offer if within our range
                    parsed_offer = parse_priced_offer(offer_item, location, category, price_value)
                    if parsed_offer and parsed_offer.id not in existing_offer_ids:
                        offer_date = date.fromisoformat(parsed_offer.offer_date)
                        if offer_date < date.today() - timedelta(days=CUTOFF_DATE):
                            return results
                        results.append(parsed_offer.model_dump(by_alias=True))
                    should_continue = True
                    
                except ValueError:
                    # Could not parse price, skip this offer
                    continue
                    
            # VB (negotiable) offers - stop here as prices become unpredictable
            elif "VB" in price_text:
                return results
        
        # If no valid offers found on this page, try next page
        if not should_continue:
            break
            
        page_number += 1
        if page_number > 50:  # Increased safety limit for price-based scraping
            break
            
    return results
