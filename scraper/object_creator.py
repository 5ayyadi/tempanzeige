import json
from pathlib import Path
from models.offer import Location, Category

def load_data():
    """Load categories and cities data."""
    data_path = Path(__file__).parent.parent / "data"
    
    with open(data_path / "categories.json", encoding="utf-8") as f:
        categories = json.load(f)
    with open(data_path / "category_id.json", encoding="utf-8") as f:
        category_id = json.load(f)
    with open(data_path / "cities.json", encoding="utf-8") as f:
        cities = json.load(f)
    with open(data_path / "location_id.json", encoding="utf-8") as f:
        location_id = json.load(f)
    
    return categories, category_id, cities, location_id

def create_category_object(category_name: str = "", subcategory_name: str = "") -> Category:
    """Create a Category object from names."""
    categories, _, _, _ = load_data()
    
    if not category_name:
        return Category()
    
    category_data = categories.get(category_name, {})
    category_id = category_data.get("id")
    subcategories = category_data.get("subcategories", {})
    
    if subcategory_name and subcategory_name in subcategories:
        subcategory_id = subcategories[subcategory_name]
    else:
        subcategory_id = None
        
    return Category(
        category_id=category_id,
        category_name=category_name,
        subcategory_id=subcategory_id,
        subcategory_name=subcategory_name
    )

def create_location_object(city_name: str = "", state_name: str = "") -> Location:
    """Create a Location object from names."""
    _, _, cities, _ = load_data()
    
    if not state_name:
        return Location()
    
    state_data = cities.get(state_name, {})
    state_id = state_data.get("id")
    cities_dict = state_data.get("cities", {})
    
    if city_name and city_name in cities_dict:
        city_id = cities_dict[city_name]
    else:
        city_id = None
        
    return Location(
        city_id=city_id,
        city_name=city_name,
        state_id=state_id,
        state_name=state_name
    )
