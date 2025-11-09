"""Configuration management for the bot."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Bot configuration class."""

    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')

        if not self.telegram_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN not found in environment variables. "
                "Please create a .env file with your bot token."
            )

    @property
    def token(self) -> str:
        """Get the Telegram bot token."""
        return self.telegram_token


# Create a singleton config instance
config = Config()
