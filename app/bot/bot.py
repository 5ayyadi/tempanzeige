import os
import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
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
        [
            InlineKeyboardButton("🏠 Set Preferences", callback_data="set_preferences"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main menu."""
    menu_text = """
🏠 **Main Menu**

Choose an option:
    """

    keyboard = [
        [
            InlineKeyboardButton("🏠 Set Preferences", callback_data="set_preferences"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message back to them."""
    await update.message.reply_text(update.message.text)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == "set_preferences":
        await handle_set_preferences(update, context)
    elif query.data == "help":
        await handle_help(update, context)
    elif query.data == "back_to_menu":
        await main_menu(update, context)

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

    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

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

    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

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

            # Callback query handler for button presses
            app.add_handler(CallbackQueryHandler(button_handler))

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
