"""Constants for the application."""

# Bot states
MAIN_MENU = "main_menu"

# Time windows (in seconds)
TIME_ONE_DAY = 86400
TIME_TWO_DAYS = 172800
TIME_THREE_DAYS = 259200
TIME_ONE_WEEK = 604800
TIME_TWO_WEEKS = 1209600
TIME_ONE_MONTH = 2592000

# Default values
DEFAULT_TIME_WINDOW = TIME_ONE_WEEK
DEFAULT_PRICE_FROM = 0
DEFAULT_PRICE_TO = 0

# Data file paths
DATA_DIR = "data"
CATEGORIES_FILE = "categories.json"
CATEGORY_ID_FILE = "category_id.json"
CITIES_FILE = "cities.json"
LOCATION_ID_FILE = "location_id.json"
ZIPCODES_FILE = "zipcodes.json"

# Menu options
MENU_ADD_PREFERENCE = "Add Preference"
MENU_VIEW_PREFERENCES = "View Preferences"
MENU_REMOVE_PREFERENCE = "Remove Preference"

# Graph actions
ACTION_START = "start"
ACTION_EXTRACT = "extract"
ACTION_LOCATION = "location"
ACTION_CONFIRM = "confirm"
ACTION_REFINE = "refine"
ACTION_END = "end"

# Messages
MSG_WELCOME = "Welcome! I can help you save preferences for Kleinanzeigen searches."
MSG_HELP = "Use the menu to add, view, or remove your preferences."
MSG_CANCELLED = "Operation cancelled. What would you like to do?"
MSG_NO_PREFERENCES = "You don't have any saved preferences yet."
MSG_PREFERENCES_REMOVED = "All preferences removed successfully!"
MSG_NO_PREFERENCES_TO_REMOVE = "No preferences found to remove."
MSG_ERROR_GENERIC = "Sorry, there was an error processing your request. Please try again."
MSG_INVALID_SELECTION = "Please select an option from the menu:"
