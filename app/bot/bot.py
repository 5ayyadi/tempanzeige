import os
import logging
import time
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler

from dotenv import load_dotenv
from app.bot.handlers import start, main_menu, cancel, MAIN_MENU

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in the .env file")
    
def run_bot():
    """Run the Telegram bot."""
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            logger.info(f"Starting bot (attempt {attempt + 1}/{max_retries})")
            app = ApplicationBuilder().token(BOT_TOKEN).build()

            conv_handler = ConversationHandler(
                entry_points=[CommandHandler("start", start)],
                states={
                    MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
                },
                fallbacks=[CommandHandler("cancel", cancel)],
            )

            app.add_handler(conv_handler)

            logger.info("Bot started successfully. Polling for updates...")
            app.run_polling()
            break  # If we get here, the bot ran successfully

        except Exception as e:
            logger.error(f"Bot crashed with error: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("Max retries reached. Bot will exit.")
                raise
