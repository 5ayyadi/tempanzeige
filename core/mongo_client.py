import logging
from pymongo import MongoClient
from bson import ObjectId
from pymongo.errors import BulkWriteError

from core.config import config
from models.preferences import UserPreferences, Preference
from models.offer import Offer

logger = logging.getLogger(__name__)

class MongoClientManager:
    def __init__(self):
        self.mongo_uri = config.MONGO_URI
        self.db_name = config.MONGO_DB_NAME
        if not self.mongo_uri or not self.db_name:
            raise ValueError("MONGO_URI and MONGO_DB_NAME must be set in the .env file")

        logger.info(f"Connecting to MongoDB: {self.mongo_uri}")
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        self.user_preferences_collection = self.db["user_preferences"]
        self.offers_collection = self.db["offers"]
        logger.info("MongoDB connection established")

    def add_user_preference(self, user_id: int, preference: Preference) -> str:
        """Add a new preference for a user."""
        logger.info(f"Adding preference for user {user_id}")
        user_prefs = self.user_preferences_collection.find_one({"user_id": user_id})
        
        if user_prefs:
            preference_dict = preference.model_dump(exclude={"_id"})
            preference_dict["_id"] = str(ObjectId())
            
            self.user_preferences_collection.update_one(
                {"user_id": user_id},
                {"$push": {"preferences": preference_dict}}
            )
            logger.info(f"Updated existing user preferences for user {user_id}")
            return preference_dict["_id"]
        else:
            preference_dict = preference.model_dump(exclude={"_id"})
            preference_dict["_id"] = str(ObjectId())
            
            new_user_prefs = UserPreferences(
                user_id=user_id,
                preferences=[preference_dict]
            )
            
            result = self.user_preferences_collection.insert_one(
                new_user_prefs.model_dump(exclude={"_id"})
            )
            logger.info(f"Created new user preferences for user {user_id}")
            return preference_dict["_id"]

    def get_user_preferences(self, user_id: int) -> UserPreferences | None:
        """Get all preferences for a user."""
        user_prefs = self.user_preferences_collection.find_one({"user_id": user_id})
        if user_prefs:
            return UserPreferences(**user_prefs)
        return None

    def delete_user_preference(self, user_id: int, preference_id: str) -> bool:
        """Delete a specific preference for a user."""
        result = self.user_preferences_collection.update_one(
            {"user_id": user_id},
            {"$pull": {"preferences": {"_id": preference_id}}}
        )
        return result.modified_count > 0

    def delete_all_user_preferences(self, user_id: int) -> bool:
        """Delete all preferences for a user."""
        result = self.user_preferences_collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0

    def create_offers(self, offers: list[dict] | None = None) -> list[str]:
        """Create offers in the database."""
        if not offers:
            return []
            
        try:
            result = self.offers_collection.insert_many(offers, ordered=False)
            return [str(oid) for oid in result.inserted_ids]
        except BulkWriteError as e:
            logger.warning(f"Some offers already exist: {len(e.details.get('writeErrors', []))}")
            return [str(oid) for oid in e.details.get('insertedIds', [])]

    def get_offers(self, filter_criteria: dict) -> list[Offer]:
        """Get offers based on filter criteria."""
        offers_data = self.offers_collection.find(filter_criteria)
        return [Offer(**offer) for offer in offers_data]

    def get_existing_offer_ids(self, filter_criteria: dict) -> set[str]:
        """Get existing offer IDs for given criteria."""
        offers = self.offers_collection.find(filter_criteria, {"_id": 1})
        return {offer["_id"] for offer in offers}

    def get_all_user_preferences(self) -> list[UserPreferences]:
        """Get all user preferences."""
        all_prefs = self.user_preferences_collection.find()
        return [UserPreferences(**prefs) for prefs in all_prefs]
