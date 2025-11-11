"""
AI Factory Module
Creates AI instances based on configuration.
"""

import os
from utils.logger import logger
from ai.base_interface import AIInterface
from ai.fake_interface import FakeAI
from ai.claude_ai import ClaudeAI


def create_ai() -> AIInterface:
    """
    Create and return AI instance based on environment configuration.

    Reads USE_FAKE_AI from environment variables.
    If True or not set, returns FakeAI for development.
    If False, returns real ClaudeAI (requires Claude API key).

    Returns:
        AI instance implementing AIInterface (FakeAI or ClaudeAI)
    """
    use_fake = os.getenv('USE_FAKE_AI', 'true').lower() == 'true'

    if use_fake:
        logger.info("🎭 Using FakeAI for development (USE_FAKE_AI=true)")
        return FakeAI()
    else:
        logger.info("🤖 Using Claude AI (USE_FAKE_AI=false)")
        try:
            return ClaudeAI()
        except Exception as e:
            logger.error(f"Failed to initialize ClaudeAI: {e}")
            logger.warning("⚠️  Falling back to FakeAI due to initialization error")
            return FakeAI()


def get_ai_info(ai_instance) -> dict:
    """
    Get information about the AI instance.

    Args:
        ai_instance: AI instance to inspect

    Returns:
        Dictionary with AI information
    """
    return {
        'model_name': getattr(ai_instance, 'model_name', 'Unknown'),
        'is_fake': isinstance(ai_instance, FakeAI),
        'is_claude': isinstance(ai_instance, ClaudeAI),
        'has_style_detection': hasattr(ai_instance, 'style_detector'),
        'has_cost_tracking': hasattr(ai_instance, 'cost_tracker')
    }
