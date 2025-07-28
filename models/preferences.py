from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Location(BaseModel):
    city: str | None = None
    state: str | None = None
    city_id: str | None = None
    state_id: str | None = None

class Category(BaseModel):
    category: str | None = None
    subcategory: str | None = None
    category_id: str | None = None
    subcategory_id: str | None = None

class Price(BaseModel):
    price_from: int = 0
    price_to: int = 0

class Preference(BaseModel):
    _id: str | None = None
    location: Location
    category: Category
    price: Price = Price()
    time_window: int = 604800  # one week in seconds
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserPreferences(BaseModel):
    _id: str | None = None
    user_id: int
    preferences: list[Preference] = []
