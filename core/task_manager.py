"""
Task Manager Module
Handles daily task generation, completion tracking, and progress analytics.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from data.storage import Storage


class TaskManager:
    """
    Manages user tasks, completion tracking, and progress statistics.
    """

    def __init__(self, storage: Storage):
        """
        Initialize TaskManager.

        Args:
            storage: Storage instance for data persistence
        """
        self.storage = storage

    def get_current_day_number(self, plan_created_at: str) -> int:
        """
        Calculate current day number in the 5-year plan.

        Args:
            plan_created_at: ISO timestamp when plan was created

        Returns:
            Day number (1-1825)
        """
        created_date = datetime.fromisoformat(plan_created_at)
        current_date = datetime.now()
        delta = current_date - created_date
        day_number = delta.days + 1  # Day 1 is the first day

        # Cap at 1825 days (5 years)
        return min(max(1, day_number), 1825)

    async def get_daily_tasks(self, user_id: int, ai_instance) -> Dict:
        """
        Get today's tasks for a user.

        Args:
            user_id: Telegram user ID
            ai_instance: AI instance for task generation

        Returns:
            Dictionary with tasks and metadata
        """
        # Load user data
        user_data = self.storage.load_user_data(user_id)

        if not user_data or not user_data.get('plan'):
            return {
                'success': False,
                'error': 'no_plan',
                'message': 'Сначала создай план с помощью /plan'
            }

        # Get plan and calculate day number
        plan = user_data['plan']
        plan_created_at = user_data.get('plan_created_at')

        if not plan_created_at:
            # If no creation date, use current date as Day 1
            plan_created_at = datetime.now().isoformat()
            user_data['plan_created_at'] = plan_created_at
            self.storage.save_user_data(user_id, user_data)

        day_number = self.get_current_day_number(plan_created_at)
        year = min(5, (day_number - 1) // 365 + 1)

        # Generate tasks using AI
        tasks = await ai_instance.generate_daily_tasks(plan, day_number)

        # Get today's date string
        today = datetime.now().strftime('%Y-%m-%d')

        # Check if tasks already exist for today
        if 'daily_tasks' not in user_data:
            user_data['daily_tasks'] = {}

        # Create task entries with completion status
        task_entries = []
        for i, task_text in enumerate(tasks, 1):
            task_id = f"{today}_{i}"
            task_entries.append({
                'id': task_id,
                'number': i,
                'text': task_text,
                'completed': user_data['daily_tasks'].get(task_id, {}).get('completed', False),
                'completed_at': user_data['daily_tasks'].get(task_id, {}).get('completed_at')
            })

        return {
            'success': True,
            'day_number': day_number,
            'year': year,
            'date': today,
            'tasks': task_entries,
            'total_tasks': len(task_entries),
            'completed_count': sum(1 for t in task_entries if t['completed'])
        }

    def mark_task_complete(self, user_id: int, task_number: int) -> Dict:
        """
        Mark a task as complete.

        Args:
            user_id: Telegram user ID
            task_number: Task number (1-based index)

        Returns:
            Result dictionary
        """
        user_data = self.storage.load_user_data(user_id)

        if not user_data:
            return {'success': False, 'error': 'no_user'}

        today = datetime.now().strftime('%Y-%m-%d')
        task_id = f"{today}_{task_number}"

        # Initialize daily_tasks if not exists
        if 'daily_tasks' not in user_data:
            user_data['daily_tasks'] = {}

        # Mark as complete
        user_data['daily_tasks'][task_id] = {
            'completed': True,
            'completed_at': datetime.now().isoformat()
        }

        # Update streak
        self._update_streak(user_data)

        # Save
        self.storage.save_user_data(user_id, user_data)

        return {
            'success': True,
            'task_id': task_id,
            'task_number': task_number
        }

    def get_progress_stats(self, user_id: int) -> Dict:
        """
        Get user's progress statistics.

        Args:
            user_id: Telegram user ID

        Returns:
            Statistics dictionary
        """
        user_data = self.storage.load_user_data(user_id)

        if not user_data or not user_data.get('plan'):
            return {'success': False, 'error': 'no_plan'}

        daily_tasks = user_data.get('daily_tasks', {})

        # Calculate statistics
        total_tasks_completed = sum(1 for task in daily_tasks.values() if task.get('completed'))

        # Count unique days with completed tasks
        completed_days = set()
        for task_id, task_data in daily_tasks.items():
            if task_data.get('completed'):
                date = task_id.rsplit('_', 1)[0]  # Extract date from task_id
                completed_days.add(date)

        days_active = len(completed_days)

        # Calculate streak
        streak = self._calculate_streak(user_data)

        # Calculate completion rate for last 7 days
        recent_completion_rate = self._calculate_recent_completion_rate(user_data)

        # Plan progress
        plan_created_at = user_data.get('plan_created_at')
        if plan_created_at:
            day_number = self.get_current_day_number(plan_created_at)
            progress_percentage = (day_number / 1825) * 100
        else:
            day_number = 0
            progress_percentage = 0

        return {
            'success': True,
            'total_tasks_completed': total_tasks_completed,
            'days_active': days_active,
            'current_streak': streak,
            'day_number': day_number,
            'progress_percentage': progress_percentage,
            'recent_completion_rate': recent_completion_rate
        }

    def get_weekly_summary(self, user_id: int) -> Dict:
        """
        Get 7-day summary of tasks.

        Args:
            user_id: Telegram user ID

        Returns:
            Weekly summary dictionary
        """
        user_data = self.storage.load_user_data(user_id)

        if not user_data or not user_data.get('plan'):
            return {'success': False, 'error': 'no_plan'}

        daily_tasks = user_data.get('daily_tasks', {})

        # Get last 7 days
        summary = []
        today = datetime.now().date()

        for i in range(6, -1, -1):  # 6 days ago to today
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')

            # Count tasks for this day
            day_tasks = [tid for tid in daily_tasks.keys() if tid.startswith(date_str)]
            completed_tasks = [tid for tid in day_tasks if daily_tasks[tid].get('completed')]

            summary.append({
                'date': date_str,
                'weekday': date.strftime('%A'),
                'total_tasks': len(day_tasks),
                'completed_tasks': len(completed_tasks),
                'completion_rate': (len(completed_tasks) / len(day_tasks) * 100) if day_tasks else 0
            })

        return {
            'success': True,
            'summary': summary,
            'week_start': summary[0]['date'] if summary else None,
            'week_end': summary[-1]['date'] if summary else None
        }

    def _calculate_streak(self, user_data: Dict) -> int:
        """
        Calculate current streak of consecutive days with completed tasks.

        Args:
            user_data: User data dictionary

        Returns:
            Streak count (days)
        """
        daily_tasks = user_data.get('daily_tasks', {})

        # Get all dates with completed tasks
        completed_dates = set()
        for task_id, task_data in daily_tasks.items():
            if task_data.get('completed'):
                date_str = task_id.rsplit('_', 1)[0]
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    completed_dates.add(date)
                except ValueError:
                    continue

        if not completed_dates:
            return 0

        # Check streak from today backwards
        streak = 0
        current_date = datetime.now().date()

        while current_date in completed_dates:
            streak += 1
            current_date -= timedelta(days=1)

        return streak

    def _update_streak(self, user_data: Dict) -> None:
        """
        Update user's streak information.

        Args:
            user_data: User data dictionary (modified in place)
        """
        streak = self._calculate_streak(user_data)

        if 'stats' not in user_data:
            user_data['stats'] = {}

        user_data['stats']['current_streak'] = streak
        user_data['stats']['last_updated'] = datetime.now().isoformat()

        # Update best streak if current is higher
        best_streak = user_data['stats'].get('best_streak', 0)
        if streak > best_streak:
            user_data['stats']['best_streak'] = streak

    def _calculate_recent_completion_rate(self, user_data: Dict) -> float:
        """
        Calculate completion rate for last 7 days.

        Args:
            user_data: User data dictionary

        Returns:
            Completion rate as percentage (0-100)
        """
        daily_tasks = user_data.get('daily_tasks', {})

        # Get tasks from last 7 days
        today = datetime.now().date()
        start_date = today - timedelta(days=6)

        total_tasks = 0
        completed_tasks = 0

        for task_id, task_data in daily_tasks.items():
            try:
                date_str = task_id.rsplit('_', 1)[0]
                task_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                if start_date <= task_date <= today:
                    total_tasks += 1
                    if task_data.get('completed'):
                        completed_tasks += 1
            except (ValueError, AttributeError):
                continue

        if total_tasks == 0:
            return 0.0

        return (completed_tasks / total_tasks) * 100
