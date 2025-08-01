import time
import logging
from datetime import datetime
from core.mongo_client import MongoClientManager
from scraper.scraper import find_offers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class OffersScraper:
    def __init__(self, sleep_interval: int = 300):
        self.mongo_client = MongoClientManager()
        self.sleep_interval = sleep_interval

    def build_url_parts(self, preference) -> tuple[str, str]:
        """Build category and city URL parts from preference."""
        category_part = ""
        city_part = ""
        
        if preference.category.category_id:
            category_part = f"c{preference.category.category_id}/"
            if preference.category.subcategory_id:
                category_part = f"c{preference.category.subcategory_id}/"
        
        if preference.location.state_id:
            city_part = f"l{preference.location.state_id}/"
            if preference.location.city_id:
                city_part = f"l{preference.location.city_id}/"
                
        return category_part, city_part

    def get_scraping_tasks(self) -> list[tuple[str, str, dict]]:
        """Get unique scraping tasks from all user preferences."""
        all_user_prefs = self.mongo_client.get_all_user_preferences()
        tasks = set()
        
        for user_prefs in all_user_prefs:
            for preference in user_prefs.preferences:
                category_part, city_part = self.build_url_parts(preference)
                
                filter_criteria = {
                    "location.city_id": preference.location.city_id,
                    "location.state_id": preference.location.state_id,
                    "category.category_id": preference.category.category_id,
                    "category.subcategory_id": preference.category.subcategory_id,
                }
                
                task = (category_part, city_part, tuple(sorted(filter_criteria.items())))
                tasks.add(task)
        
        return [(cat, city, dict(criteria)) for cat, city, criteria in tasks]

    def scrape_offers(self):
        """Main scraping function."""
        logger.info("Starting offers scraping")
        tasks = self.get_scraping_tasks()
        
        if not tasks:
            logger.info("No user preferences found")
            return
            
        logger.info(f"Found {len(tasks)} unique scraping tasks")
        
        total_new_offers = 0
        for category_part, city_part, filter_criteria in tasks:
            try:
                existing_ids = self.mongo_client.get_existing_offer_ids(filter_criteria)
                offers = find_offers(category_part, city_part, existing_ids)
                
                if offers:
                    saved_ids = self.mongo_client.create_offers(offers)
                    total_new_offers += len(saved_ids)
                    logger.info(f"Saved {len(saved_ids)} new offers for {category_part}{city_part}")
                    
            except Exception as e:
                logger.error(f"Error scraping {category_part}{city_part}: {e}")
                
        logger.info(f"Scraping completed. Total new offers: {total_new_offers}")

    def run(self):
        """Run the scraper in a loop."""
        logger.info(f"Starting scraper with {self.sleep_interval}s interval")
        
        while True:
            try:
                start_time = datetime.now()
                self.scrape_offers()
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"Scraping cycle completed in {duration:.2f}s")
                
            except KeyboardInterrupt:
                logger.info("Scraper stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in scraper: {e}")
                
            logger.info(f"Sleeping for {self.sleep_interval}s")
            time.sleep(self.sleep_interval)

if __name__ == "__main__":
    scraper = OffersScraper()
    scraper.run()
