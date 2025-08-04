"""Keyboard layouts for the Telegram bot."""

from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from core.constants import MENU_PREFERENCES, MENU_ADD_PREFERENCE, MENU_VIEW_PREFERENCES, MENU_REMOVE_PREFERENCE, MENU_BACK

def get_main_menu_keyboard():
    """Get the main menu keyboard."""
    keyboard = [
        [KeyboardButton(MENU_PREFERENCES)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_preferences_menu_keyboard():
    """Get the preferences menu keyboard."""
    keyboard = [
        [KeyboardButton(MENU_ADD_PREFERENCE)],
        [KeyboardButton(MENU_VIEW_PREFERENCES)],
        [KeyboardButton(MENU_REMOVE_PREFERENCE)],
        [KeyboardButton(MENU_BACK)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_remove_keyboard():
    """Get keyboard to remove custom keyboard."""
    return ReplyKeyboardRemove()
