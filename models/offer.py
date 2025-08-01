from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Location(BaseModel):
    city_id: str | None = None
    city_name: str | None = None
    state_id: str | None = None
    state_name: str | None = None

class Category(BaseModel):
    category_id: str | None = None
    category_name: str | None = None
    subcategory_id: str | None = None
    subcategory_name: str | None = None

class Offer(BaseModel):
    id: str = Field(..., alias='_id')
    title: str
    description: str
    address: str
    link: str | None = None
    offer_date: str
    photos: list[str] = []
    location: Location
    category: Category
    price: float = 0.0  # 0 for "Zu verschenken", actual price for priced offers
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __init__(self, **data):
        if data.get("_id"):
            data["_id"] = str(data["_id"])
        super().__init__(**data)
