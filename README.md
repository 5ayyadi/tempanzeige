# Tempanzeige - Kleinanzeigen Preference Bot

A Telegram bot for managing Kleinanzeigen search preferences with AI-powered natural language processing.

## Project Structure

```
├── bot/              # Telegram bot logic
│   ├── bot.py        # Bot application setup
│   ├── handlers.py   # Conversation handlers
│   └── keyboards.py  # Keyboard layouts
├── core/             # Core business logic
│   ├── config.py     # Configuration settings
│   ├── constants.py  # Application constants
│   ├── mongo_client.py     # Database operations
│   └── preference_graph.py # LangGraph workflow
├── llm/              # LLM integration
│   ├── gemini_client.py    # Gemini API client
│   ├── nodes.py           # Graph nodes
│   ├── states.py          # State models
│   └── formatters.py      # Data formatting
├── models/           # Pydantic models
│   ├── offer.py          # Offer models
│   ├── preferences.py    # Preference models
│   └── user.py          # User models
├── runners/          # Background tasks
│   ├── offers_scraper.py # Scrapes offers from sites
│   └── message_sender.py # Sends offers to users
├── scraper/          # Web scraping logic
│   ├── scraper.py        # Main scraper
│   ├── parse_data.py     # Data parsing
│   └── object_creator.py # Object creation
├── prompts/          # AI prompts
│   └── prompts.py        # Prompt templates
├── utils/            # Helper functions
│   ├── helpers.py        # Utility functions
│   └── user_prefrences_manager.py  # Legacy preference manager
├── data/             # Static data files
│   ├── categories.json   # Category mappings
│   ├── cities.json      # City data
│   └── zipcodes.json    # Zipcode mappings
└── main.py           # Application entry point
```

## Usage

### Starting the Application

The main.py file supports different modes:

```bash
# Start the Telegram bot (default)
python main.py
python main.py bot

# Run the offers scraper
python main.py scraper

# Run the message sender
python main.py sender
```

### Message Format

The bot sends offers to users with enhanced Telegram formatting:

```
[Picture here]
**Vier Posterstühle Holz**

**Insgesamt 4 Stück. Am liebsten gemeinsam abzugeben.
Abzuholen in Mainz-Laubenheim. Wir verschenken...**

📍 55130 Mainz
📅 2025, Jul 19

🔗 [Mehr Details](https://www.kleinanzeigen.de/s-anzeige/vier-posterstuehle-holz/3139262451-86-5316)
```

**Formatting Features:**
- **Bold titles and descriptions** for better readability
- **Clickable links** for direct access to offers
- **Clean emoji indicators** for location, date, and links
- **Monospace formatting** for preferences display
- **Underlined text** for emphasis where needed

### Features

- **Smart Offer Tracking**: Prevents sending duplicate offers to users
- **Natural Language Processing**: Uses Gemini AI to understand user preferences
- **Flexible Preferences**: Support for location, category, price, and time filters
- **Background Processing**: Separate runners for scraping and message sending
│   └── ...
├── handlers/         # Additional handlers (placeholder)
├── scraper/          # Scraping functionality (placeholder)
├── config.py         # Configuration settings
├── constants.py      # Application constants
└── main.py          # Application entry point
```

## Setup

1. Install dependencies:
   ```bash
   make install
   ```

2. Set up environment variables in `.env`:
   ```
   BOT_TOKEN=your_telegram_bot_token
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB_NAME=tempanzeige
   GOOGLE_API_KEY=your_gemini_api_key
   ```

3. Start development database:
   ```bash
   make dev
   ```

4. Run the bot:
   ```bash
   make run
   ```

## Development

- `make dev` - Start development environment with database
- `make dev-stop` - Stop development environment  
- `make run` - Run the bot application
- `make test` - Run tests
- `make clean` - Clean up Docker containers
- `make logs` - Show database logs

## Features

- Natural language preference extraction using Gemini AI
- MongoDB integration for preference storage
- LangGraph workflow for conversation management
- Multi-language support (German/English)
- Telegram bot interface with custom keyboards
