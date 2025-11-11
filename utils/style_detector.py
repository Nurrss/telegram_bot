"""
Style Detector Module
Analyzes user messages to detect communication style and preferences.
"""

import re
from typing import Dict


class StyleDetector:
    """
    Detects user communication style from text.
    Analyzes formality, language, emoji usage, and verbosity.
    """

    # Formal Russian markers
    FORMAL_RUSSIAN = [
        'здравствуйте', 'уважаемый', 'благодарю', 'пожалуйста',
        'будьте добры', 'не могли бы', 'разрешите', 'извините',
        'позвольте', 'спасибо вам', 'с уважением'
    ]

    # Casual Russian markers
    CASUAL_RUSSIAN = [
        'привет', 'прив', 'ку', 'здарова', 'хай', 'дарова',
        'спс', 'пасиб', 'пож', 'давай', 'ок', 'окей',
        'чё', 'чего', 'ваще', 'короче', 'типа', 'блин'
    ]

    # Kazakh language markers
    KAZAKH_MARKERS = [
        'сәлем', 'сәлеметсіз', 'салам', 'қалайсың', 'қалайсыз',
        'рақмет', 'көмектес', 'көмек', 'жоспар', 'мақсат',
        'керек', 'қажет', 'бол', 'жасау', 'істеу',
        'өтінем', 'өтініш', 'құрметті', 'алға'
    ]

    # Russian language markers (to distinguish from Kazakh)
    RUSSIAN_MARKERS = [
        'привет', 'здравствуйте', 'помогите', 'помощь', 'план',
        'нужно', 'надо', 'сделать', 'помочь', 'цель',
        'спасибо', 'пожалуйста', 'хорошо', 'да', 'нет'
    ]

    def __init__(self):
        """Initialize style detector."""
        pass

    def analyze_style(self, text: str) -> Dict[str, str]:
        """
        Analyze text and return style parameters.

        Args:
            text: User's message text

        Returns:
            Dictionary with style parameters:
            - formality: 'formal' or 'casual'
            - language: 'russian' or 'kazakh'
            - emoji_usage: 'high' or 'low'
            - verbosity: 'brief' or 'detailed'
        """
        if not text:
            return self._default_style()

        text_lower = text.lower()

        formality = self._detect_formality(text_lower)
        language = self._detect_language(text_lower)
        emoji_usage = self._detect_emoji_usage(text)
        verbosity = self._detect_verbosity(text)

        return {
            'formality': formality,
            'language': language,
            'emoji_usage': emoji_usage,
            'verbosity': verbosity
        }

    def _detect_formality(self, text: str) -> str:
        """
        Detect formality level.

        Args:
            text: Lowercased message text

        Returns:
            'formal' or 'casual'
        """
        formal_count = sum(1 for marker in self.FORMAL_RUSSIAN if marker in text)
        casual_count = sum(1 for marker in self.CASUAL_RUSSIAN if marker in text)

        # Check for formal indicators
        has_full_punctuation = text.count('.') > 0 or text.count('!') > 1
        has_long_words = any(len(word) > 12 for word in text.split())

        if formal_count > casual_count:
            return 'formal'
        elif casual_count > formal_count:
            return 'casual'
        else:
            # Default based on other indicators
            if has_full_punctuation and has_long_words:
                return 'formal'
            else:
                return 'casual'

    def _detect_language(self, text: str) -> str:
        """
        Detect language (Russian or Kazakh).

        Args:
            text: Lowercased message text

        Returns:
            'russian' or 'kazakh'
        """
        kazakh_count = sum(1 for marker in self.KAZAKH_MARKERS if marker in text)
        russian_count = sum(1 for marker in self.RUSSIAN_MARKERS if marker in text)

        # Check for specific Kazakh characters
        kazakh_chars = ['ә', 'ғ', 'қ', 'ң', 'ө', 'ұ', 'ү', 'һ', 'і']
        has_kazakh_chars = any(char in text for char in kazakh_chars)

        if kazakh_count > russian_count or has_kazakh_chars:
            return 'kazakh'
        else:
            return 'russian'

    def _detect_emoji_usage(self, text: str) -> str:
        """
        Detect emoji usage level.

        Args:
            text: Original message text (not lowercased)

        Returns:
            'high' or 'low'
        """
        # Count emojis using regex
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )

        emoji_count = len(emoji_pattern.findall(text))

        # High usage: 2 or more emojis, or emoji density > 10%
        if emoji_count >= 2 or (emoji_count > 0 and len(text) < 20):
            return 'high'
        else:
            return 'low'

    def _detect_verbosity(self, text: str) -> str:
        """
        Detect verbosity level.

        Args:
            text: Message text

        Returns:
            'brief' or 'detailed'
        """
        word_count = len(text.split())
        sentence_count = max(1, text.count('.') + text.count('!') + text.count('?'))

        # Brief: less than 10 words or short sentences
        # Detailed: more than 20 words or multiple sentences
        if word_count < 10:
            return 'brief'
        elif word_count > 20 or sentence_count > 2:
            return 'detailed'
        else:
            # Medium length defaults to brief
            return 'brief'

    def _default_style(self) -> Dict[str, str]:
        """
        Return default style parameters.

        Returns:
            Default style dictionary
        """
        return {
            'formality': 'casual',
            'language': 'russian',
            'emoji_usage': 'low',
            'verbosity': 'brief'
        }

    def create_system_prompt(self, style: Dict) -> str:
        """
        Create AI system prompt based on detected communication style.

        Args:
            style: Style dictionary with formality, language, emoji_usage, verbosity

        Returns:
            System prompt string for AI
        """
        formality = style.get('formality', 'casual')
        language = style.get('language', 'russian')
        emoji_usage = style.get('emoji_usage', 'low')
        verbosity = style.get('verbosity', 'brief')

        # Base prompt templates
        if language == 'kazakh':
            base_prompt = self._create_kazakh_prompt(formality, emoji_usage, verbosity)
        else:
            base_prompt = self._create_russian_prompt(formality, emoji_usage, verbosity)

        return base_prompt

    def _create_russian_prompt(self, formality: str, emoji_usage: str, verbosity: str) -> str:
        """Create Russian language system prompt."""
        if formality == 'formal':
            tone = (
                "Вы - профессиональный AI-ассистент по планированию карьеры. "
                "Общайтесь уважительно, используйте 'Вы'. "
                "Давайте структурированные и обоснованные рекомендации."
            )
        else:
            tone = (
                "Ты - дружелюбный AI-помощник по планированию. "
                "Общайся на 'ты', будь позитивным и поддерживающим. "
                "Давай практичные советы простым языком."
            )

        if emoji_usage == 'high':
            emoji_instruction = " Используй эмодзи для эмоциональности. "
        else:
            emoji_instruction = " Минимизируй использование эмодзи. "

        if verbosity == 'detailed':
            length_instruction = "Давай подробные, развёрнутые ответы (5-7 предложений)."
        else:
            length_instruction = "Давай краткие, ёмкие ответы (2-3 предложения)."

        return f"{tone}{emoji_instruction}{length_instruction}"

    def _create_kazakh_prompt(self, formality: str, emoji_usage: str, verbosity: str) -> str:
        """Create Kazakh language system prompt."""
        if formality == 'formal':
            tone = (
                "Сіз - мансапты жоспарлау бойынша кәсіби AI-ассистентсіз. "
                "'Сіз' деп құрметпен қарап, құрылымдалған және негізделген ұсыныстар беріңіз."
            )
        else:
            tone = (
                "Сен - жоспарлау бойынша достық AI-көмекшісің. "
                "'Сен' деп сөйлес, оң көңіл-күйде және қолдаушы бол. "
                "Қарапайым тілмен практикалық кеңестер бер."
            )

        if emoji_usage == 'high':
            emoji_instruction = " Эмоционалдық болу үшін эмодзи қолдан. "
        else:
            emoji_instruction = " Эмодзи қолдануды азайт. "

        if verbosity == 'detailed':
            length_instruction = "Толық, кеңейтілген жауаптар бер (5-7 сөйлем)."
        else:
            length_instruction = "Қысқа, нұсқа жауаптар бер (2-3 сөйлем)."

        return f"{tone}{emoji_instruction}{length_instruction}"
