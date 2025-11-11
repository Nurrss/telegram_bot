"""
Scheduler Module
Handles scheduled reminders using APScheduler.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from datetime import datetime

from utils.logger import logger
from data.storage import Storage
from core.reminders import ReminderGenerator
from core.task_manager import TaskManager


class ReminderScheduler:
    """
    Manages scheduled reminders for users.
    Sends personalized reminders at specific times.
    """

    def __init__(self, bot: Bot, storage: Storage, ai_instance, task_manager: TaskManager):
        """
        Initialize ReminderScheduler.

        Args:
            bot: Telegram Bot instance
            storage: Storage instance
            ai_instance: AI instance for task generation
            task_manager: TaskManager instance
        """
        self.bot = bot
        self.storage = storage
        self.ai_instance = ai_instance
        self.task_manager = task_manager
        self.reminder_generator = ReminderGenerator()
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Start the scheduler with all reminder jobs."""
        logger.info("Starting reminder scheduler...")

        # Morning reminder: 7:00 AM
        self.scheduler.add_job(
            self.send_morning_reminders,
            trigger=CronTrigger(hour=7, minute=0),
            id='morning_reminder',
            name='Morning Reminder (7 AM)',
            replace_existing=True
        )

        # Afternoon check: 2:00 PM
        self.scheduler.add_job(
            self.send_afternoon_reminders,
            trigger=CronTrigger(hour=14, minute=0),
            id='afternoon_reminder',
            name='Afternoon Reminder (2 PM)',
            replace_existing=True
        )

        # Evening summary: 6:00 PM
        self.scheduler.add_job(
            self.send_evening_reminders,
            trigger=CronTrigger(hour=18, minute=0),
            id='evening_reminder',
            name='Evening Reminder (6 PM)',
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("Reminder scheduler started successfully")

    def stop(self):
        """Stop the scheduler."""
        logger.info("Stopping reminder scheduler...")
        self.scheduler.shutdown()
        logger.info("Reminder scheduler stopped")

    async def send_morning_reminders(self):
        """Send morning reminders to all users with plans."""
        logger.info("Sending morning reminders...")

        # Get all users with plans
        users = self._get_users_with_plans()

        for user_id in users:
            try:
                user_data = self.storage.load_user_data(user_id)

                if not user_data or not user_data.get('plan'):
                    continue

                # Check if reminders are enabled (default: true)
                if not user_data.get('reminders_enabled', True):
                    continue

                # Get user info
                name = user_data.get('name', 'User')
                style = user_data.get('communication_style', {})

                # Get streak
                stats = self.task_manager.get_progress_stats(user_id)
                streak = stats.get('current_streak', 0)

                # Generate reminder
                reminder = self.reminder_generator.generate_morning_reminder(
                    name, style, streak
                )

                # Send message
                await self.bot.send_message(chat_id=user_id, text=reminder)
                logger.info(f"Morning reminder sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending morning reminder to user {user_id}: {e}")

    async def send_afternoon_reminders(self):
        """Send afternoon check-in reminders."""
        logger.info("Sending afternoon reminders...")

        users = self._get_users_with_plans()

        for user_id in users:
            try:
                user_data = self.storage.load_user_data(user_id)

                if not user_data or not user_data.get('plan'):
                    continue

                if not user_data.get('reminders_enabled', True):
                    continue

                # Get user info
                name = user_data.get('name', 'User')
                style = user_data.get('communication_style', {})

                # Get today's task progress
                tasks_data = await self.task_manager.get_daily_tasks(user_id, self.ai_instance)

                if not tasks_data['success']:
                    continue

                completed = tasks_data['completed_count']
                total = tasks_data['total_tasks']

                # Generate reminder
                reminder = self.reminder_generator.generate_afternoon_reminder(
                    name, style, completed, total
                )

                # Send message
                await self.bot.send_message(chat_id=user_id, text=reminder)
                logger.info(f"Afternoon reminder sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending afternoon reminder to user {user_id}: {e}")

    async def send_evening_reminders(self):
        """Send evening summary reminders."""
        logger.info("Sending evening reminders...")

        users = self._get_users_with_plans()

        for user_id in users:
            try:
                user_data = self.storage.load_user_data(user_id)

                if not user_data or not user_data.get('plan'):
                    continue

                if not user_data.get('reminders_enabled', True):
                    continue

                # Get user info
                name = user_data.get('name', 'User')
                style = user_data.get('communication_style', {})

                # Get today's task progress
                tasks_data = await self.task_manager.get_daily_tasks(user_id, self.ai_instance)

                if not tasks_data['success']:
                    continue

                completed = tasks_data['completed_count']
                total = tasks_data['total_tasks']

                # Generate reminder
                reminder = self.reminder_generator.generate_evening_reminder(
                    name, style, completed, total
                )

                # Send message
                await self.bot.send_message(chat_id=user_id, text=reminder)
                logger.info(f"Evening reminder sent to user {user_id}")

                # Check for streak milestones
                stats = self.task_manager.get_progress_stats(user_id)
                streak = stats.get('current_streak', 0)

                if streak in [7, 14, 30, 50, 100, 365]:
                    milestone_msg = self.reminder_generator.generate_streak_milestone(
                        name, style, streak
                    )
                    if milestone_msg:
                        await self.bot.send_message(chat_id=user_id, text=milestone_msg)
                        logger.info(f"Streak milestone message sent to user {user_id} for {streak} days")

            except Exception as e:
                logger.error(f"Error sending evening reminder to user {user_id}: {e}")

    def _get_users_with_plans(self) -> list:
        """
        Get list of user IDs who have plans.

        Returns:
            List of user IDs
        """
        # Get all user data files from storage
        import os
        data_dir = self.storage.data_dir

        user_ids = []

        if not os.path.exists(data_dir):
            return user_ids

        for filename in os.listdir(data_dir):
            if filename.startswith('user_') and filename.endswith('.json'):
                try:
                    # Extract user ID from filename
                    user_id_str = filename.replace('user_', '').replace('.json', '')
                    user_id = int(user_id_str)

                    # Check if user has a plan
                    user_data = self.storage.load_user_data(user_id)
                    if user_data and user_data.get('plan'):
                        user_ids.append(user_id)

                except (ValueError, TypeError):
                    continue

        return user_ids
