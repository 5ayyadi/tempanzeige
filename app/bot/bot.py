import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

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
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handler for /start
    app.add_handler(CommandHandler("start", start))

    # Message handler to echo messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot is running...")
    app.run_polling()
