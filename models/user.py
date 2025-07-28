from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Location(BaseModel):
    state: str | None = None
    state_id: str | None = None
    city: str | None = None
    city_id: str | None = None

class Category(BaseModel):
    category: str | None = None
    category_id: str | None = None
    subcategory: str | None = None
    subcategory_id: str | None = None

class Price(BaseModel):
    price_from: int = 0
    price_to: int = 0

class Preference(BaseModel):
    location: Location
    category: Category
    price: Price = Price()
    time_window: int = 604800  # one week in seconds
    created_at: datetime = Field(default_factory=datetime.now(tz=timezone.utc))

class UserModel(BaseModel):
    user_id: int
    name: str | None = None
    preferences: list[Preference] = []
    time_window: int = 604800  # one week in seconds
