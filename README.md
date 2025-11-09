# AI Planner Telegram Bot

A Telegram bot integrated with AI (Claude) that helps users build and manage personalized 5-year life roadmaps for education, work, and personal growth.

## Description

This bot provides:
- AI-powered personalized planning
- 5-year roadmap generation (year → month → week → day)
- Daily task delivery and reminders
- Progress tracking and adaptive planning
- User goal collection and analysis

## Project Structure

```
telegram_bot/
├── bot/                 # Telegram bot interaction (aiogram)
│   ├── __init__.py
│   └── main.py         # Entry point for the bot
│
├── ai/                 # AI integration (Claude)
│   ├── __init__.py
│   └── interface.py    # AI model interface
│
├── core/               # Planning and task management
│   ├── __init__.py
│   └── planner.py      # Plan generation and management
│
├── data/               # Data storage
│   ├── __init__.py
│   └── storage.py      # User data persistence
│
├── utils/              # Helper functions
│   ├── __init__.py
│   └── logger.py       # Logging configuration
│
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

## Setup

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd telegram_bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Edit `.env` and add your bot token:
```
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
```

### Getting a Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token provided by BotFather
5. Add it to your `.env` file

## Running the Bot

```bash
python -m bot.main
```

The bot will start polling for updates. Press Ctrl+C to stop.

## Usage

1. Find your bot on Telegram
2. Start a chat with `/start`
3. The bot will respond: "Hello, I'm your AI planner bot!"

## Current Features

- `/start` - Initialize conversation with the bot

## Planned Features

- User onboarding and goal collection
- AI-powered 5-year plan generation
- Daily task breakdown and delivery
- Progress tracking and analytics
- Plan adaptation based on progress

## Architecture

The project follows a modular architecture:

- **bot/**: Handles all Telegram interactions using aiogram library
- **ai/**: Interface for AI model integration (Claude or similar)
- **core/**: Business logic for planning and task management
- **data/**: Data persistence and storage management
- **utils/**: Shared utilities like logging and configuration

## Development

The project is in early stages. AI integration and planning features will be added in future iterations.

## License

MIT License
