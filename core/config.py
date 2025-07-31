"""Configuration settings for the application."""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # Bot configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Database configuration
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    
    # LLM configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = "gemini-1.5-flash"
    GEMINI_TEMPERATURE = 0.1
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        required_vars = [
            ("BOT_TOKEN", cls.BOT_TOKEN),
            ("MONGO_URI", cls.MONGO_URI), 
            ("MONGO_DB_NAME", cls.MONGO_DB_NAME),
            ("GOOGLE_API_KEY", cls.GOOGLE_API_KEY)
        ]
        
        missing = [name for name, value in required_vars if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

config = Config()
