# Project Context

## Goal

Create a Telegram bot integrated with an AI (Claude or similar) that builds
a personalized 5-year life roadmap (education, work, personal growth).

## Core Features

- Registration and onboarding via Telegram.
- Collection of user data and goals (via forms or test).
- AI-generated 5-year roadmap (year → month → week → day).
- Daily task delivery and reminders.
- Tracking progress and AI-driven adaptation.
- Analytics dashboard (Telegram Mini App optional).

## Architecture Outline
telegram_bot/
│
├── bot/ → Telegram interaction (aiogram / telebot)
├── ai/ → AI logic & Claude integration
├── core/ → Planning engine (tasks, progress, schedule)
├── data/ → Local DB or JSON files for now
└── utils/ → Helpers (logging, validation, etc.)


## Tech Stack
- Python 3.11+
- aiogram / telebot
- SQLite (or JSON for prototype)
- Claude API integration (local)
- Git automation

## Development Rules
- Commit frequently with atomic changes.
- Never push broken code.
- Claude will auto-push after success.
- Each feature must be tested minimally before commit.

## Milestones
1. Base bot structure & commands
2. AI integration interface
3. 5-year plan generator
4. Daily task manager
5. Progress tracking
6. Mini App UI (optional)
