import logging
import sys

from core.config import config
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

def run_offers_scraper():
    """Run the offers scraper."""
    from runners.offers_scraper import main as scraper_main
    scraper_main()

def run_message_sender():
    """Run the message sender."""
    from runners.message_sender import main as sender_main
    sender_main()

if __name__ == "__main__":
    logger.info("Starting application...")
    
    # Initialize MongoClientManager
    try:
        manager = MongoClientManager()
        logger.info("MongoClientManager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        exit(1)

    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "scraper":
            logger.info("Starting offers scraper")
            run_offers_scraper()
        elif command == "sender":
            logger.info("Starting message sender")
            run_message_sender()
        elif command == "bot":
            logger.info("Starting Telegram bot")
            run_bot()
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: bot, scraper, sender")
            exit(1)
    else:
        # Default: start the Telegram bot
        logger.info("Starting Telegram bot (default)")
        try:
            run_bot()
        except Exception as e:
            logger.error(f"Bot failed to start: {e}")
            exit(1)
