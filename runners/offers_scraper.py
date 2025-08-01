import time
import logging
from datetime import datetime
from core.mongo_client import MongoClientManager
from scraper.scraper import find_offers
from models.preferences import UserPreferences

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SLEEP_INTERVAL = 300  # 5 minutes

class OffersScraper:
    def __init__(self):
        self.mongo_client = MongoClientManager()
    
    def build_scraping_urls(self, preferences: list[UserPreferences]) -> list[dict]:
        """Build list of unique scraping criteria from user preferences."""
        scraping_tasks = []
        seen_criteria = set()
        
        for user_prefs in preferences:
            for pref in user_prefs.preferences:
                category_id = pref.category.subcategory_id or pref.category.category_id
                city_id = pref.location.city_id or pref.location.state_id
                
                if not category_id or not city_id:
                    continue
                    
                criteria_key = f"{category_id}_{city_id}"
                if criteria_key not in seen_criteria:
                    seen_criteria.add(criteria_key)
                    scraping_tasks.append({
                        'category_id': category_id,
                        'city_id': city_id,
                        'price_ranges': []
                    })
        
        # Add price ranges for each unique criteria and merge overlapping ranges
        for task in scraping_tasks:
            price_ranges = []
            for user_prefs in preferences:
                for pref in user_prefs.preferences:
                    task_category_id = pref.category.subcategory_id or pref.category.category_id
                    task_city_id = pref.location.city_id or pref.location.state_id
                    
                    if (task['category_id'] == task_category_id and 
                        task['city_id'] == task_city_id):
                        price_range = {
                            'price_from': pref.price.price_from,
                            'price_to': pref.price.price_to
                        }
                        price_ranges.append(price_range)
            
            # Merge overlapping price ranges to determine optimal scraping range
            task['max_price'] = self._calculate_max_price_needed(price_ranges)
            task['price_ranges'] = price_ranges
        
        return scraping_tasks
    
    def _calculate_max_price_needed(self, price_ranges: list[dict]) -> int:
        """Calculate the maximum price we need to scrape up to."""
        max_price = 0
        
        for price_range in price_ranges:
            price_to = price_range['price_to']
            
            # If price_to is 0 and price_from > 0, this means "from X onwards" (unlimited)
            if price_to == 0 and price_range['price_from'] > 0:
                return float('inf')  # Need to scrape all prices
            
            # Otherwise, track the highest price_to
            if price_to > max_price:
                max_price = price_to
        
        return max_price
    
    def filter_offers_by_price(self, offers: list[dict], price_ranges: list[dict]) -> list[dict]:
        """Filter offers based on price ranges."""
        if not price_ranges:
            return offers
            
        filtered_offers = []
        for offer in offers:
            offer_price = offer.get('price', 0.0)
            
            for price_range in price_ranges:
                price_from = price_range['price_from']
                price_to = price_range['price_to']
                
                # If both price_from and price_to are 0, user wants free items
                if price_from == 0 and price_to == 0:
                    if offer_price == 0:
                        filtered_offers.append(offer)
                        break
                # If price_to is 0 but price_from > 0, user wants items from price_from onwards
                elif price_to == 0 and price_from > 0:
                    if offer_price >= price_from:
                        filtered_offers.append(offer)
                        break
                # Normal price range
                else:
                    if price_from <= offer_price <= price_to:
                        filtered_offers.append(offer)
                        break
        
        return filtered_offers
    
    def scrape_and_save_offers(self):
        """Main scraping function that runs continuously."""
        logger.info("Starting offers scraping session")
        
        # Get all user preferences
        all_preferences = self.mongo_client.get_all_user_preferences()
        if not all_preferences:
            logger.info("No user preferences found")
            return
        
        logger.info(f"Found {len(all_preferences)} users with preferences")
        
        # Build scraping tasks
        scraping_tasks = self.build_scraping_urls(all_preferences)
        logger.info(f"Generated {len(scraping_tasks)} unique scraping tasks")
        
        total_new_offers = 0
        
        for task in scraping_tasks:
            category_id = task['category_id']
            city_id = task['city_id']
            price_ranges = task['price_ranges']
            max_price = task['max_price']
            
            logger.info(f"Scraping category_id={category_id}, city_id={city_id}, max_price={max_price}")
            
            # Get existing offer IDs to avoid duplicates
            filter_criteria = {
                "location.city_id": city_id,
                "category.category_id": category_id
            }
            existing_offer_ids = self.mongo_client.get_existing_offer_ids(filter_criteria)
            
            # Scrape offers with pagination - continue until we reach max_price or no more offers
            offers = find_offers(category_id, city_id, existing_offer_ids, max_price)
            
            if offers:
                # Filter by price ranges
                filtered_offers = self.filter_offers_by_price(offers, price_ranges)
                
                if filtered_offers:
                    # Save to database
                    saved_ids = self.mongo_client.create_offers(filtered_offers)
                    total_new_offers += len(saved_ids)
                    logger.info(f"Saved {len(saved_ids)} new offers for category_id={category_id}, city_id={city_id}")
                else:
                    logger.info(f"No offers matched price criteria for category_id={category_id}, city_id={city_id}")
            else:
                logger.info(f"No new offers found for category_id={category_id}, city_id={city_id}")
        
        logger.info(f"Scraping session completed. Total new offers: {total_new_offers}")
    
    def run_continuous(self):
        """Run the scraper continuously with sleep intervals."""
        logger.info(f"Starting continuous scraper with {SLEEP_INTERVAL}s intervals")
        
        while True:
            try:
                start_time = datetime.now()
                self.scrape_and_save_offers()
                end_time = datetime.now()
                
                duration = (end_time - start_time).total_seconds()
                logger.info(f"Scraping session took {duration:.2f} seconds")
                
                logger.info(f"Sleeping for {SLEEP_INTERVAL} seconds...")
                time.sleep(SLEEP_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in scraping session: {e}")
                logger.info(f"Continuing after error, sleeping for {SLEEP_INTERVAL} seconds...")
                time.sleep(SLEEP_INTERVAL)

def main():
    scraper = OffersScraper()
    scraper.run_continuous()

if __name__ == "__main__":
    main()
