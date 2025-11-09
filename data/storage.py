"""
Storage Module
Handles local database or data file operations.
"""

import json
from pathlib import Path
from typing import Any, Optional


class Storage:
    """
    Manages data persistence for user information and plans.
    Currently uses JSON file storage, can be extended to use databases.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize storage.

        Args:
            data_dir: Directory for storing data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def save_user_data(self, user_id: int, data: dict) -> bool:
        """
        Save user data.

        Args:
            user_id: Telegram user ID
            data: User data dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.data_dir / f"user_{user_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False

    def load_user_data(self, user_id: int) -> Optional[dict]:
        """
        Load user data.

        Args:
            user_id: Telegram user ID

        Returns:
            User data dictionary or None if not found
        """
        try:
            file_path = self.data_dir / f"user_{user_id}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading user data: {e}")
            return None

    def delete_user_data(self, user_id: int) -> bool:
        """
        Delete user data.

        Args:
            user_id: Telegram user ID

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.data_dir / f"user_{user_id}.json"
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting user data: {e}")
            return False
