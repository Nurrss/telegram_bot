"""
Claude AI Integration Module
Real Claude API integration for production use.
"""

import os
import asyncio
from typing import Dict, List, Callable, Any
from datetime import datetime
import anthropic
import time

from ai.base_interface import AIInterface
from utils.logger import logger
from utils.style_detector import StyleDetector
from utils.cost_tracker import CostTracker


class ClaudeAI(AIInterface):
    """
    Real Claude API implementation for production.
    Integrates with Anthropic's Claude API.
    """

    def __init__(self):
        """Initialize Claude AI with API key."""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment variables. "
                "Please add it to your .env file."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model_name = "claude-3-5-sonnet-20241022"  # Latest Sonnet model
        self.style_detector = StyleDetector()
        self.cost_tracker = CostTracker()

        logger.info(f"Claude AI initialized with model: {self.model_name}")

    async def _retry_with_backoff(
        self,
        func: Callable,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0
    ) -> Any:
        """
        Retry a function with exponential backoff.

        Args:
            func: Function to retry
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds

        Returns:
            Result from the function

        Raises:
            Last exception if all retries fail
        """
        delay = initial_delay
        last_exception = None

        for attempt in range(max_retries):
            try:
                return await asyncio.to_thread(func)
            except anthropic.RateLimitError as e:
                last_exception = e
                logger.warning(f"Rate limit hit, attempt {attempt + 1}/{max_retries}. Waiting {delay}s...")
                await asyncio.sleep(delay)
                delay = min(delay * 2, max_delay)  # Exponential backoff
            except anthropic.APIConnectionError as e:
                last_exception = e
                logger.warning(f"Connection error, attempt {attempt + 1}/{max_retries}. Waiting {delay}s...")
                await asyncio.sleep(delay)
                delay = min(delay * 2, max_delay)
            except anthropic.APIStatusError as e:
                # Don't retry on 4xx errors (except rate limit)
                if 400 <= e.status_code < 500 and e.status_code != 429:
                    logger.error(f"Client error {e.status_code}: {e}")
                    raise
                last_exception = e
                logger.warning(f"API error {e.status_code}, attempt {attempt + 1}/{max_retries}. Waiting {delay}s...")
                await asyncio.sleep(delay)
                delay = min(delay * 2, max_delay)
            except Exception as e:
                # Don't retry on unexpected errors
                logger.error(f"Unexpected error in retry logic: {e}")
                raise

        # All retries exhausted
        logger.error(f"All {max_retries} retry attempts failed")
        raise last_exception

    async def generate_response(self, prompt: str, user_id: int, style: Dict = None) -> str:
        """
        Generate a response using Claude API.

        Args:
            prompt: The input prompt from user
            user_id: Telegram user ID
            style: User style dictionary (formality, language, etc.)

        Returns:
            Generated response string adapted to user style
        """
        try:
            # Detect style if not provided
            if style is None:
                style = self.style_detector.analyze_style(prompt)

            # Create system prompt based on style
            system_prompt = self.style_detector.create_system_prompt(style)

            # Add specific instructions for brief responses
            verbosity = style.get('verbosity', 'brief')
            if verbosity == 'brief':
                system_prompt += " Давай краткие ответы (2-3 предложения)."
            else:
                system_prompt += " Давай подробные ответы (5-7 предложений)."

            # Call Claude API with retry logic
            start_time = datetime.now()

            response = await self._retry_with_backoff(
                lambda: self.client.messages.create(
                    model=self.model_name,
                    max_tokens=500,  # Limit response length
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            )

            # Extract text from response
            response_text = response.content[0].text

            # Track cost
            elapsed_time = (datetime.now() - start_time).total_seconds()
            self.cost_tracker.track_request(
                model=self.model_name,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                user_id=user_id,
                request_type='generate_response',
                elapsed_time=elapsed_time
            )

            logger.info(
                f"Claude API response generated for user {user_id} "
                f"(in: {response.usage.input_tokens}, out: {response.usage.output_tokens} tokens)"
            )

            return response_text

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            return self._get_error_fallback_response(style)

        except Exception as e:
            logger.error(f"Unexpected error in Claude API: {e}")
            return self._get_error_fallback_response(style)

    async def generate_plan(self, user_data: Dict, style: Dict = None) -> Dict:
        """
        Generate a 5-year plan using Claude API.

        Args:
            user_data: Dictionary containing user information and goals
            style: User style dictionary for personalization

        Returns:
            Dictionary containing the generated plan structure
        """
        try:
            # Get user info
            name = user_data.get('name', 'пользователь')
            age = user_data.get('age', 25)
            goals = user_data.get('goals', 'личное развитие')
            preferred_language = user_data.get('preferred_language', 'russian')

            # Detect or use provided style
            if style is None:
                style = user_data.get('communication_style', {})

            language = style.get('language', preferred_language)

            # Create prompt for plan generation
            if language == 'kazakh':
                prompt = self._create_kazakh_plan_prompt(name, age, goals)
            else:
                prompt = self._create_russian_plan_prompt(name, age, goals)

            # System prompt for structured output
            system_prompt = (
                "Ты - эксперт по планированию карьеры и личного развития. "
                "Создай реалистичный, достижимый 5-летний план с конкретными этапами. "
                "Структурируй план по годам с четкими целями и этапами."
            )

            # Call Claude API with retry logic
            start_time = datetime.now()

            response = await self._retry_with_backoff(
                lambda: self.client.messages.create(
                    model=self.model_name,
                    max_tokens=4000,  # Longer response for detailed plan
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            )

            # Parse response into structured plan
            plan_text = response.content[0].text
            plan = self._parse_plan_response(plan_text, user_data, language, style.get('formality', 'casual'))

            # Track cost
            elapsed_time = (datetime.now() - start_time).total_seconds()
            self.cost_tracker.track_request(
                model=self.model_name,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                user_id=user_data.get('user_id'),
                request_type='generate_plan',
                elapsed_time=elapsed_time
            )

            logger.info(
                f"Plan generated for user {user_data.get('user_id')} "
                f"(in: {response.usage.input_tokens}, out: {response.usage.output_tokens} tokens)"
            )

            return plan

        except Exception as e:
            logger.error(f"Error generating plan with Claude API: {e}")
            # Fallback to basic plan structure
            return self._create_fallback_plan(user_data, language)

    async def generate_daily_tasks(self, plan_data: Dict, day: int) -> List[str]:
        """
        Generate daily tasks using Claude API.

        Args:
            plan_data: The user's 5-year plan data
            day: Day number (1-1825 for 5 years)

        Returns:
            List of daily tasks as strings
        """
        try:
            # Determine year and context
            year = min(5, (day - 1) // 365 + 1)
            language = plan_data.get('language', 'russian')

            # Get relevant year's goals from plan
            years = plan_data.get('years', [])
            if year <= len(years):
                year_data = years[year - 1]
                year_focus = year_data.get('title', f'Year {year}')
                year_goals = year_data.get('milestones', [])
            else:
                year_focus = f"Year {year}"
                year_goals = []

            # Create prompt
            if language == 'kazakh':
                prompt = (
                    f"{year} жыл, {day} күн.\n"
                    f"Бағыт: {year_focus}\n"
                    f"4 практикалық тапсырма жаса (қысқа, нақты, орындалатын).\n"
                    f"Тек тапсырмалар тізімін жаз, түсініктемесіз."
                )
            else:
                prompt = (
                    f"Год {year}, день {day}.\n"
                    f"Фокус: {year_focus}\n"
                    f"Создай 4 практические задачи (краткие, конкретные, выполнимые).\n"
                    f"Напиши только список задач, без объяснений."
                )

            # Call Claude API with retry logic
            start_time = datetime.now()

            response = await self._retry_with_backoff(
                lambda: self.client.messages.create(
                    model=self.model_name,
                    max_tokens=300,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            )

            # Parse tasks from response
            tasks_text = response.content[0].text
            tasks = self._parse_tasks_response(tasks_text)

            # Ensure we have exactly 4 tasks
            if len(tasks) < 4:
                tasks.extend([
                    "Дополнительная задача на день",
                    "Рефлексия и планирование"
                ][:4 - len(tasks)])
            tasks = tasks[:4]

            # Track cost
            elapsed_time = (datetime.now() - start_time).total_seconds()
            self.cost_tracker.track_request(
                model=self.model_name,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                user_id=plan_data.get('user_id'),
                request_type='generate_daily_tasks',
                elapsed_time=elapsed_time
            )

            return tasks

        except Exception as e:
            logger.error(f"Error generating daily tasks: {e}")
            # Fallback to generic tasks
            return self._get_fallback_tasks(year, language)

    def _create_russian_plan_prompt(self, name: str, age: int, goals: str) -> str:
        """Create Russian prompt for plan generation."""
        return f"""Создай персональный 5-летний план развития для человека:
- Имя: {name}
- Возраст: {age}
- Цели: {goals}

Создай план из 5 лет. Для каждого года укажи:
1. Название года (краткое, мотивирующее)
2. Описание (1-2 предложения)
3. 3-4 ключевых этапа (milestones)

Формат ответа:
ГОД 1: [название]
[описание]
- [этап 1]
- [этап 2]
- [этап 3]

[и так далее для всех 5 лет]

План должен быть реалистичным и достижимым."""

    def _create_kazakh_plan_prompt(self, name: str, age: int, goals: str) -> str:
        """Create Kazakh prompt for plan generation."""
        return f"""Адам үшін 5 жылдық жеке даму жоспарын жаса:
- Аты: {name}
- Жасы: {age}
- Мақсаттары: {goals}

5 жылдың жоспарын жаса. Әр жыл үшін көрсет:
1. Жылдың атауы (қысқа, ынталандырушы)
2. Сипаттама (1-2 сөйлем)
3. 3-4 негізгі кезең

Жауап форматы:
1 ЖЫЛ: [атауы]
[сипаттама]
- [кезең 1]
- [кезең 2]
- [кезең 3]

[барлық 5 жылға осылай]

Жоспар нақты және қол жетімді болуы керек."""

    def _parse_plan_response(self, plan_text: str, user_data: Dict, language: str, formality: str) -> Dict:
        """Parse Claude's response into structured plan."""
        # Basic parsing - split by years
        years = []

        # Split text into year sections
        year_sections = []
        if language == 'kazakh':
            # Look for "1 ЖЫЛ:", "2 ЖЫЛ:", etc.
            import re
            year_sections = re.split(r'(\d+\s+ЖЫЛ:)', plan_text)
        else:
            # Look for "ГОД 1:", "ГОД 2:", etc.
            import re
            year_sections = re.split(r'(ГОД\s+\d+:)', plan_text)

        # Parse each year
        for i in range(1, len(year_sections), 2):
            if i + 1 >= len(year_sections):
                break

            year_num = (i + 1) // 2
            year_content = year_sections[i + 1].strip()

            # Extract title (first line)
            lines = year_content.split('\n')
            title = lines[0].strip() if lines else f"Год {year_num}"

            # Extract description and milestones
            description = ""
            milestones = []

            for line in lines[1:]:
                line = line.strip()
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    milestones.append(line.lstrip('-•* '))
                elif line and not milestones:
                    description += " " + line

            years.append({
                'year': year_num,
                'title': title,
                'description': description.strip(),
                'milestones': milestones[:4] if milestones else [
                    f"Этап 1 года {year_num}",
                    f"Этап 2 года {year_num}",
                    f"Этап 3 года {year_num}"
                ]
            })

        # Ensure we have 5 years
        while len(years) < 5:
            year_num = len(years) + 1
            years.append({
                'year': year_num,
                'title': f"Год {year_num}",
                'description': f"Развитие на {year_num} году",
                'milestones': [f"Этап {i}" for i in range(1, 4)]
            })

        return {
            'user_name': user_data.get('name', 'пользователь'),
            'goal': user_data.get('goals', ''),
            'greeting': user_data.get('name', 'пользователь'),
            'years': years[:5],
            'language': language,
            'formality': formality,
            'created_at': datetime.now().isoformat()
        }

    def _parse_tasks_response(self, tasks_text: str) -> List[str]:
        """Parse tasks from Claude's response."""
        tasks = []
        lines = tasks_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            # Remove numbering and bullet points
            line = line.lstrip('0123456789.-)• \t')
            if line and len(line) > 5:  # Minimum task length
                tasks.append(line)

        return tasks

    def _get_fallback_tasks(self, year: int, language: str) -> List[str]:
        """Get fallback tasks if API fails."""
        if language == 'kazakh':
            return [
                "Күнделікті тапсырманы орындау",
                "Білімді тереңдету",
                "Практикалық жаттығу",
                "Прогресті талдау"
            ]
        else:
            return [
                "Выполнить ежедневное задание",
                "Углубить знания",
                "Практическое упражнение",
                "Анализ прогресса"
            ]

    def _create_fallback_plan(self, user_data: Dict, language: str) -> Dict:
        """Create fallback plan if API fails."""
        name = user_data.get('name', 'User')
        goal = user_data.get('goals', 'развитие')

        if language == 'kazakh':
            years = [
                {'year': 1, 'title': 'Іргетас', 'description': 'Негізді қалау', 'milestones': ['Бастау', 'Үйрену', 'Практика']},
                {'year': 2, 'title': 'Даму', 'description': 'Дағдыларды дамыту', 'milestones': ['Тереңдету', 'Қолдану', 'Жетілдіру']},
                {'year': 3, 'title': 'Өсу', 'description': 'Тәжірибе жинау', 'milestones': ['Сарапшылық', 'Менторлық', 'Жоба']},
                {'year': 4, 'title': 'Шеберлік', 'description': 'Мастер болу', 'milestones': ['Көшбасшылық', 'Инновация', 'Тану']},
                {'year': 5, 'title': 'Мақсат', 'description': goal, 'milestones': ['Жетістік', 'Беру', 'Жаңа']}
            ]
        else:
            years = [
                {'year': 1, 'title': 'Фундамент', 'description': 'Построение основы', 'milestones': ['Начало', 'Обучение', 'Практика']},
                {'year': 2, 'title': 'Развитие', 'description': 'Развитие навыков', 'milestones': ['Углубление', 'Применение', 'Совершенствование']},
                {'year': 3, 'title': 'Рост', 'description': 'Набор опыта', 'milestones': ['Экспертиза', 'Менторство', 'Проекты']},
                {'year': 4, 'title': 'Мастерство', 'description': 'Достижение мастерства', 'milestones': ['Лидерство', 'Инновации', 'Признание']},
                {'year': 5, 'title': 'Цель', 'description': goal, 'milestones': ['Достижение', 'Передача опыта', 'Новые горизонты']}
            ]

        return {
            'user_name': name,
            'goal': goal,
            'greeting': name,
            'years': years,
            'language': language,
            'formality': 'casual',
            'created_at': datetime.now().isoformat()
        }

    def _get_error_fallback_response(self, style: Dict = None) -> str:
        """Get fallback response when API fails."""
        if style and style.get('language') == 'kazakh':
            return "Кешіріңіз, қазір жауап бере алмаймын. Кейінірек қайталап көріңіз."
        else:
            return "Извините, сейчас не могу ответить. Попробуйте позже."
