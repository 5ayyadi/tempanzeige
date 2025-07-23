import os
import logging
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the /start command is issued."""
    await update.message.reply_text("Welcome! Send me a message and I'll echo it back.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message back to them."""
    await update.message.reply_text(update.message.text)

def run_bot():
    """Run the bot with error handling and retry logic."""
    max_retries = 5
    retry_delay = 10  # seconds

    for attempt in range(max_retries):
        try:
            logger.info(f"Starting bot (attempt {attempt + 1}/{max_retries})...")

            app = ApplicationBuilder().token(BOT_TOKEN).build()

            # Command handler for /start
            app.add_handler(CommandHandler("start", start))

            # Message handler to echo messages
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

            logger.info("Bot is running...")
            app.run_polling()

        except Exception as e:
            logger.error(f"Bot crashed with error: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("Max retries reached. Bot will exit.")
                raise
