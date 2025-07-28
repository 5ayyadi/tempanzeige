"""Graph nodes for the preference extraction workflow."""

import logging

from llm.states import PreferenceState
from llm.gemini_client import GeminiClient
from llm.formatters import format_location, format_category, format_price, format_time_window
from core.mongo_client import MongoClientManager
from models.preferences import Location, Category, Price, Preference

logger = logging.getLogger(__name__)

gemini_client = GeminiClient()
mongo_client = MongoClientManager()

def extract_preference_node(state: PreferenceState) -> PreferenceState:
    """Extract preference data from user input."""
    try:
        logger.info(f"Starting preference extraction for input: {state.user_input}")
        extracted_data = gemini_client.extract_preference_data(state.user_input)
        
        logger.info(f"Creating Location object with: {extracted_data['location']}")
        location = Location(**extracted_data["location"])
        
        logger.info(f"Creating Category object with: {extracted_data['category']}")
        category = Category(**extracted_data["category"]) 
        
        logger.info(f"Creating Price object with: {extracted_data['price']}")
        price = Price(**extracted_data["price"])
        
        logger.info("Creating Preference object")
        preference = Preference(
            location=location,
            category=category,
            price=price,
            time_window=extracted_data["time_window"]
        )
        
        # Check if location is missing and should ask for it
        if not location.city:
            return PreferenceState(
                user_input=state.user_input,
                user_id=state.user_id,
                extracted_data=extracted_data,
                preference=preference,
                message="I found your search criteria, but no location was specified. In which city would you like to search?",
                next_action="location",
                is_complete=False,
                needs_location=True
            )
        
        # Show preliminary results and ask for refinement
        location_text = format_location(location)
        category_text = format_category(category)
        price_text = format_price(price)
        time_text = format_time_window(preference.time_window)
        
        refinement_message = f"""I found the following search preferences:

Location: {location_text}
Category: {category_text}
Price: {price_text}
Time window: {time_text}

Would you like to:
• Type 'save' to save this preference
• Type 'location' to change the location
• Type 'category' to change the category  
• Type 'price' to change the price
• Or describe any changes you'd like to make"""
        
        result_state = PreferenceState(
            user_input=state.user_input,
            user_id=state.user_id,
            extracted_data=extracted_data,
            preference=preference,
            message=refinement_message,
            next_action="refine",
            is_complete=False,
            needs_refinement=True
        )
        
        logger.info(f"Extract node completed, next_action: {result_state.next_action}")
        return result_state
    
    except Exception as e:
        logger.error(f"Error in extract_preference_node: {e}", exc_info=True)
        error_message = "Sorry, I couldn't process your request. Please try again with a different description."
        
        return PreferenceState(
            user_input=state.user_input,
            user_id=state.user_id,
            extracted_data={},
            preference=None,
            message=error_message,
            next_action="end",
            is_complete=True
        )

def confirm_preference_node(state: PreferenceState) -> PreferenceState:
    """Handle preference confirmation."""
    user_response = state.user_input.lower().strip()
    
    if user_response in ["yes", "y", "ja", "save", "speichern"]:
        try:
            mongo_client.add_user_preference(state.user_id, state.preference)
            return PreferenceState(
                user_input=state.user_input,
                user_id=state.user_id,
                extracted_data=state.extracted_data,
                preference=state.preference,
                message="Preference saved successfully!",
                next_action="done",
                is_complete=True
            )
        except Exception as e:
            return PreferenceState(
                user_input=state.user_input,
                user_id=state.user_id,
                extracted_data=state.extracted_data,
                preference=state.preference,
                message="Error saving preference. Please try again.",
                next_action="done",
                is_complete=True
            )
    
    elif user_response in ["no", "n", "nein", "cancel", "abbrechen"]:
        return PreferenceState(
            user_input=state.user_input,
            user_id=state.user_id,
            message="Preference cancelled.",
            next_action="done",
            is_complete=True
        )
    
    elif user_response in ["edit", "change", "modify", "aendern"]:
        return PreferenceState(
            user_input="",
            user_id=state.user_id,
            message="Please describe your search again with any changes:",
            next_action="extract",
            is_complete=False
        )
    
    else:
        return PreferenceState(
            user_input=state.user_input,
            user_id=state.user_id,
            extracted_data=state.extracted_data,
            preference=state.preference,
            message="Please answer with 'yes' to save, 'no' to cancel, or 'edit' to modify.",
            next_action="confirm",
            is_complete=False
        )

def location_node(state: PreferenceState) -> PreferenceState:
    """Handle location input when missing."""
    user_input = state.user_input.strip()
    
    # Try to extract city from user input (more flexible matching)
    city_info = gemini_client._find_city_details(user_input)
    if city_info[0]:  # city_id found
        # Find the properly capitalized city name from the database
        proper_city_name = None
        for state_name, state_data in gemini_client.cities.items():
            if "cities" in state_data:
                for city, city_id in state_data["cities"].items():
                    if city.lower() == user_input.lower():
                        proper_city_name = city
                        break
                if proper_city_name:
                    break
        
        # Update the preference with the new location
        updated_location = Location(
            city=proper_city_name or user_input.title(),
            city_id=city_info[0],
            state=city_info[1],
            state_id=city_info[2]
        )
        
        # Update preference
        preference = state.preference
        preference.location = updated_location
        
        # Now show refinement options
        location_text = format_location(updated_location)
        category_text = format_category(preference.category)
        price_text = format_price(preference.price)
        time_text = format_time_window(preference.time_window)
        
        refinement_message = f"""Great! Updated search preferences:

Location: {location_text}
Category: {category_text}
Price: {price_text}
Time window: {time_text}

Would you like to:
• Type 'save' to save this preference
• Type 'category' to change the category  
• Type 'price' to change the price
• Or describe any changes you'd like to make"""
        
        return PreferenceState(
            user_input=state.user_input,
            user_id=state.user_id,
            extracted_data=state.extracted_data,
            preference=preference,
            message=refinement_message,
            next_action="refine",
            is_complete=False
        )
    else:
        return PreferenceState(
            user_input=state.user_input,
            user_id=state.user_id,
            extracted_data=state.extracted_data,
            preference=state.preference,
            message="I couldn't find that city. Please try again with a different city name:",
            next_action="location",
            is_complete=False,
            needs_location=True
        )

def refine_node(state: PreferenceState) -> PreferenceState:
    """Handle refinement requests."""
    user_response = state.user_input.lower().strip()
    
    if user_response in ["save", "ok", "yes", "ja", "speichern"]:
        # Move to final confirmation
        location_text = format_location(state.preference.location)
        category_text = format_category(state.preference.category)
        price_text = format_price(state.preference.price)
        time_text = format_time_window(state.preference.time_window)
        
        confirmation_message = f"""Final confirmation:

Location: {location_text}
Category: {category_text}
Price: {price_text}
Time window: {time_text}

Save this preference? (yes/no)"""
        
        return PreferenceState(
            user_input=state.user_input,
            user_id=state.user_id,
            extracted_data=state.extracted_data,
            preference=state.preference,
            message=confirmation_message,
            next_action="confirm",
            is_complete=False
        )
    
    elif user_response in ["location", "stadt", "ort"]:
        return PreferenceState(
            user_input=state.user_input,
            user_id=state.user_id,
            extracted_data=state.extracted_data,
            preference=state.preference,
            message="In which city would you like to search?",
            next_action="location",
            is_complete=False,
            needs_location=True
        )
    
    elif user_response in ["category", "kategorie"]:
        return PreferenceState(
            user_input=state.user_input,
            user_id=state.user_id,
            extracted_data=state.extracted_data,
            preference=state.preference,
            message="What are you looking for? (e.g., 'Sofa', 'Schreibtischstuhl', 'Xbox Controller')",
            next_action="extract",
            is_complete=False
        )
    
    elif user_response in ["price", "preis"]:
        return PreferenceState(
            user_input=state.user_input,
            user_id=state.user_id,
            extracted_data=state.extracted_data,
            preference=state.preference,
            message="What's your price range? (e.g., 'max 50 EUR', 'verschenken', 'bis 100 EUR')",
            next_action="extract", 
            is_complete=False
        )
    
    else:
        # Try to process the refinement by updating existing preference
        try:
            # Extract new data from user input
            new_extracted_data = gemini_client.extract_preference_data(state.user_input)
            
            # Merge with existing preference, keeping non-empty values
            existing_pref = state.preference
            merged_data = {
                "location": {},
                "category": {},
                "price": {"price_from": 0, "price_to": 0},
                "time_window": 604800
            }
            
            # Keep existing location if new one is empty
            if new_extracted_data.get("location", {}).get("city"):
                merged_data["location"] = new_extracted_data["location"]
            else:
                merged_data["location"] = {
                    "city": existing_pref.location.city,
                    "state": existing_pref.location.state,
                    "city_id": existing_pref.location.city_id,
                    "state_id": existing_pref.location.state_id
                }
            
            # Use new category if provided, otherwise keep existing
            if new_extracted_data.get("category", {}).get("category"):
                merged_data["category"] = new_extracted_data["category"]
            else:
                merged_data["category"] = {
                    "category": existing_pref.category.category,
                    "subcategory": existing_pref.category.subcategory,
                    "category_id": existing_pref.category.category_id,
                    "subcategory_id": existing_pref.category.subcategory_id
                }
            
            # Use new price if provided, otherwise keep existing
            if (new_extracted_data.get("price", {}).get("price_from") is not None or 
                new_extracted_data.get("price", {}).get("price_to") is not None):
                merged_data["price"] = new_extracted_data["price"]
            else:
                merged_data["price"] = {
                    "price_from": existing_pref.price.price_from,
                    "price_to": existing_pref.price.price_to
                }
            
            # Use new time_window if provided, otherwise keep existing
            if new_extracted_data.get("time_window"):
                merged_data["time_window"] = new_extracted_data["time_window"]
            else:
                merged_data["time_window"] = existing_pref.time_window
            
            # Create updated preference
            updated_location = Location(**merged_data["location"])
            updated_category = Category(**merged_data["category"])
            updated_price = Price(**merged_data["price"])
            
            updated_preference = Preference(
                location=updated_location,
                category=updated_category,
                price=updated_price,
                time_window=merged_data["time_window"]
            )
            
            # Show updated preferences
            location_text = format_location(updated_location)
            category_text = format_category(updated_category)
            price_text = format_price(updated_price)
            time_text = format_time_window(updated_preference.time_window)
            
            refinement_message = f"""Updated search preferences:

Location: {location_text}
Category: {category_text}
Price: {price_text}
Time window: {time_text}

Would you like to:
• Type 'save' to save this preference
• Type 'location' to change the location
• Type 'category' to change the category  
• Type 'price' to change the price
• Or describe any other changes"""
            
            return PreferenceState(
                user_input=state.user_input,
                user_id=state.user_id,
                extracted_data=merged_data,
                preference=updated_preference,
                message=refinement_message,
                next_action="refine",
                is_complete=False
            )
            
        except Exception as e:
            logger.error(f"Error in refine_node: {e}", exc_info=True)
            return PreferenceState(
                user_input=state.user_input,
                user_id=state.user_id,
                extracted_data=state.extracted_data,
                preference=state.preference,
                message="I didn't understand that. Please try: 'save', 'location', 'category', 'price', or describe your changes clearly.",
                next_action="refine",
                is_complete=False
            )
