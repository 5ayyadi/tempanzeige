#!/usr/bin/env python3
"""
Simple test script to verify the MVP components work correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def test_models():
    """Test Pydantic models."""
    print("Testing Pydantic models...")
    from app.models.preferences import Location, Category, Price, Preference, UserPreferences
    
    # Test Location
    location = Location(city="Köln", state="Nordrhein-Westfalen")
    print(f"Location: {location}")
    
    # Test Category
    category = Category(category="Elektronik", subcategory="Handy & Telefon")
    print(f"Category: {category}")
    
    # Test Price
    price = Price(price_from=0, price_to=50)
    print(f"Price: {price}")
    
    # Test Preference
    preference = Preference(location=location, category=category, price=price)
    print(f"Preference: {preference}")
    
    print("✅ Models test passed!")

def test_llm_client():
    """Test LLM client."""
    print("\nTesting LLM client...")
    
    try:
        from app.core.llm_client import LLMClient
        
        # This will only work if OPENAI_API_KEY is set
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  OPENAI_API_KEY not set, skipping LLM test")
            return
        
        llm = LLMClient()
        
        # Test with simple input
        test_input = "Ich suche einen Stuhl in Berlin, max 30 Euro"
        result = llm.extract_preference_data(test_input)
        print(f"LLM extraction result: {result}")
        
        print("✅ LLM client test passed!")
        
    except Exception as e:
        print(f"⚠️  LLM client test failed: {e}")

def test_mongo_client():
    """Test MongoDB client."""
    print("\nTesting MongoDB client...")
    
    try:
        from app.core.mongo_client import MongoClientManager
        from app.models.preferences import Location, Category, Price, Preference
        
        # This will only work if MongoDB connection is available
        if not os.getenv("MONGO_URI"):
            print("⚠️  MONGO_URI not set, skipping MongoDB test")
            return
        
        mongo = MongoClientManager()
        
        # Create test preference
        location = Location(city="Test City")
        category = Category(category="Test Category")
        price = Price(price_to=100)
        preference = Preference(location=location, category=category, price=price)
        
        # Test user ID
        test_user_id = 12345
        
        # Add preference
        pref_id = mongo.add_user_preference(test_user_id, preference)
        print(f"Added preference with ID: {pref_id}")
        
        # Get preferences
        user_prefs = mongo.get_user_preferences(test_user_id)
        print(f"Retrieved preferences: {user_prefs}")
        
        # Clean up
        mongo.delete_all_user_preferences(test_user_id)
        print("Cleaned up test data")
        
        print("✅ MongoDB client test passed!")
        
    except Exception as e:
        print(f"⚠️  MongoDB client test failed: {e}")

if __name__ == "__main__":
    print("Running MVP component tests...\n")
    
    test_models()
    test_llm_client()
    test_mongo_client()
    
    print("\n🎉 Component tests completed!")
    print("\nTo run the bot:")
    print("1. Make sure you have set BOT_TOKEN, MONGO_URI, MONGO_DB_NAME, and OPENAI_API_KEY in .env")
    print("2. Run: python main.py")
