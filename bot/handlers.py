"""Improved conversation handlers for the Telegram bot."""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from core.constants import (
    MAIN_MENU, MENU_ADD_PREFERENCE, MENU_VIEW_PREFERENCES, MENU_REMOVE_PREFERENCE,
    MSG_WELCOME, MSG_HELP, MSG_NO_PREFERENCES, MSG_PREFERENCES_REMOVED, 
    MSG_NO_PREFERENCES_TO_REMOVE, MSG_PREFERENCE_SAVED, MSG_ENTER_LOCATION, 
    MSG_ENTER_PRICE, MSG_ENTER_CATEGORY, MSG_ENTER_TIME, MSG_PROCESSING
)
from core.mongo_client import MongoClientManager
from llm.gemini_client import GeminiClient
from llm.formatters import format_location, format_category, format_price, format_time_window
from models.preferences import Location, Category, Price, Preference
from bot.keyboards import get_main_menu_keyboard, get_remove_keyboard

logger = logging.getLogger(__name__)
mongo_client = MongoClientManager()
gemini_client = GeminiClient()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the /start command is issued."""
    await update.message.reply_text(
        f"{MSG_WELCOME}\n{MSG_HELP}",
        reply_markup=get_main_menu_keyboard()
    )
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu selection and preference flow."""
    text = update.message.text
    
    if text == MENU_ADD_PREFERENCE:
        await update.message.reply_text(
            "Tell me what you're looking for! 🔍\n\n"
            "Example: 'Schreibtisch in München bis 50 Euro'",
            reply_markup=get_remove_keyboard()
        )
        context.user_data.pop("preference_draft", None)
        context.user_data.pop("awaiting_input", None)
        return MAIN_MENU
    
    elif text == MENU_VIEW_PREFERENCES:
        await show_user_preferences(update, context)
        return MAIN_MENU
    
    elif text == MENU_REMOVE_PREFERENCE:
        await remove_user_preferences(update, context)
        return MAIN_MENU
    
    # Handle preference input
    elif not context.user_data.get("awaiting_input"):
        await handle_preference_input(update, context)
        return MAIN_MENU
    
    # Handle specific edits
    elif context.user_data.get("awaiting_input") == "location":
        await handle_location_edit(update, context)
        return MAIN_MENU
    
    elif context.user_data.get("awaiting_input") == "price":
        await handle_price_edit(update, context)
        return MAIN_MENU
    
    elif context.user_data.get("awaiting_input") == "category":
        await handle_category_edit(update, context)
        return MAIN_MENU
    
    elif context.user_data.get("awaiting_input") == "time":
        await handle_time_edit(update, context)
        return MAIN_MENU
    
    else:
        await update.message.reply_text(
            "Please select an option from the menu:",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU

async def handle_preference_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process natural language preference input."""
    user_input = update.message.text
    
    try:
        processing_msg = await update.message.reply_text(MSG_PROCESSING)
        
        # Extract data using Gemini
        extracted_data = gemini_client.extract_preference_data(user_input)
        
        # Store in context
        context.user_data["preference_draft"] = extracted_data
        
        # Delete processing message
        await processing_msg.delete()
        
        # Show confirmation
        await show_confirmation(update, context, extracted_data)
        
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        await update.message.reply_text(
            "Sorry, I couldn't understand that. Please try again.",
            reply_markup=get_main_menu_keyboard()
        )

async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict):
    """Show preference confirmation with inline buttons."""
    location = Location(**data["location"])
    category = Category(**data["category"])
    price = Price(**data["price"])
    
    summary = (
        f"📍 **Location:** {format_location(location)}\n"
        f"🏷️ **Category:** {format_category(category)}\n"
        f"💰 **Price:** {format_price(price)}\n"
        f"⏰ **Time:** {format_time_window(data.get('time_window', 604800))}"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Save", callback_data="save")],
        [
            InlineKeyboardButton("📍 Edit Location", callback_data="edit_location"),
            InlineKeyboardButton("💰 Edit Price", callback_data="edit_price")
        ],
        [
            InlineKeyboardButton("🏷️ Change Category", callback_data="edit_category"),
            InlineKeyboardButton("⏰ Change Time", callback_data="edit_time")
        ]
    ]
    
    await update.message.reply_text(
        f"I found the following preferences:\n\n{summary}\n\nWhat would you like to do?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()  # Answer immediately to avoid timeout
    
    # Show processing message for better UX
    processing_msg = await query.edit_message_text(MSG_PROCESSING)
    
    try:
        if query.data == "save":
            await save_preference(update, context)
        
        elif query.data == "edit_location":
            context.user_data["awaiting_input"] = "location"
            await processing_msg.edit_text(MSG_ENTER_LOCATION)
        
        elif query.data == "edit_price":
            context.user_data["awaiting_input"] = "price"
            await processing_msg.edit_text(MSG_ENTER_PRICE)
        
        elif query.data == "edit_category":
            context.user_data["awaiting_input"] = "category"
            await processing_msg.edit_text(MSG_ENTER_CATEGORY)
        
        elif query.data == "edit_time":
            context.user_data["awaiting_input"] = "time"
            await processing_msg.edit_text(MSG_ENTER_TIME)
            
    except Exception as e:
        logger.error(f"Error handling callback: {e}")
        try:
            await processing_msg.edit_text("Sorry, something went wrong. Please try again.")
        except Exception:
            # If we can't edit the message, send a new one
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, something went wrong. Please try again.",
                reply_markup=get_main_menu_keyboard()
            )

async def handle_location_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location editing."""
    location_text = update.message.text.strip()
    
    try:
        processing_msg = await update.message.reply_text(MSG_PROCESSING)
        
        # Re-extract with new location
        location_data = gemini_client.extract_preference_data(f"location: {location_text}")["location"]
        
        # Update draft
        draft = context.user_data.get("preference_draft", {})
        draft["location"] = location_data
        context.user_data["preference_draft"] = draft
        context.user_data.pop("awaiting_input", None)
        
        await processing_msg.delete()
        await show_confirmation(update, context, draft)
        
    except Exception as e:
        logger.error(f"Error updating location: {e}")
        await update.message.reply_text(
            "Sorry, couldn't understand that location. Please try again:",
            reply_markup=get_main_menu_keyboard()
        )

async def handle_price_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle price editing."""
    price_text = update.message.text.strip()
    
    try:
        processing_msg = await update.message.reply_text(MSG_PROCESSING)
        
        # Re-extract with new price
        price_data = gemini_client.extract_preference_data(f"price: {price_text}")["price"]
        
        # Update draft
        draft = context.user_data.get("preference_draft", {})
        draft["price"] = price_data
        context.user_data["preference_draft"] = draft
        context.user_data.pop("awaiting_input", None)
        
        await processing_msg.delete()
        await show_confirmation(update, context, draft)
        
    except Exception as e:
        logger.error(f"Error updating price: {e}")
        await update.message.reply_text(
            "Sorry, couldn't understand that price. Please try again:",
            reply_markup=get_main_menu_keyboard()
        )

async def handle_category_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category editing."""
    category_text = update.message.text.strip()
    
    try:
        processing_msg = await update.message.reply_text(MSG_PROCESSING)
        
        # Re-extract with new category
        category_data = gemini_client.extract_preference_data(f"category: {category_text}")["category"]
        
        # Update draft
        draft = context.user_data.get("preference_draft", {})
        draft["category"] = category_data
        context.user_data["preference_draft"] = draft
        context.user_data.pop("awaiting_input", None)
        
        await processing_msg.delete()
        await show_confirmation(update, context, draft)
        
    except Exception as e:
        logger.error(f"Error updating category: {e}")
        await update.message.reply_text(
            "Sorry, couldn't understand that category. Please try again:",
            reply_markup=get_main_menu_keyboard()
        )

async def handle_time_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle time window editing."""
    time_text = update.message.text.strip()
    
    try:
        processing_msg = await update.message.reply_text(MSG_PROCESSING)
        
        # Re-extract with new time window
        time_data = gemini_client.extract_preference_data(f"time: {time_text}")["time_window"]
        
        # Update draft
        draft = context.user_data.get("preference_draft", {})
        draft["time_window"] = time_data
        context.user_data["preference_draft"] = draft
        context.user_data.pop("awaiting_input", None)
        
        await processing_msg.delete()
        await show_confirmation(update, context, draft)
        
    except Exception as e:
        logger.error(f"Error updating time: {e}")
        await update.message.reply_text(
            "Sorry, couldn't understand that time window. Please try again:",
            reply_markup=get_main_menu_keyboard()
        )

async def save_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save preference to database."""
    try:
        draft = context.user_data.get("preference_draft")
        if not draft:
            await update.callback_query.edit_message_text("No preference to save.")
            return
        
        user_id = update.effective_user.id
        
        preference = Preference(
            location=Location(**draft["location"]),
            category=Category(**draft["category"]),
            price=Price(**draft["price"]),
            time_window=draft["time_window"]
        )
        
        mongo_client.add_user_preference(user_id, preference)
        
        # Clear context
        context.user_data.pop("preference_draft", None)
        context.user_data.pop("awaiting_input", None)
        
        await update.callback_query.edit_message_text(MSG_PREFERENCE_SAVED)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="What would you like to do next?",
            reply_markup=get_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error saving preference: {e}")
        await update.callback_query.edit_message_text(
            "Error saving preference. Please try again."
        )

async def show_user_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all user preferences."""
    user_id = update.effective_user.id
    user_prefs = mongo_client.get_user_preferences(user_id)
    
    if not user_prefs or not user_prefs.preferences:
        await update.message.reply_text(MSG_NO_PREFERENCES)
        return
    
    prefs_text = "Your saved preferences:\n\n"
    for i, pref in enumerate(user_prefs.preferences, 1):
        location_text = format_location(pref.location)
        category_text = format_category(pref.category)
        price_text = format_price(pref.price)
        prefs_text += f"{i}. {location_text} | {category_text} | {price_text}\n"
    
    await update.message.reply_text(prefs_text)

async def remove_user_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove all user preferences."""
    user_id = update.effective_user.id
    
    if mongo_client.delete_all_user_preferences(user_id):
        await update.message.reply_text(MSG_PREFERENCES_REMOVED)
    else:
        await update.message.reply_text(MSG_NO_PREFERENCES_TO_REMOVE)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    context.user_data.pop("preference_draft", None)
    context.user_data.pop("awaiting_input", None)
    
    await update.message.reply_text(
        "Operation cancelled. What would you like to do?",
        reply_markup=get_main_menu_keyboard()
    )
    return MAIN_MENU
