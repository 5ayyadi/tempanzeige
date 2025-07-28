import logging
from pymongo import MongoClient
from bson import ObjectId

from config import config
from models.preferences import UserPreferences, Preference

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
