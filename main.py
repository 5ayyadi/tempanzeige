import logging

from config import config
from core.mongo_client import MongoClientManager
from bot.bot import run_bot

# Configure logging
logging.basicConfig(
    format=config.LOG_FORMAT,
    level=getattr(logging, config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

# Validate configuration
config.validate()

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
