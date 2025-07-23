"""Keyboard layouts for the Telegram bot."""

from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard():
    """Get the main menu keyboard."""
    keyboard = [
        [KeyboardButton("Add Preference")],
        [KeyboardButton("View Preferences")],
        [KeyboardButton("Remove Preference")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
