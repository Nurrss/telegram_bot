"""
Base AI Interface Module
Defines the abstract interface that all AI implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class AIInterface(ABC):
    """
    Base interface that all AI implementations must follow.
    This ensures FakeAI and ClaudeAI have the same contract.
    """

    @abstractmethod
    async def generate_response(self, prompt: str, user_id: int, style: Dict = None) -> str:
        """
        Generate a response to user's message.

        Args:
            prompt: The user's message/prompt
            user_id: Telegram user ID
            style: Optional style parameters (formality, language, etc.)

        Returns:
            Generated response string
        """
        pass

    @abstractmethod
    async def generate_plan(self, user_data: Dict) -> Dict:
        """
        Generate a 5-year plan based on user profile.

        Args:
            user_data: Dictionary containing user information and goals

        Returns:
            Dictionary containing the generated plan structure
        """
        pass

    @abstractmethod
    async def generate_daily_tasks(self, plan_data: Dict, day: int) -> List[str]:
        """
        Generate daily tasks from the plan.

        Args:
            plan_data: The user's 5-year plan data
            day: Day number (1-1825 for 5 years)

        Returns:
            List of daily tasks as strings
        """
        pass
