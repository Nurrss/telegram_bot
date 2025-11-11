"""
Reminder Generator Module
Creates personalized reminders based on user communication style.
"""

import random
from typing import Dict, List


class ReminderGenerator:
    """
    Generates personalized reminder messages based on user's communication style.
    Supports Russian and Kazakh languages with formal/casual variations.
    """

    def __init__(self):
        """Initialize ReminderGenerator."""
        pass

    def generate_morning_reminder(self, user_name: str, style: Dict, streak: int = 0) -> str:
        """
        Generate morning reminder (7 AM).

        Args:
            user_name: User's name
            style: User's communication style dict
            streak: Current streak count

        Returns:
            Reminder message string
        """
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')
        emoji_usage = style.get('emoji_usage', 'low')

        if language == 'kazakh':
            return self._generate_kazakh_morning(user_name, formality, emoji_usage, streak)
        else:
            return self._generate_russian_morning(user_name, formality, emoji_usage, streak)

    def generate_afternoon_reminder(self, user_name: str, style: Dict, tasks_completed: int, total_tasks: int) -> str:
        """
        Generate afternoon reminder (2 PM).

        Args:
            user_name: User's name
            style: User's communication style dict
            tasks_completed: Number of completed tasks
            total_tasks: Total number of tasks

        Returns:
            Reminder message string
        """
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')
        emoji_usage = style.get('emoji_usage', 'low')

        if language == 'kazakh':
            return self._generate_kazakh_afternoon(user_name, formality, emoji_usage, tasks_completed, total_tasks)
        else:
            return self._generate_russian_afternoon(user_name, formality, emoji_usage, tasks_completed, total_tasks)

    def generate_evening_reminder(self, user_name: str, style: Dict, tasks_completed: int, total_tasks: int) -> str:
        """
        Generate evening reminder (6 PM).

        Args:
            user_name: User's name
            style: User's communication style dict
            tasks_completed: Number of completed tasks
            total_tasks: Total number of tasks

        Returns:
            Reminder message string
        """
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')
        emoji_usage = style.get('emoji_usage', 'low')

        if language == 'kazakh':
            return self._generate_kazakh_evening(user_name, formality, emoji_usage, tasks_completed, total_tasks)
        else:
            return self._generate_russian_evening(user_name, formality, emoji_usage, tasks_completed, total_tasks)

    def _generate_russian_morning(self, name: str, formality: str, emoji_usage: str, streak: int) -> str:
        """Generate Russian morning reminder."""
        if formality == 'formal':
            greetings = [
                f"Доброе утро, {name}!",
                f"Здравствуйте, {name}!",
                f"Добрый день, {name}!"
            ]
            messages = [
                "Пора начать работу над вашим планом.",
                "Сегодня отличный день для достижения целей.",
                "Не забудьте выполнить задачи на сегодня."
            ]
            ending = "Посмотрите задачи с помощью /tasks"
        else:
            greetings = [
                f"Доброе утро, {name}!",
                f"Привет, {name}!",
                f"С добрым утром, {name}!"
            ]
            messages = [
                "Время работать над своими целями!",
                "Сегодня будет продуктивный день!",
                "Не забудь про свои задачи!"
            ]
            ending = "Смотри задачи: /tasks"

        greeting = random.choice(greetings)
        message = random.choice(messages)

        # Add streak info if exists
        if streak > 0:
            if formality == 'formal':
                streak_text = f"\nВаша серия: {streak} дней подряд!"
            else:
                streak_text = f"\nТвоя серия: {streak} дней подряд!"

            if emoji_usage == 'high':
                streak_text = f"🔥 {streak_text}"
        else:
            streak_text = ""

        # Add emojis
        if emoji_usage == 'high':
            greeting = f"☀️ {greeting}"
            ending = f"📋 {ending}"

        return f"{greeting}\n{message}{streak_text}\n\n{ending}"

    def _generate_russian_afternoon(self, name: str, formality: str, emoji_usage: str, completed: int, total: int) -> str:
        """Generate Russian afternoon reminder."""
        completion_rate = (completed / total * 100) if total > 0 else 0

        if formality == 'formal':
            greeting = f"{name}, как продвигается работа?"
            if completion_rate >= 75:
                feedback = "Отличный прогресс! Продолжайте в том же духе."
            elif completion_rate >= 50:
                feedback = "Хорошая работа! Осталось совсем немного."
            elif completion_rate >= 25:
                feedback = "Вы на правильном пути. Продолжайте!"
            else:
                feedback = "Еще есть время выполнить задачи."
            ending = f"Выполнено: {completed}/{total} задач."
        else:
            greeting = f"{name}, как дела?"
            if completion_rate >= 75:
                feedback = "Отлично! Так держать!"
            elif completion_rate >= 50:
                feedback = "Хорошо идёшь! Осталось немного."
            elif completion_rate >= 25:
                feedback = "Продолжай! Ты можешь!"
            else:
                feedback = "Давай, время еще есть!"
            ending = f"Готово: {completed}/{total}"

        # Add emojis
        if emoji_usage == 'high':
            if completion_rate >= 75:
                greeting = f"🌟 {greeting}"
            elif completion_rate >= 50:
                greeting = f"👍 {greeting}"
            else:
                greeting = f"⏰ {greeting}"
            ending = f"✅ {ending}"

        return f"{greeting}\n{feedback}\n\n{ending}"

    def _generate_russian_evening(self, name: str, formality: str, emoji_usage: str, completed: int, total: int) -> str:
        """Generate Russian evening reminder."""
        completion_rate = (completed / total * 100) if total > 0 else 0

        if formality == 'formal':
            greeting = f"Добрый вечер, {name}!"
            if completion_rate == 100:
                feedback = "Превосходно! Вы выполнили все задачи сегодня."
                encouragement = "Так держать!"
            elif completion_rate >= 75:
                feedback = f"Отличная работа! Выполнено {completed} из {total} задач."
                encouragement = "Завтра продолжим с новыми силами."
            elif completion_rate >= 50:
                feedback = f"Хороший результат. Выполнено {completed} из {total}."
                encouragement = "Завтра получится лучше!"
            else:
                feedback = f"Сегодня получилось {completed} из {total} задач."
                encouragement = "Не расстраивайтесь, завтра новый день!"
            ending = "Отдохните и подготовьтесь к новому дню."
        else:
            greeting = f"Привет, {name}!"
            if completion_rate == 100:
                feedback = "Супер! Все задачи выполнены!"
                encouragement = "Ты молодец! 🎉" if emoji_usage == 'high' else "Ты молодец!"
            elif completion_rate >= 75:
                feedback = f"Отлично! Сделано {completed}/{total}."
                encouragement = "Завтра продолжим!"
            elif completion_rate >= 50:
                feedback = f"Неплохо! Готово {completed}/{total}."
                encouragement = "Завтра наверстаем!"
            else:
                feedback = f"Сегодня {completed}/{total}."
                encouragement = "Ничего, завтра лучше!"
            ending = "Отдохни и набирайся сил!"

        # Add emojis
        if emoji_usage == 'high':
            if completion_rate == 100:
                greeting = f"🌙 {greeting}"
                ending = f"💪 {ending}"
            elif completion_rate >= 50:
                greeting = f"🌙 {greeting}"
            else:
                greeting = f"🌆 {greeting}"

        return f"{greeting}\n{feedback} {encouragement}\n\n{ending}"

    def _generate_kazakh_morning(self, name: str, formality: str, emoji_usage: str, streak: int) -> str:
        """Generate Kazakh morning reminder."""
        if formality == 'formal':
            greetings = [
                f"Қайырлы таң, {name}!",
                f"Сәлеметсіз бе, {name}!",
            ]
            messages = [
                "Жоспарыңызбен жұмыс бастау уақыты.",
                "Бүгін мақсаттарға жету үшін керемет күн.",
            ]
            ending = "Тапсырмаларды /tasks арқылы қараңыз"
        else:
            greetings = [
                f"Қайырлы таң, {name}!",
                f"Сәлем, {name}!",
            ]
            messages = [
                "Мақсаттарыңмен жұмыс бастау уақыты!",
                "Бүгін өнімді күн болады!",
            ]
            ending = "Тапсырмалар: /tasks"

        greeting = random.choice(greetings)
        message = random.choice(messages)

        # Add streak info
        if streak > 0:
            if formality == 'formal':
                streak_text = f"\nСіздің серияңыз: {streak} күн қатарынан!"
            else:
                streak_text = f"\nСенің серияң: {streak} күн қатарынан!"

            if emoji_usage == 'high':
                streak_text = f"🔥 {streak_text}"
        else:
            streak_text = ""

        # Add emojis
        if emoji_usage == 'high':
            greeting = f"☀️ {greeting}"
            ending = f"📋 {ending}"

        return f"{greeting}\n{message}{streak_text}\n\n{ending}"

    def _generate_kazakh_afternoon(self, name: str, formality: str, emoji_usage: str, completed: int, total: int) -> str:
        """Generate Kazakh afternoon reminder."""
        completion_rate = (completed / total * 100) if total > 0 else 0

        if formality == 'formal':
            greeting = f"{name}, жұмыс қалай жүріп жатыр?"
            if completion_rate >= 75:
                feedback = "Тамаша прогресс! Осылай жалғастырыңыз."
            elif completion_rate >= 50:
                feedback = "Жақсы жұмыс! Азырақ қалды."
            elif completion_rate >= 25:
                feedback = "Дұрыс жолдасыз. Жалғастырыңыз!"
            else:
                feedback = "Тапсырмаларды орындауға әлі уақыт бар."
            ending = f"Орындалды: {completed}/{total} тапсырма."
        else:
            greeting = f"{name}, қалай?"
            if completion_rate >= 75:
                feedback = "Керемет! Осылай!"
            elif completion_rate >= 50:
                feedback = "Жақсы бара жатыр! Азырақ қалды."
            elif completion_rate >= 25:
                feedback = "Жалғастыр! Сен істей аласың!"
            else:
                feedback = "Әлі уақыт бар!"
            ending = f"Дайын: {completed}/{total}"

        # Add emojis
        if emoji_usage == 'high':
            if completion_rate >= 75:
                greeting = f"🌟 {greeting}"
            elif completion_rate >= 50:
                greeting = f"👍 {greeting}"
            else:
                greeting = f"⏰ {greeting}"
            ending = f"✅ {ending}"

        return f"{greeting}\n{feedback}\n\n{ending}"

    def _generate_kazakh_evening(self, name: str, formality: str, emoji_usage: str, completed: int, total: int) -> str:
        """Generate Kazakh evening reminder."""
        completion_rate = (completed / total * 100) if total > 0 else 0

        if formality == 'formal':
            greeting = f"Қайырлы кеш, {name}!"
            if completion_rate == 100:
                feedback = "Тамаша! Бүгін барлық тапсырмаларды орындадыңыз."
                encouragement = "Осылай жалғастырыңыз!"
            elif completion_rate >= 75:
                feedback = f"Жақсы жұмыс! {completed}/{total} орындалды."
                encouragement = "Ертең жаңа күшпен жалғастырамыз."
            elif completion_rate >= 50:
                feedback = f"Жақсы нәтиже. {completed}/{total} орындалды."
                encouragement = "Ертең жақсырақ болады!"
            else:
                feedback = f"Бүгін {completed}/{total} шықты."
                encouragement = "Ештеңе емес, ертең жаңа күн!"
            ending = "Демалыңыз және жаңа күнге дайындалыңыз."
        else:
            greeting = f"Сәлем, {name}!"
            if completion_rate == 100:
                feedback = "Супер! Барлық тапсырмалар орындалды!"
                encouragement = "Сен жақсысың! 🎉" if emoji_usage == 'high' else "Сен жақсысың!"
            elif completion_rate >= 75:
                feedback = f"Керемет! Дайын {completed}/{total}."
                encouragement = "Ертең жалғастырамыз!"
            elif completion_rate >= 50:
                feedback = f"Жаман емес! Дайын {completed}/{total}."
                encouragement = "Ертең толықтырамыз!"
            else:
                feedback = f"Бүгін {completed}/{total}."
                encouragement = "Ештеңе, ертең жақсырақ!"
            ending = "Демал және күш жина!"

        # Add emojis
        if emoji_usage == 'high':
            if completion_rate == 100:
                greeting = f"🌙 {greeting}"
                ending = f"💪 {ending}"
            elif completion_rate >= 50:
                greeting = f"🌙 {greeting}"
            else:
                greeting = f"🌆 {greeting}"

        return f"{greeting}\n{feedback} {encouragement}\n\n{ending}"

    def generate_streak_milestone(self, user_name: str, style: Dict, streak: int) -> str:
        """
        Generate milestone message for streak achievements.

        Args:
            user_name: User's name
            style: User's communication style
            streak: Streak count

        Returns:
            Milestone message
        """
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')
        emoji_usage = style.get('emoji_usage', 'low')

        # Milestone days
        if streak not in [7, 14, 30, 50, 100, 365]:
            return ""

        if language == 'kazakh':
            if formality == 'formal':
                message = f"🎉 {user_name}, құттықтаймыз!\n\nСіз {streak} күн қатарынан тапсырмаларды орындап жатырсыз! Керемет нәтиже!"
            else:
                message = f"🎉 {user_name}, құттықтаймыз!\n\nСен {streak} күн қатарынан орындап жатырсың! Керемет!"
        else:
            if formality == 'formal':
                message = f"🎉 {user_name}, поздравляем!\n\nВы выполняете задачи {streak} дней подряд! Отличный результат!"
            else:
                message = f"🎉 {user_name}, поздравляем!\n\nТы выполняешь задачи {streak} дней подряд! Отлично!"

        if emoji_usage == 'high':
            message += " 🔥💪✨"

        return message
