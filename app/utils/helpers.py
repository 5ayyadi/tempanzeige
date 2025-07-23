"""Utility functions for the Telegram bot."""

from datetime import datetime, timezone

def get_current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)

def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

def parse_time_window_text(text: str) -> int:
    """Parse natural language time window to seconds."""
    text = text.lower().strip()
    
    # Common time patterns
    time_mappings = {
        "1 day": 86400,
        "one day": 86400,
        "2 days": 172800,
        "two days": 172800,
        "3 days": 259200,
        "three days": 259200,
        "1 week": 604800,
        "one week": 604800,
        "2 weeks": 1209600,
        "two weeks": 1209600,
        "1 month": 2592000,
        "one month": 2592000,
    }
    
    for pattern, seconds in time_mappings.items():
        if pattern in text:
            return seconds
    
    # Default to one week
    return 604800
