"""Keyboard layouts for the Telegram bot."""

from telegram import ReplyKeyboardMarkup, KeyboardButton
from constants import MENU_ADD_PREFERENCE, MENU_VIEW_PREFERENCES, MENU_REMOVE_PREFERENCE

def get_main_menu_keyboard():
    """Get the main menu keyboard."""
    keyboard = [
        [KeyboardButton(MENU_ADD_PREFERENCE)],
        [KeyboardButton(MENU_VIEW_PREFERENCES)],
        [KeyboardButton(MENU_REMOVE_PREFERENCE)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
