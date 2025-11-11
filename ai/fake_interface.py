"""
Fake AI Interface Module
Used for development and testing before real Claude API integration.
Simulates AI responses with personality adaptation.
"""

import asyncio
import random
from typing import Dict, Any, List
from datetime import datetime
from ai.base_interface import AIInterface
from utils.style_detector import StyleDetector


class FakeAI(AIInterface):
    """
    Fake AI implementation for development and testing.
    Simulates Claude API with pre-made responses and style adaptation.
    """

    def __init__(self):
        """Initialize Fake AI interface."""
        self.model_name = "FakeAI-Dev"
        self.style_detector = StyleDetector()
        self.conversation_history = {}

    async def generate_response(self, prompt: str, user_id: int = None, style: Dict = None) -> str:
        """
        Generate a fake AI response based on user style.

        Args:
            prompt: The input prompt from user
            user_id: Telegram user ID
            style: User style dictionary (formality, language, etc.)

        Returns:
            Generated response string adapted to user style
        """
        # Simulate API delay
        await asyncio.sleep(random.uniform(1.0, 2.0))

        # Detect style if not provided
        if style is None:
            style = self.style_detector.analyze_style(prompt)

        # Generate response based on detected style
        response = self._generate_styled_response(prompt, style)

        return response

    async def generate_plan(self, user_data: dict, style: Dict = None) -> dict:
        """
        Generate a fake 5-year plan based on user data.

        Args:
            user_data: Dictionary containing user information and goals
            style: User style dictionary for personalization

        Returns:
            Dictionary containing the fake generated plan
        """
        # Simulate API delay
        await asyncio.sleep(random.uniform(1.5, 2.5))

        # Get user info
        user_goal = user_data.get('goal', 'карьерный рост')
        user_name = user_data.get('name', 'друг')

        # Detect style from goal text if available
        if style is None and user_goal:
            style = self.style_detector.analyze_style(user_goal)

        # Generate plan based on style
        plan = self._generate_styled_plan(user_name, user_goal, style)

        return plan

    def _generate_styled_response(self, prompt: str, style: Dict) -> str:
        """
        Generate response adapted to user's communication style.

        Args:
            prompt: User's message
            style: Detected style parameters

        Returns:
            Styled response string
        """
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')
        emoji_usage = style.get('emoji_usage', 'low')

        prompt_lower = prompt.lower()

        # Detect intent
        if any(word in prompt_lower for word in ['план', 'жоспар', 'plan', 'roadmap']):
            return self._plan_request_response(formality, language, emoji_usage)
        elif any(word in prompt_lower for word in ['помощь', 'help', 'көмек', 'көмектес']):
            return self._help_response(formality, language, emoji_usage)
        elif any(word in prompt_lower for word in ['прив', 'салам', 'сәлем', 'hello', 'hi']):
            return self._greeting_response(formality, language, emoji_usage)
        else:
            return self._general_response(formality, language, emoji_usage)

    def _plan_request_response(self, formality: str, language: str, emoji_usage: str) -> str:
        """Generate response for plan requests."""
        responses = {
            ('formal', 'russian'): "Конечно, я помогу вам составить персональный план. Для этого мне нужна информация о ваших целях и текущей ситуации. Расскажите, пожалуйста, чего вы хотите достичь?",
            ('casual', 'russian'): "Отлично! Давай создадим для тебя план. Расскажи, какие у тебя цели? Чего хочешь добиться?",
            ('formal', 'kazakh'): "Әрине, сізге жеке жоспар құруға көмектесемін. Ол үшін мақсаттарыңыз бен ағымдағы жағдайыңыз туралы ақпарат қажет. Не қол жеткізгіңіз келетінін айтып беріңізші.",
            ('casual', 'kazakh'): "Керемет! Саған жоспар жасап берейік. Мақсаттарың қандай? Неге жеткің келеді?",
        }

        key = (formality, language)
        response = responses.get(key, responses[('casual', 'russian')])

        if emoji_usage == 'high':
            emoji_map = {
                ('formal', 'russian'): "📋 " + response,
                ('casual', 'russian'): "🎯 " + response + " 💪",
                ('formal', 'kazakh'): "📋 " + response,
                ('casual', 'kazakh'): "🎯 " + response + " 💪",
            }
            response = emoji_map.get(key, response)

        return response

    def _help_response(self, formality: str, language: str, emoji_usage: str) -> str:
        """Generate response for help requests."""
        responses = {
            ('formal', 'russian'): "Я - AI-планировщик, который помогает создавать персональные 5-летние планы развития. Я могу помочь вам с планированием карьеры, образования и личностного роста.",
            ('casual', 'russian'): "Я помогаю строить планы на 5 лет! Карьера, учёба, саморазвитие - всё это можем спланировать вместе.",
            ('formal', 'kazakh'): "Мен жеке 5 жылдық даму жоспарларын құруға көмектесетін AI-жоспаршымын. Мансап, білім және жеке өсу жоспарлауға көмектесе аламын.",
            ('casual', 'kazakh'): "Мен 5 жылға жоспар құруға көмектесемін! Мансап, оқу, өзін-өзі дамыту - бәрін бірге жоспарлай аламыз.",
        }

        key = (formality, language)
        response = responses.get(key, responses[('casual', 'russian')])

        if emoji_usage == 'high':
            response = "🤖 " + response + " ✨"

        return response

    def _greeting_response(self, formality: str, language: str, emoji_usage: str) -> str:
        """Generate greeting response."""
        responses = {
            ('formal', 'russian'): "Здравствуйте! Рад помочь вам с планированием. Чем могу быть полезен?",
            ('casual', 'russian'): "Привет! Чем могу помочь?",
            ('formal', 'kazakh'): "Сәлеметсіз бе! Жоспарлауға көмектесуге қуаныштымын. Немен көмектесе аламын?",
            ('casual', 'kazakh'): "Сәлем! Немен көмектесейін?",
        }

        key = (formality, language)
        response = responses.get(key, responses[('casual', 'russian')])

        if emoji_usage == 'high':
            response = "👋 " + response + " 😊"

        return response

    def _general_response(self, formality: str, language: str, emoji_usage: str) -> str:
        """Generate general response."""
        responses = {
            ('formal', 'russian'): "Я понял ваш запрос. Могу помочь с созданием персонального плана развития. Используйте команду /plan для начала.",
            ('casual', 'russian'): "Понял! Могу помочь с планами. Жми /plan чтобы начать.",
            ('formal', 'kazakh'): "Сұранысыңызды түсіндім. Жеке даму жоспарын құруға көмектесе аламын. Бастау үшін /plan командасын пайдаланыңыз.",
            ('casual', 'kazakh'): "Түсінікті! Жоспармен көмектесе аламын. Бастау үшін /plan басыңыз.",
        }

        key = (formality, language)
        response = responses.get(key, responses[('casual', 'russian')])

        if emoji_usage == 'high':
            response = "💭 " + response

        return response

    def _generate_styled_plan(self, user_name: str, goal: str, style: Dict) -> dict:
        """
        Generate a fake 5-year plan with style adaptation.

        Args:
            user_name: User's name
            goal: User's goal
            style: Style parameters

        Returns:
            Dictionary with plan structure
        """
        language = style.get('language', 'russian')
        formality = style.get('formality', 'casual')

        if language == 'kazakh':
            return self._generate_kazakh_plan(user_name, goal, formality)
        else:
            return self._generate_russian_plan(user_name, goal, formality)

    def _generate_russian_plan(self, user_name: str, goal: str, formality: str) -> dict:
        """Generate Russian language plan."""
        greeting = f"Уважаемый {user_name}" if formality == 'formal' else user_name

        return {
            "user_name": user_name,
            "goal": goal,
            "greeting": greeting,
            "years": [
                {
                    "year": 1,
                    "title": "Фундамент и основы",
                    "description": "Изучение базовых навыков и построение фундамента",
                    "milestones": [
                        "Освоение основных инструментов",
                        "Первые практические проекты",
                        "Нетворкинг и поиск менторов"
                    ]
                },
                {
                    "year": 2,
                    "title": "Практика и опыт",
                    "description": "Применение знаний на практике",
                    "milestones": [
                        "Работа над реальными проектами",
                        "Развитие профессиональных навыков",
                        "Первые достижения"
                    ]
                },
                {
                    "year": 3,
                    "title": "Рост и развитие",
                    "description": "Углубление экспертизы",
                    "milestones": [
                        "Становление экспертом",
                        "Обучение других",
                        "Расширение влияния"
                    ]
                },
                {
                    "year": 4,
                    "title": "Мастерство",
                    "description": "Достижение высокого уровня",
                    "milestones": [
                        "Признание в профессии",
                        "Сложные проекты",
                        "Лидерство"
                    ]
                },
                {
                    "year": 5,
                    "title": "Цель достигнута",
                    "description": f"Достижение цели: {goal}",
                    "milestones": [
                        "Реализация амбиций",
                        "Новые горизонты",
                        "Передача опыта"
                    ]
                }
            ],
            "language": "russian",
            "formality": formality
        }

    def _generate_kazakh_plan(self, user_name: str, goal: str, formality: str) -> dict:
        """Generate Kazakh language plan."""
        greeting = f"Құрметті {user_name}" if formality == 'formal' else user_name

        return {
            "user_name": user_name,
            "goal": goal,
            "greeting": greeting,
            "years": [
                {
                    "year": 1,
                    "title": "Іргетас және негіздер",
                    "description": "Базалық дағдыларды үйрену және іргетас қалау",
                    "milestones": [
                        "Негізгі құралдарды меңгеру",
                        "Алғашқы практикалық жобалар",
                        "Желілік байланыс және менторлар іздеу"
                    ]
                },
                {
                    "year": 2,
                    "title": "Практика және тәжірибе",
                    "description": "Білімді практикада қолдану",
                    "milestones": [
                        "Нақты жобалармен жұмыс",
                        "Кәсіби дағдыларды дамыту",
                        "Алғашқы жетістіктер"
                    ]
                },
                {
                    "year": 3,
                    "title": "Өсу және даму",
                    "description": "Экспертизаны тереңдету",
                    "milestones": [
                        "Сарапшы болу",
                        "Басқаларды оқыту",
                        "Әсерді кеңейту"
                    ]
                },
                {
                    "year": 4,
                    "title": "Шеберлік",
                    "description": "Жоғары деңгейге жету",
                    "milestones": [
                        "Кәсібінде тану",
                        "Күрделі жобалар",
                        "Көшбасшылық"
                    ]
                },
                {
                    "year": 5,
                    "title": "Мақсатқа жету",
                    "description": f"Мақсатқа жету: {goal}",
                    "milestones": [
                        "Амбицияларды іске асыру",
                        "Жаңа көкжиектер",
                        "Тәжірибені беру"
                    ]
                }
            ],
            "language": "kazakh",
            "formality": formality
        }

    async def generate_daily_tasks(self, plan_data: Dict, day: int) -> List[str]:
        """
        Generate fake daily tasks from the plan.

        Args:
            plan_data: The user's 5-year plan data
            day: Day number (1-1825 for 5 years)

        Returns:
            List of daily tasks as strings
        """
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.5, 1.0))

        # Determine which year we're in (365 days per year)
        year = min(5, (day - 1) // 365 + 1)
        day_in_year = ((day - 1) % 365) + 1

        # Get language and formality from plan if available
        language = plan_data.get('language', 'russian')
        formality = plan_data.get('formality', 'casual')

        # Generate tasks based on language
        if language == 'kazakh':
            tasks = self._generate_kazakh_tasks(year, day_in_year, formality)
        else:
            tasks = self._generate_russian_tasks(year, day_in_year, formality)

        return tasks

    def _generate_russian_tasks(self, year: int, day_in_year: int, formality: str) -> List[str]:
        """Generate Russian language daily tasks."""
        # Determine quarter
        quarter = (day_in_year - 1) // 91 + 1  # ~91 days per quarter

        task_templates = {
            1: [  # Year 1: Foundation
                "Изучить основы выбранного направления (30 минут)",
                "Прочитать главу из профессиональной литературы",
                "Посмотреть обучающее видео по теме"
            ],
            2: [  # Year 2: Practice
                "Выполнить практическое задание",
                "Поработать над личным проектом (1 час)",
                "Проанализировать чужой код/работу"
            ],
            3: [  # Year 3: Growth
                "Помочь новичку с вопросом",
                "Написать статью/пост о своём опыте",
                "Изучить продвинутую технику"
            ],
            4: [  # Year 4: Mastery
                "Провести код-ревью или менторинг",
                "Работа над сложным проектом (2 часа)",
                "Выступить с докладом или презентацией"
            ],
            5: [  # Year 5: Goal Achievement
                "Стратегическое планирование",
                "Передача опыта: обучение команды",
                "Работа над масштабным проектом"
            ]
        }

        tasks = task_templates.get(year, task_templates[1])

        # Add day-specific context
        if formality == 'formal':
            tasks = [f"• {task}" for task in tasks]
        else:
            tasks = [f"✓ {task}" for task in tasks]

        # Add motivational task
        if formality == 'formal':
            tasks.append("• Рефлексия: записать сегодняшний прогресс")
        else:
            tasks.append("✓ Отметь свой прогресс за день!")

        return tasks

    def _generate_kazakh_tasks(self, year: int, day_in_year: int, formality: str) -> List[str]:
        """Generate Kazakh language daily tasks."""
        task_templates = {
            1: [  # Year 1: Foundation
                "Таңдаған бағыттың негіздерін үйрену (30 минут)",
                "Кәсіби әдебиеттен бір тарау оқу",
                "Тақырып бойынша оқу видеосын көру"
            ],
            2: [  # Year 2: Practice
                "Практикалық тапсырманы орындау",
                "Жеке жоба үстінде жұмыс (1 сағат)",
                "Басқа біреудің кодын/жұмысын талдау"
            ],
            3: [  # Year 3: Growth
                "Жаңадан бастаушыға көмектесу",
                "Өз тәжірибең туралы мақала/пост жазу",
                "Алдыңғы қатарлы техниканы үйрену"
            ],
            4: [  # Year 4: Mastery
                "Код-ревью немесе менторинг өткізу",
                "Күрделі жоба үстінде жұмыс (2 сағат)",
                "Баяндама немесе презентация жасау"
            ],
            5: [  # Year 5: Goal Achievement
                "Стратегиялық жоспарлау",
                "Тәжірибе беру: командаға оқыту",
                "Ауқымды жоба үстінде жұмыс"
            ]
        }

        tasks = task_templates.get(year, task_templates[1])

        # Add markers
        if formality == 'formal':
            tasks = [f"• {task}" for task in tasks]
        else:
            tasks = [f"✓ {task}" for task in tasks]

        # Add motivational task
        if formality == 'formal':
            tasks.append("• Рефлексия: бүгінгі прогресті жазу")
        else:
            tasks.append("✓ Бүгінгі прогресіңді белгіле!")

        return tasks
