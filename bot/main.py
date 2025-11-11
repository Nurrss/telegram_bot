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
from ai.factory import create_ai
from data.storage import Storage
from utils.style_detector import StyleDetector
from bot.onboarding import onboarding_router
from core.task_manager import TaskManager
from bot.scheduler import ReminderScheduler

# Load environment variables
load_dotenv()

# Initialize AI and storage
ai_instance = None
storage = Storage()
style_detector = StyleDetector()
task_manager = TaskManager(storage)
reminder_scheduler = None


async def start_command(message: Message) -> None:
    """
    Handle /start command.
    Sends welcome message to new users.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "User"

    logger.info(f"User {user_id} (@{username}) started the bot")

    # Save initial user data
    user_data = {
        'user_id': user_id,
        'username': username,
        'started_at': message.date.isoformat() if message.date else None
    }
    storage.save_user_data(user_id, user_data)

    await message.reply(
        "Привет! 👋 Я - AI планировщик, который поможет тебе создать персональный 5-летний план развития.\n\n"
        "Команды:\n"
        "/start - Начать работу\n"
        "/onboarding - Создать профиль\n"
        "/profile - Посмотреть профиль\n"
        "/plan - Создать 5-летний план\n"
        "/tasks - Задачи на сегодня\n"
        "/done <номер> - Отметить задачу\n"
        "/progress - Твоя статистика\n"
        "/weekly - Сводка за неделю\n"
        "/ask <вопрос> - Задать вопрос AI\n\n"
        "Начни с /onboarding чтобы создать свой профиль!"
    )


async def ask_command(message: Message) -> None:
    """
    Handle /ask command.
    Allows users to ask questions to the AI.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "User"

    # Extract question from command
    command_text = message.text or ""
    if " " in command_text:
        question = command_text.split(" ", 1)[1]
    else:
        await message.reply("Использование: /ask <ваш вопрос>\nПример: /ask помоги с планом")
        return

    logger.info(f"User {user_id} (@{username}) asked: {question}")

    # Detect user style
    style = style_detector.analyze_style(question)

    # Load user data to update style preferences
    user_data = storage.load_user_data(user_id)
    if user_data:
        user_data['last_style'] = style
        storage.save_user_data(user_id, user_data)

    # Send "typing" action
    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        # Generate AI response
        response = await ai_instance.generate_response(question, user_id, style)
        await message.reply(response)
        logger.info(f"AI responded to user {user_id} with style: {style}")
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        await message.reply("Извините, произошла ошибка. Попробуйте ещё раз.")


async def plan_command(message: Message) -> None:
    """
    Generate or view user's 5-year plan.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "User"

    logger.info(f"User {user_id} (@{username}) requested plan generation")

    # Load user profile
    user_data = storage.load_user_data(user_id)

    if not user_data or not user_data.get('onboarding_completed'):
        await message.reply(
            "Пожалуйста, сначала создай профиль с помощью /onboarding\n\n"
            "Алдымен /onboarding арқылы профиль жаса"
        )
        return

    # Check if plan already exists
    if user_data.get('plan'):
        await message.reply(
            "У тебя уже есть план! Хочешь создать новый?\n"
            "Напиши 'да' для создания нового плана или /viewplan чтобы посмотреть текущий"
        )
        # TODO: Add state to wait for confirmation
        return

    await message.reply("Создаю твой персональный 5-летний план... ⏳")

    # Send "typing" action
    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        # Get user's communication style
        style = user_data.get('communication_style', {})

        # Generate plan using AI
        plan = await ai_instance.generate_plan(user_data, style)

        # Save plan to storage
        user_data['plan'] = plan
        user_data['plan_created_at'] = plan.get('created_at')
        storage.save_user_data(user_id, user_data)

        # Format and send plan
        plan_text = format_plan(plan, style)
        await message.reply(plan_text)

        logger.info(f"Plan generated and saved for user {user_id}")

    except Exception as e:
        logger.error(f"Error generating plan: {e}")
        await message.reply(
            "Произошла ошибка при создании плана 😔\n"
            "Попробуй ещё раз позже."
        )


def format_plan(plan: dict, style: dict = None) -> str:
    """
    Format plan data into readable message.

    Args:
        plan: Plan dictionary with years data
        style: User's communication style

    Returns:
        Formatted plan text
    """
    if not style:
        style = {}

    language = style.get('language', 'russian')
    emoji_usage = style.get('emoji_usage', 'low')

    # Header
    if language == 'kazakh':
        if emoji_usage == 'high':
            header = "🎯 Сіздің 5 жылдық жоспарыңыз дайын! ✨\n\n"
        else:
            header = "Сіздің 5 жылдық жоспарыңыз:\n\n"
    else:
        if emoji_usage == 'high':
            header = "🎯 Твой 5-летний план готов! ✨\n\n"
        else:
            header = "Твой 5-летний план:\n\n"

    # Build plan text
    plan_lines = [header]

    years = plan.get('years', [])
    for year_data in years:
        year = year_data.get('year')
        title = year_data.get('title', f'Год {year}')
        description = year_data.get('description', '')

        # Year header
        plan_lines.append(f"📅 Год {year}: {title}")
        plan_lines.append(f"   {description}\n")

        # Milestones
        milestones = year_data.get('milestones', [])
        if milestones:
            for milestone in milestones[:3]:  # Show first 3 milestones
                plan_lines.append(f"   ✓ {milestone}")
        plan_lines.append("")

    # Footer
    if language == 'kazakh':
        footer = (
            "\n💡 Күнделікті тапсырмаларды алу үшін /tasks пайдаланыңыз\n"
            "📊 Прогресті қарау үшін /progress пайдаланыңыз"
        )
    else:
        footer = (
            "\n💡 Используй /tasks для получения ежедневных задач\n"
            "📊 Используй /progress для просмотра прогресса"
        )

    plan_lines.append(footer)

    return "\n".join(plan_lines)


async def tasks_command(message: Message) -> None:
    """
    Show today's tasks for the user.
    """
    user_id = message.from_user.id

    logger.info(f"User {user_id} requested today's tasks")

    # Get tasks
    tasks_data = await task_manager.get_daily_tasks(user_id, ai_instance)

    if not tasks_data['success']:
        if tasks_data.get('error') == 'no_plan':
            await message.reply(
                "Сначала создай план с помощью /plan\n\n"
                "Алдымен /plan арқылы жоспар жаса"
            )
        else:
            await message.reply("Произошла ошибка при загрузке задач.")
        return

    # Format tasks message
    day_number = tasks_data['day_number']
    year = tasks_data['year']
    tasks = tasks_data['tasks']
    completed = tasks_data['completed_count']
    total = tasks_data['total_tasks']

    # Build message
    header = f"📋 Задачи на сегодня (День {day_number}, Год {year})\n\n"

    task_lines = []
    for task in tasks:
        if task['completed']:
            task_lines.append(f"✅ {task['number']}. {task['text']}")
        else:
            task_lines.append(f"⬜ {task['number']}. {task['text']}")

    footer = f"\n\nВыполнено: {completed}/{total}"
    footer += "\n\n💡 Используй /done <номер> чтобы отметить задачу"

    message_text = header + "\n".join(task_lines) + footer

    await message.reply(message_text)


async def done_command(message: Message) -> None:
    """
    Mark a task as complete.
    Usage: /done 1
    """
    user_id = message.from_user.id
    command_text = message.text or ""

    # Extract task number
    parts = command_text.split()
    if len(parts) < 2:
        await message.reply(
            "Использование: /done <номер>\n"
            "Пример: /done 1"
        )
        return

    try:
        task_number = int(parts[1])
    except ValueError:
        await message.reply("Номер задачи должен быть числом.\nПример: /done 1")
        return

    logger.info(f"User {user_id} marking task {task_number} as complete")

    # Mark task complete
    result = task_manager.mark_task_complete(user_id, task_number)

    if not result['success']:
        await message.reply("Не удалось отметить задачу. Попробуй ещё раз.")
        return

    # Success message
    await message.reply(
        f"✅ Задача {task_number} выполнена!\n\n"
        f"Отличная работа! Используй /tasks чтобы посмотреть оставшиеся задачи."
    )

    # Check for streak milestones
    stats = task_manager.get_progress_stats(user_id)
    streak = stats.get('current_streak', 0)

    if streak in [7, 14, 30, 50, 100, 365]:
        user_data = storage.load_user_data(user_id)
        name = user_data.get('name', 'User')
        style = user_data.get('communication_style', {})

        from core.reminders import ReminderGenerator
        reminder_gen = ReminderGenerator()
        milestone_msg = reminder_gen.generate_streak_milestone(name, style, streak)

        if milestone_msg:
            await message.reply(milestone_msg)


async def progress_command(message: Message) -> None:
    """
    Show user's progress statistics.
    """
    user_id = message.from_user.id

    logger.info(f"User {user_id} requested progress stats")

    # Get stats
    stats = task_manager.get_progress_stats(user_id)

    if not stats['success']:
        await message.reply(
            "Сначала создай план с помощью /plan\n\n"
            "Алдымен /plan арқылы жоспар жаса"
        )
        return

    # Format stats message
    total_completed = stats['total_tasks_completed']
    days_active = stats['days_active']
    streak = stats['current_streak']
    day_number = stats['day_number']
    progress_pct = stats['progress_percentage']
    completion_rate = stats['recent_completion_rate']

    message_text = (
        f"📊 Твоя статистика\n\n"
        f"🎯 Выполнено задач: {total_completed}\n"
        f"📅 Активных дней: {days_active}\n"
        f"🔥 Текущая серия: {streak} дней\n"
        f"📈 Прогресс плана: {day_number}/1825 дней ({progress_pct:.1f}%)\n"
        f"✅ Выполнение (7 дней): {completion_rate:.0f}%\n\n"
        f"💪 Продолжай в том же духе!"
    )

    await message.reply(message_text)


async def weekly_command(message: Message) -> None:
    """
    Show 7-day weekly summary.
    """
    user_id = message.from_user.id

    logger.info(f"User {user_id} requested weekly summary")

    # Get weekly summary
    summary_data = task_manager.get_weekly_summary(user_id)

    if not summary_data['success']:
        await message.reply(
            "Сначала создай план с помощью /plan\n\n"
            "Алдымен /plan арқылы жоспар жаса"
        )
        return

    # Format summary
    summary = summary_data['summary']

    header = "📅 Сводка за неделю\n\n"

    lines = []
    for day in summary:
        date = day['date']
        weekday = day['weekday'][:3]  # First 3 letters
        completed = day['completed_tasks']
        total = day['total_tasks']
        rate = day['completion_rate']

        if total == 0:
            lines.append(f"⚪ {weekday} {date}: нет задач")
        elif rate == 100:
            lines.append(f"✅ {weekday} {date}: {completed}/{total} (100%)")
        elif rate >= 50:
            lines.append(f"🟡 {weekday} {date}: {completed}/{total} ({rate:.0f}%)")
        else:
            lines.append(f"⚫ {weekday} {date}: {completed}/{total} ({rate:.0f}%)")

    footer = "\n\n💡 Используй /tasks для сегодняшних задач"

    message_text = header + "\n".join(lines) + footer

    await message.reply(message_text)


async def handle_message(message: Message) -> None:
    """
    Handle regular text messages.
    Detects style and responds using AI.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    text = message.text or ""

    logger.info(f"User {user_id} (@{username}) sent message: {text}")

    # Detect user style
    style = style_detector.analyze_style(text)

    # Load and update user data with style
    user_data = storage.load_user_data(user_id) or {'user_id': user_id, 'username': username}
    user_data['last_style'] = style
    storage.save_user_data(user_id, user_data)

    # Send "typing" action
    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        # Generate AI response
        response = await ai_instance.generate_response(text, user_id, style)
        await message.reply(response)
        logger.info(f"AI responded to user {user_id} with style: {style}")
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        await message.reply("Извините, произошла ошибка. Попробуйте ещё раз.")


async def main() -> None:
    """
    Main function to initialize and run the bot.
    Loads configuration, registers handlers, and starts polling.
    """
    global ai_instance, reminder_scheduler

    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        raise ValueError("TELEGRAM_BOT_TOKEN is required")

    logger.info("Initializing bot...")

    # Initialize AI
    ai_instance = create_ai()

    # Initialize bot and dispatcher
    bot = Bot(token=bot_token)
    dp = Dispatcher()

    # Initialize and start reminder scheduler
    reminder_scheduler = ReminderScheduler(bot, storage, ai_instance, task_manager)
    reminder_scheduler.start()

    # Include routers (onboarding must be first for FSM priority)
    dp.include_router(onboarding_router)

    # Register handlers
    dp.message.register(start_command, Command("start"))
    dp.message.register(ask_command, Command("ask"))
    dp.message.register(plan_command, Command("plan"))
    dp.message.register(tasks_command, Command("tasks"))
    dp.message.register(done_command, Command("done"))
    dp.message.register(progress_command, Command("progress"))
    dp.message.register(weekly_command, Command("weekly"))
    dp.message.register(handle_message)  # Handle all other messages

    logger.info("Bot is running. Press Ctrl+C to stop.")

    try:
        # Start polling
        await dp.start_polling(bot)
    finally:
        # Stop scheduler
        if reminder_scheduler:
            reminder_scheduler.stop()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
