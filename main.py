import os
from dotenv import load_dotenv
from app.core.mongo_manager import MongoManager
from app.bot.bot import run_bot

load_dotenv()

# Example: print a variable from .env
if __name__ == "__main__":
    print("Running main.py inside Docker...")
    print(os.getenv('MY_VARIABLE', 'Variable not set'))

    # Initialize MongoManager
    manager = MongoManager()
    print("MongoManager initialized.")

    # Start the Telegram bot
    run_bot()
