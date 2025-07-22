import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoManager:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB_NAME")
        if not self.mongo_uri or not self.db_name:
            raise ValueError("MONGO_URI and MONGO_DB_NAME must be set in the .env file")

        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]

    def insert_document(self, collection_name, document):
        """Insert a document into a collection."""
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        return result.inserted_id

    def find_documents(self, collection_name, query):
        """Find documents in a collection based on a query."""
        collection = self.db[collection_name]
        return list(collection.find(query))

    def update_document(self, collection_name, query, update):
        """Update a document in a collection."""
        collection = self.db[collection_name]
        result = collection.update_one(query, {"$set": update})
        return result.modified_count

    def delete_document(self, collection_name, query):
        """Delete a document from a collection."""
        collection = self.db[collection_name]
        result = collection.delete_one(query)
        return result.deleted_count

    def save_user_preferences(self, user_id, preferences):
        """Save user preferences into the 'user_preferences' collection."""
        collection = self.db['user_preferences']
        document = {"user_id": user_id, "preferences": preferences}
        result = collection.update_one({"user_id": user_id}, {"$set": document}, upsert=True)
        return result.upserted_id or result.modified_count

    def get_user_preferences(self, user_id):
        """Retrieve user preferences from the 'user_preferences' collection."""
        collection = self.db['user_preferences']
        document = collection.find_one({"user_id": user_id})
        return document

    def get_all_user_preferences(self):
        """Retrieve all user preferences from the 'user_preferences' collection."""
        collection = self.db['user_preferences']
        return list(collection.find())

    def remove_user_preferences(self, user_id):
        """Remove user preferences from the 'user_preferences' collection."""
        collection = self.db['user_preferences']
        result = collection.delete_one({"user_id": user_id})
        return result.deleted_count
