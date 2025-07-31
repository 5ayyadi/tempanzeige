"""Utility functions for the Telegram bot."""

from datetime import datetime, timezone
from core.constants import (
    TIME_ONE_DAY, TIME_TWO_DAYS, TIME_THREE_DAYS, TIME_ONE_WEEK, 
    TIME_TWO_WEEKS, TIME_ONE_MONTH, DEFAULT_TIME_WINDOW
)

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
        "1 day": TIME_ONE_DAY,
        "one day": TIME_ONE_DAY,
        "2 days": TIME_TWO_DAYS,
        "two days": TIME_TWO_DAYS,
        "3 days": TIME_THREE_DAYS,
        "three days": TIME_THREE_DAYS,
        "1 week": TIME_ONE_WEEK,
        "one week": TIME_ONE_WEEK,
        "2 weeks": TIME_TWO_WEEKS,
        "two weeks": TIME_TWO_WEEKS,
        "1 month": TIME_ONE_MONTH,
        "one month": TIME_ONE_MONTH,
    }
    
    for pattern, seconds in time_mappings.items():
        if pattern in text:
            return seconds
    
    # Default to one week
    return DEFAULT_TIME_WINDOW
