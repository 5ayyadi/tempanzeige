# Tempanzeige - Kleinanzeigen Preference Bot

A Telegram bot for managing Kleinanzeigen search preferences with AI-powered natural language processing.

## Project Structure

```
├── bot/              # Telegram bot logic
│   ├── bot.py        # Bot application setup
│   ├── handlers.py   # Conversation handlers
│   └── keyboards.py  # Keyboard layouts
├── core/             # Core business logic
│   ├── mongo_client.py     # Database operations
│   └── preference_graph.py # LangGraph workflow
├── llm/              # LLM integration
│   ├── gemini_client.py    # Gemini API client
│   ├── nodes.py           # Graph nodes
│   ├── states.py          # State models
│   └── formatters.py      # Data formatting
├── models/           # Pydantic models
│   ├── preferences.py     # Preference models
│   └── user.py           # User models
├── prompts/          # AI prompts
│   └── prompts.py        # Prompt templates
├── utils/            # Helper functions
│   ├── helpers.py        # Utility functions
│   └── user_prefrences_manager.py  # Legacy preference manager
├── data/             # Static data files
│   ├── categories.json   # Category mappings
│   ├── cities.json      # City data
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
