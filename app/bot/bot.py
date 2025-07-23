import os
import logging
import time
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
    """Send a welcome message with main menu when the /start command is issued."""
    welcome_text = """
🌡️ **Welcome to TempAnzeige Bot!**

Your personal temperature and weather monitoring assistant.

Please choose an option from the menu below:
    """

    keyboard = [
        [KeyboardButton("🏠 Set Preferences"), KeyboardButton("ℹ️ Help")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main menu."""
    menu_text = """
🏠 **Main Menu**

Choose an option:
    """

    keyboard = [
        [KeyboardButton("🏠 Set Preferences"), KeyboardButton("ℹ️ Help")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages from users."""
    message_text = update.message.text

    if message_text == "🏠 Set Preferences":
        await handle_set_preferences(update, context)
    elif message_text == "ℹ️ Help":
        await handle_help(update, context)
    elif message_text == "🔙 Back to Menu":
        await main_menu(update, context)
    else:
        # Echo other messages
        await update.message.reply_text(f"You said: {message_text}")

async def handle_set_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle set preferences button."""
    text = """
🏠 **Set Preferences**

Here you can configure your temperature monitoring preferences:

• Temperature units (°C/°F)
• Alert thresholds
• Notification frequency
• Monitoring locations

*This feature is coming soon!*
    """

    keyboard = [[KeyboardButton("🔙 Back to Menu")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help button."""
    text = """
ℹ️ **Help & Commands**

**Available Commands:**
• `/start` - Show main menu
• `/menu` - Return to main menu
• `/help` - Show this help message

**How to use:**
1. Set your preferences for temperature monitoring
2. Add locations you want to monitor
3. Configure alert settings
4. View temperature data and statistics

**Need more help?**
Contact support or check our documentation.
    """

    keyboard = [[KeyboardButton("🔙 Back to Menu")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

def run_bot():
    """Run the bot with error handling and retry logic."""
    max_retries = 5
    retry_delay = 10  # seconds

    for attempt in range(max_retries):
        try:
            logger.info(f"Starting bot (attempt {attempt + 1}/{max_retries})...")

            app = ApplicationBuilder().token(BOT_TOKEN).build()

            # Command handlers
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("menu", main_menu))
            app.add_handler(CommandHandler("help", handle_help))

            # Message handler for keyboard button presses and other text
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

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
