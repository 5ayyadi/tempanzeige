import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv
from app.bot.handlers import start, main_menu, cancel, MAIN_MENU

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in the .env file")

def run_bot():
    """Run the Telegram bot."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()
