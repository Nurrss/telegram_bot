"""
Main entry point for the Telegram bot.
Using aiogram library for Telegram Bot API interaction.
"""

import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from utils.logger import logger

# Load environment variables
load_dotenv()


async def start_command(message: Message) -> None:
    """
    Handle /start command.
    Sends welcome message to new users.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "User"

    logger.info(f"User {user_id} (@{username}) started the bot")

    await message.reply("Hello, I'm your AI planner bot!")


async def main() -> None:
    """
    Main function to initialize and run the bot.
    Loads configuration, registers handlers, and starts polling.
    """
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        raise ValueError("TELEGRAM_BOT_TOKEN is required")

    logger.info("Initializing bot...")

    # Initialize bot and dispatcher
    bot = Bot(token=bot_token)
    dp = Dispatcher()

    # Register handlers
    dp.message.register(start_command, Command("start"))

    logger.info("Bot is running. Press Ctrl+C to stop.")

    try:
        # Start polling
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
