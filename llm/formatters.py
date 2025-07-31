"""Utility functions for formatting preference data."""

from models.preferences import Location, Category, Price

def format_location(location: Location) -> str:
    """Format location for display."""
    if location.city:
        if location.state:
            return f"{location.city}, {location.state}"
        return location.city
    return "Any location"

def format_category(category: Category) -> str:
    """Format category for display."""
    if category.subcategory:
        return category.subcategory
    elif category.category:
        return category.category
    return "Any category"

def format_price(price: Price) -> str:
    """Format price for display."""
    if price.price_from == 0 and price.price_to == 0:
        return "Free (verschenken)"
    elif price.price_from == 0:
        return f"Up to {price.price_to} EUR"
    elif price.price_to == 0:
        return f"From {price.price_from} EUR"
    else:
        return f"{price.price_from} EUR - {price.price_to} EUR"

def format_time_window(seconds: int) -> str:
    """Format time window for display."""
    days = seconds // 86400
    if days == 1:
        return "1 day"
    elif days == 7:
        return "1 week"
    else:
        return f"{days} days"

def format_preference_summary(location: Location, category: Category, price: Price, time_window: int) -> str:
    """Format a complete preference summary for display."""
    return (
        f"📍 **Location:** {format_location(location)}\n"
        f"🏷️ **Category:** {format_category(category)}\n"
        f"💰 **Price:** {format_price(price)}\n"
        f"⏰ **Time window:** {format_time_window(time_window)}"
    )
