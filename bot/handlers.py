"""Conversation handlers for the Telegram bot with LangGraph integration."""

import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from constants import (
    MAIN_MENU, MENU_ADD_PREFERENCE, MENU_VIEW_PREFERENCES, 
    MENU_REMOVE_PREFERENCE, MSG_WELCOME, MSG_HELP, MSG_CANCELLED,
    MSG_NO_PREFERENCES, MSG_PREFERENCES_REMOVED, MSG_NO_PREFERENCES_TO_REMOVE,
    MSG_ERROR_GENERIC, MSG_INVALID_SELECTION
)
from core.mongo_client import MongoClientManager
from core.preference_graph import create_preference_graph
from llm.states import PreferenceState
from llm.nodes import confirm_preference_node
from llm.formatters import format_location, format_category, format_price
from bot.keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)

mongo_client = MongoClientManager()
preference_graph = create_preference_graph()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the /start command is issued."""
    await update.message.reply_text(
        f"{MSG_WELCOME}\n{MSG_HELP}",
        reply_markup=get_main_menu_keyboard()
    )
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu selection."""
    text = update.message.text
    
    if text == MENU_ADD_PREFERENCE:
        await update.message.reply_text(
            "Tell me what you're looking for! You can describe it naturally in German or English.\n\n"
            "Examples:\n"
            "• 'Ich suche einen Schreibtischstuhl in Koeln, max 30 EUR'\n"
            "• 'Sofa in Berlin, bis 100 EUR, letzte Woche'\n"
            "• 'Auto parts in Munich under 50 EUR'",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Initialize LangGraph state
        initial_state = PreferenceState(
            user_input="",
            user_id=update.effective_user.id,
            next_action="extract"
        )
        context.user_data["graph_state"] = initial_state.model_dump()
        context.user_data["in_preference_flow"] = True
        
        return MAIN_MENU
    
    elif text == MENU_VIEW_PREFERENCES:
        await show_user_preferences(update, context)
        return MAIN_MENU
    
    elif text == MENU_REMOVE_PREFERENCE:
        await remove_user_preferences(update, context)
        return MAIN_MENU
    
    # Handle preference flow messages
    elif context.user_data.get("in_preference_flow"):
        await handle_preference_flow(update, context)
        return MAIN_MENU
    
    else:
        await update.message.reply_text(
            MSG_INVALID_SELECTION,
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU

async def handle_preference_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages within the preference extraction flow."""
    user_input = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Handling preference flow for user {user_id}: {user_input}")
    
    # Get current graph state from context
    graph_state_dict = context.user_data.get("graph_state", {})
    
    # Update state with new user input
    graph_state_dict["user_input"] = user_input
    current_state = PreferenceState(**graph_state_dict)
    
    # Handle each phase manually without using graph.invoke
    try:
        logger.info(f"Processing state: next_action={current_state.next_action}, user_input='{user_input}'")
        
        if current_state.next_action == "extract":
            # Run extract node directly
            from llm.nodes import extract_preference_node
            result = extract_preference_node(current_state)
        elif current_state.next_action == "location":
            # Run location node directly
            from llm.nodes import location_node
            result = location_node(current_state)
        elif current_state.next_action == "refine":
            # Run refine node directly
            from llm.nodes import refine_node
            result = refine_node(current_state)
        elif current_state.next_action == "confirm":
            # Run confirm node directly
            result = confirm_preference_node(current_state)
        else:
            # Default case - should not happen
            result = current_state
            result.is_complete = True
            result.message = "Something went wrong. Please start over."
        
        # Update context with new state
        context.user_data["graph_state"] = result.model_dump()
        
        # Send response to user
        await update.message.reply_text(result.message)
        logger.info(f"Phase completed: next_action={result.next_action}, is_complete={result.is_complete}")
        
        # Check if flow is complete
        if result.is_complete:
            context.user_data.pop("graph_state", None)
            context.user_data.pop("in_preference_flow", None)
            
            await update.message.reply_text(
                "What would you like to do next?",
                reply_markup=get_main_menu_keyboard()
            )
    
    except Exception as e:
        logger.error(f"Error in preference flow: {e}")
        await update.message.reply_text(
            MSG_ERROR_GENERIC,
            reply_markup=get_main_menu_keyboard()
        )
        
        # Clean up context on error
        context.user_data.pop("graph_state", None)
        context.user_data.pop("in_preference_flow", None)

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
    context.user_data.pop("graph_state", None)
    context.user_data.pop("in_preference_flow", None)
    
    await update.message.reply_text(
        MSG_CANCELLED,
        reply_markup=get_main_menu_keyboard()
    )
    return MAIN_MENU
