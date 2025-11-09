# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Telegram echo bot built with python-telegram-bot library (v20.7). The bot echoes back any text message sent to it and includes basic command handling for `/start` and `/help`.

## Development Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Then edit .env with actual TELEGRAM_BOT_TOKEN
```

### Running the Bot
```bash
# Run the bot
python -m bot.main

# Run with specific Python version
python3 -m bot.main
```

### Testing
```bash
# Currently no automated tests
# Manual testing: Run bot and interact via Telegram
```

## Architecture

### Core Modules

**bot/config.py** - Configuration Management
- Loads environment variables using python-dotenv
- Exports singleton `config` instance with bot token
- Validates that TELEGRAM_BOT_TOKEN is present

**bot/handlers.py** - Handler Functions
- `start_command()` - Handles `/start` command with welcome message
- `help_command()` - Handles `/help` command
- `echo_message()` - Main echo functionality for text messages
- `error_handler()` - Logs errors from bot operations
- All handlers are async functions compatible with python-telegram-bot v20+

**bot/main.py** - Application Entry Point
- Initializes the `Application` with bot token from config
- Registers all handlers (CommandHandler and MessageHandler)
- Runs polling loop to receive updates from Telegram

### Data Flow

1. Telegram sends update → Application receives via polling
2. Application routes to appropriate handler based on update type
3. Handler processes update and sends response back to Telegram
4. All interactions are logged via Python logging module

### Handler Registration Pattern

Handlers are registered in `bot/main.py` using:
- `CommandHandler(command_name, handler_function)` for commands
- `MessageHandler(filters, handler_function)` for messages
- Filters like `filters.TEXT & ~filters.COMMAND` ensure message handlers don't intercept commands

## Extending the Bot

### Adding New Commands

1. Define async handler in `bot/handlers.py`:
```python
async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Response text")
    logger.info(f"User {update.effective_user.id} used /mycommand")
```

2. Register in `bot/main.py`:
```python
application.add_handler(CommandHandler("mycommand", my_command))
```

### Adding Message Filters

To handle specific message types (photos, documents, etc.):
```python
# In handlers.py
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Handle photo
    pass

# In main.py
application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
```

### Adding State/Context

For conversation flows, use ConversationHandler from telegram.ext. This requires importing and configuring states, which is not currently implemented but is a common extension pattern.

## Configuration

All configuration is environment-based via `.env` file:
- `TELEGRAM_BOT_TOKEN` - Required. Bot token from @BotFather

The bot uses python-dotenv to load these variables. Never commit the `.env` file.

## Logging

Logging is configured in both `bot/handlers.py` and `bot/main.py`:
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Level: INFO
- Logs user interactions, commands used, and errors

## Dependencies

- `python-telegram-bot==20.7` - Official Telegram Bot API wrapper
- `python-dotenv==1.0.0` - Environment variable management

Version 20.7 of python-telegram-bot uses async/await pattern (differs from older synchronous versions).
