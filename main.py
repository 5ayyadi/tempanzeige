import os
import logging
import time
from dotenv import load_dotenv
from app.core.mongo_manager import MongoManager
from app.bot.bot import run_bot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

# Example: print a variable from .env
if __name__ == "__main__":
    logger.info("Running main.py inside Docker...")
    logger.info(f"Environment variable check: {os.getenv('MY_VARIABLE', 'Variable not set')}")

    # Initialize MongoManager with retry logic
    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to MongoDB (attempt {attempt + 1}/{max_retries})...")
            manager = MongoManager()
            logger.info("MongoManager initialized successfully.")
            break
        except Exception as e:
            logger.error(f"Failed to initialize MongoManager: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error("Failed to connect to MongoDB after all retries. Continuing without MongoDB...")

    # Start the Telegram bot
    try:
        run_bot()
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        # Keep container alive for debugging
        logger.info("Keeping container alive for debugging...")
        while True:
            time.sleep(60)
