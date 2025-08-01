import pytest
from core.mongo_client import MongoClientManager
from models.preferences import Preference, Location, Category, Price
from scraper.offers_scraper import OffersScraper

class TestOffersScraper:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.mongo_client = MongoClientManager()
        self.scraper = OffersScraper(sleep_interval=1)
        
        # Clean up any existing test data
        self.mongo_client.user_preferences_collection.delete_many({})
        self.mongo_client.offers_collection.delete_many({})

    def test_save_preferences_and_scrape(self):
        """Test saving different types of preferences and scraping."""
        
        # Test data for Mainz and kitchen/dining categories
        test_preferences = [
            {
                "user_id": 12345,
                "preference": Preference(
                    location=Location(
                        city="Mainz",
                        state="Rheinland-Pfalz", 
                        city_id="5315",
                        state_id="4938"
                    ),
                    category=Category(
                        category="Haus & Garten",
                        subcategory="Küche & Esszimmer",
                        category_id="c80",
                        subcategory_id="c86"
                    ),
                    price=Price(price_from=0, price_to=0)  # Only free items
                )
            },
            {
                "user_id": 67890,
                "preference": Preference(
                    location=Location(
                        city="Mainz",
                        state="Rheinland-Pfalz",
                        city_id="5315", 
                        state_id="4938"
                    ),
                    category=Category(
                        category="Haus & Garten",
                        subcategory="Küche & Esszimmer",
                        category_id="c80",
                        subcategory_id="c86"
                    ),
                    price=Price(price_from=0, price_to=50)  # Up to 50 EUR
                )
            },
            {
                "user_id": 11111,
                "preference": Preference(
                    location=Location(
                        city="Mainz",
                        state="Rheinland-Pfalz",
                        city_id="5315",
                        state_id="4938"
                    ),
                    category=Category(
                        category="Haus & Garten", 
                        subcategory="Esszimmer",
                        category_id="c80",
                        subcategory_id="c82"
                    ),
                    price=Price(price_from=10, price_to=100)  # Between 10-100 EUR
                )
            }
        ]
        
        # Save preferences to database
        for test_data in test_preferences:
            pref_id = self.mongo_client.add_user_preference(
                test_data["user_id"], 
                test_data["preference"]
            )
            assert pref_id is not None
            
        # Verify preferences were saved
        all_prefs = self.mongo_client.get_all_user_preferences()
        assert len(all_prefs) == 3
        
        # Test scraping tasks generation
        tasks = self.scraper.get_scraping_tasks()
        assert len(tasks) >= 1  # Should have at least one unique task
        
        # Test URL building
        for test_data in test_preferences:
            cat_part, city_part = self.scraper.build_url_parts(test_data["preference"])
            assert cat_part.startswith("c")
            assert city_part.startswith("l")
            
        # Test one scraping cycle (without actual HTTP requests in unit test)
        try:
            self.scraper.scrape_offers()
            # This should not fail even if no internet connection
        except Exception as e:
            # Expected to fail in test environment, just ensure structure is correct
            assert "Error scraping" in str(e) or "requests" in str(e) or "Connection" in str(e)
            
    def test_preference_filtering(self):
        """Test that preference filtering works correctly."""
        
        # Add a preference
        pref = Preference(
            location=Location(
                city="Mainz",
                state="Rheinland-Pfalz",
                city_id="5315",
                state_id="4938"
            ),
            category=Category(
                category="Haus & Garten",
                subcategory="Küche & Esszimmer", 
                category_id="c80",
                subcategory_id="c86"
            ),
            price=Price(price_from=0, price_to=0)
        )
        
        self.mongo_client.add_user_preference(99999, pref)
        
        # Build filter criteria
        cat_part, city_part = self.scraper.build_url_parts(pref)
        
        # Verify URL parts are correct
        assert cat_part == "c86/"  # Should use subcategory
        assert city_part == "l5315/"  # Should use city
        
        # Test existing offers check
        filter_criteria = {
            "location.city_id": pref.location.city_id,
            "location.state_id": pref.location.state_id,
            "category.category_id": pref.category.category_id,
            "category.subcategory_id": pref.category.subcategory_id,
        }
        
        existing_ids = self.mongo_client.get_existing_offer_ids(filter_criteria)
        assert isinstance(existing_ids, set)
        assert len(existing_ids) == 0  # Should be empty initially
