import os
import logging
from dotenv import load_dotenv
from app.core.mongo_client import MongoClientManager
from app.bot.bot import run_bot

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Telegram bot application...")
    
    # Initialize MongoClientManager
    try:
        manager = MongoClientManager()
        logger.info("MongoClientManager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        exit(1)

    # Start the Telegram bot
    try:
        run_bot()
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        exit(1)
