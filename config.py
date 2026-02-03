"""
SignalForge Configuration Module
Centralized configuration management
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # Database
    DB_URL = os.getenv("DATABASE_URL", "sqlite:///signalforge.db")
    
    # Telegram
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Scoring
    ALERT_THRESHOLD = int(os.getenv("ALERT_THRESHOLD", "70"))
    
    # Rules
    MAX_AGE_DAYS = int(os.getenv("MAX_AGE_DAYS", "7"))
    
    # Scheduler
    COLLECTOR_INTERVAL_MINUTES = int(os.getenv("COLLECTOR_INTERVAL_MINUTES", "60"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "signalforge.log")
    
    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Features
    ENABLE_ALERTS = os.getenv("ENABLE_ALERTS", "false").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if cls.ENABLE_ALERTS and not cls.TELEGRAM_TOKEN:
            errors.append("TELEGRAM_TOKEN is required when alerts are enabled (set ENABLE_ALERTS=false to disable)")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True


# Export singleton instance
config = Config()
