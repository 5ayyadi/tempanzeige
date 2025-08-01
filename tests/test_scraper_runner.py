import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from core.mongo_client import MongoClientManager
from models.preferences import UserPreferences, Preference, Location, Category, Price
from runners.offers_scraper import OffersScraper

@pytest.fixture
def mongo_client():
    """Mock MongoDB client."""
    return MagicMock(spec=MongoClientManager)

@pytest.fixture
def scraper(mongo_client):
    """Create scraper instance with mocked mongo client."""
    scraper = OffersScraper()
    scraper.mongo_client = mongo_client
    return scraper

class TestScraperRunner:
    
    def test_save_preferences_with_price(self, mongo_client):
        """Test saving user preferences with price range."""
        # Create preference with price range
        preference = Preference(
            location=Location(
                city="Mainz",
                state="Rheinland-Pfalz",
                city_id="5324",
                state_id="10"
            ),
            category=Category(
                category="Haus & Garten",
                subcategory="Küche & Esszimmer",
                category_id="86",
                subcategory_id="86-5"
            ),
            price=Price(price_from=10, price_to=50)
        )
        
        user_prefs = UserPreferences(
            user_id=12345,
            preferences=[preference]
        )
        
        # Mock database response
        mongo_client.add_user_preference.return_value = "pref_id_123"
        
        # Save preference
        result = mongo_client.add_user_preference(12345, preference)
        
        # Verify
        assert result == "pref_id_123"
        mongo_client.add_user_preference.assert_called_once()
    
    def test_save_preferences_without_price(self, mongo_client):
        """Test saving user preferences without price (free items only)."""
        # Create preference without price (defaults to 0-0)
        preference = Preference(
            location=Location(
                city="Mainz",
                state="Rheinland-Pfalz", 
                city_id="5324",
                state_id="10"
            ),
            category=Category(
                category="Haus & Garten",
                subcategory="Küche & Esszimmer",
                category_id="86",
                subcategory_id="86-5"
            ),
            price=Price(price_from=0, price_to=0)  # Free items only
        )
        
        user_prefs = UserPreferences(
            user_id=67890,
            preferences=[preference]
        )
        
        # Mock database response
        mongo_client.add_user_preference.return_value = "pref_id_456"
        
        # Save preference
        result = mongo_client.add_user_preference(67890, preference)
        
        # Verify
        assert result == "pref_id_456"
        mongo_client.add_user_preference.assert_called_once()
        assert preference.price.price_from == 0
        assert preference.price.price_to == 0
    
    def test_save_preferences_with_starting_and_ending_price(self, mongo_client):
        """Test saving user preferences with both starting and ending price."""
        # Create preference with full price range
        preference = Preference(
            location=Location(
                city="Mainz",
                state="Rheinland-Pfalz",
                city_id="5324", 
                state_id="10"
            ),
            category=Category(
                category="Haus & Garten",
                subcategory="Küche & Esszimmer",
                category_id="86",
                subcategory_id="86-5"
            ),
            price=Price(price_from=20, price_to=100)
        )
        
        user_prefs = UserPreferences(
            user_id=11111,
            preferences=[preference]
        )
        
        # Mock database response
        mongo_client.add_user_preference.return_value = "pref_id_789"
        
        # Save preference
        result = mongo_client.add_user_preference(11111, preference)
        
        # Verify
        assert result == "pref_id_789"
        mongo_client.add_user_preference.assert_called_once()
        assert preference.price.price_from == 20
        assert preference.price.price_to == 100
    
    def test_build_scraping_urls(self, scraper):
        """Test building scraping URLs from user preferences."""
        # Create multiple user preferences
        prefs1 = UserPreferences(
            user_id=1,
            preferences=[
                Preference(
                    location=Location(city_id="5324", state_id="10"),
                    category=Category(category_id="86", subcategory_id="86-5"),
                    price=Price(price_from=0, price_to=0)
                )
            ]
        )
        
        prefs2 = UserPreferences(
            user_id=2, 
            preferences=[
                Preference(
                    location=Location(city_id="5324", state_id="10"),
                    category=Category(category_id="86", subcategory_id="86-5"),
                    price=Price(price_from=10, price_to=50)
                )
            ]
        )
        
        # Test URL building
        scraping_tasks = scraper.build_scraping_urls([prefs1, prefs2])
        
        # Should have one unique task (same category and location)
        assert len(scraping_tasks) == 1
        assert scraping_tasks[0]['category_id'] == "86-5"
        assert scraping_tasks[0]['city_id'] == "5324"
        assert len(scraping_tasks[0]['price_ranges']) == 2
    
    def test_filter_offers_by_price(self, scraper):
        """Test filtering offers by price ranges."""
        # Mock offers with different prices
        offers = [
            {"id": "1", "title": "Free table", "price": 0.0},
            {"id": "2", "title": "Cheap chair", "price": 15.0},
            {"id": "3", "title": "Expensive desk", "price": 75.0},
        ]
        
        # Test filtering for free items only
        price_ranges = [{"price_from": 0, "price_to": 0}]
        filtered = scraper.filter_offers_by_price(offers, price_ranges)
        assert len(filtered) == 1  # Only free item
        assert filtered[0]["price"] == 0.0
        
        # Test filtering for priced items in range
        price_ranges = [{"price_from": 10, "price_to": 50}]
        filtered = scraper.filter_offers_by_price(offers, price_ranges)
        assert len(filtered) == 1  # Only the 15 EUR item
        assert filtered[0]["price"] == 15.0
        
        # Test filtering for multiple ranges
        price_ranges = [
            {"price_from": 0, "price_to": 0},    # Free items
            {"price_from": 70, "price_to": 100}  # Expensive items
        ]
        filtered = scraper.filter_offers_by_price(offers, price_ranges)
        assert len(filtered) == 2  # Free item + expensive item
    
    @patch('runners.offers_scraper.find_offers')
    def test_scrape_and_save_offers(self, mock_find_offers, scraper):
        """Test the main scraping and saving logic."""
        # Mock user preferences
        user_prefs = UserPreferences(
            user_id=1,
            preferences=[
                Preference(
                    location=Location(city_id="5324", state_id="10"),
                    category=Category(category_id="86", subcategory_id="86-5"),
                    price=Price(price_from=0, price_to=0)
                )
            ]
        )
        
        # Mock database methods
        scraper.mongo_client.get_all_user_preferences.return_value = [user_prefs]
        scraper.mongo_client.get_existing_offer_ids.return_value = set()
        scraper.mongo_client.create_offers.return_value = ["offer_1", "offer_2"]
        
        # Mock scraped offers
        mock_find_offers.return_value = [
            {"id": "offer_1", "title": "Free table", "price": 0.0},
            {"id": "offer_2", "title": "Free chair", "price": 0.0}
        ]
        
        # Run scraping
        scraper.scrape_and_save_offers()
        
        # Verify calls
        scraper.mongo_client.get_all_user_preferences.assert_called_once()
        mock_find_offers.assert_called_once()
        scraper.mongo_client.create_offers.assert_called_once()
