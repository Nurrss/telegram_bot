"""
Cost tracking for Claude API usage.
Monitors token consumption and calculates costs based on Anthropic pricing.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from utils.logger import logger


class CostTracker:
    """
    Track Claude API costs and token usage.

    Pricing for claude-3-5-sonnet-20241022:
    - Input: $3.00 per million tokens
    - Output: $15.00 per million tokens
    """

    # Pricing per million tokens (in USD)
    PRICING = {
        'claude-3-5-sonnet-20241022': {
            'input': 3.00,
            'output': 15.00
        },
        'claude-3-opus-20240229': {
            'input': 15.00,
            'output': 75.00
        },
        'claude-3-sonnet-20240229': {
            'input': 3.00,
            'output': 15.00
        },
        'claude-3-haiku-20240307': {
            'input': 0.25,
            'output': 1.25
        }
    }

    def __init__(self, storage_path: str = 'data/cost_tracking.json'):
        """
        Initialize cost tracker.

        Args:
            storage_path: Path to JSON file for cost data storage
        """
        self.storage_path = storage_path
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        """
        Load cost tracking data from storage.

        Returns:
            Dictionary with cost tracking data
        """
        if not os.path.exists(self.storage_path):
            # Create directory if needed
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

            # Initialize empty data structure
            data = {
                'total_requests': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_cost': 0.0,
                'requests': [],
                'daily_stats': {},
                'monthly_stats': {}
            }
            self._save_data(data)
            return data

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cost data: {e}")
            return {
                'total_requests': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_cost': 0.0,
                'requests': [],
                'daily_stats': {},
                'monthly_stats': {}
            }

    def _save_data(self, data: Dict) -> None:
        """
        Save cost tracking data to storage.

        Args:
            data: Cost tracking data to save
        """
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving cost data: {e}")

    def track_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        user_id: int,
        request_type: str = 'general',
        elapsed_time: float = 0.0
    ) -> Dict:
        """
        Track a single API request.

        Args:
            model: Model name (e.g., 'claude-3-5-sonnet-20241022')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            user_id: User ID making the request
            request_type: Type of request (general, plan, tasks, etc.)
            elapsed_time: Request duration in seconds (optional)

        Returns:
            Dictionary with request cost information
        """
        # Calculate cost
        pricing = self.PRICING.get(model, self.PRICING['claude-3-5-sonnet-20241022'])
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        total_cost = input_cost + output_cost

        # Create request record
        timestamp = datetime.now().isoformat()
        date_key = datetime.now().strftime('%Y-%m-%d')
        month_key = datetime.now().strftime('%Y-%m')

        request_record = {
            'timestamp': timestamp,
            'model': model,
            'user_id': user_id,
            'request_type': request_type,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': round(input_cost, 6),
            'output_cost': round(output_cost, 6),
            'total_cost': round(total_cost, 6),
            'elapsed_time': round(elapsed_time, 3) if elapsed_time else 0.0
        }

        # Update totals
        self.data['total_requests'] += 1
        self.data['total_input_tokens'] += input_tokens
        self.data['total_output_tokens'] += output_tokens
        self.data['total_cost'] += total_cost

        # Add to requests list (keep last 1000 requests)
        self.data['requests'].append(request_record)
        if len(self.data['requests']) > 1000:
            self.data['requests'] = self.data['requests'][-1000:]

        # Update daily stats
        if date_key not in self.data['daily_stats']:
            self.data['daily_stats'][date_key] = {
                'requests': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'cost': 0.0
            }

        daily = self.data['daily_stats'][date_key]
        daily['requests'] += 1
        daily['input_tokens'] += input_tokens
        daily['output_tokens'] += output_tokens
        daily['cost'] += total_cost

        # Update monthly stats
        if month_key not in self.data['monthly_stats']:
            self.data['monthly_stats'][month_key] = {
                'requests': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'cost': 0.0
            }

        monthly = self.data['monthly_stats'][month_key]
        monthly['requests'] += 1
        monthly['input_tokens'] += input_tokens
        monthly['output_tokens'] += output_tokens
        monthly['cost'] += total_cost

        # Save updated data
        self._save_data(self.data)

        logger.info(
            f"API request tracked: {request_type} for user {user_id}, "
            f"tokens: {input_tokens}+{output_tokens}, cost: ${total_cost:.6f}"
        )

        return request_record

    def get_total_cost(self) -> float:
        """
        Get total cost across all requests.

        Returns:
            Total cost in USD
        """
        return round(self.data['total_cost'], 2)

    def get_daily_cost(self, date: Optional[str] = None) -> float:
        """
        Get cost for a specific day.

        Args:
            date: Date in 'YYYY-MM-DD' format (default: today)

        Returns:
            Daily cost in USD
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        daily = self.data['daily_stats'].get(date, {})
        return round(daily.get('cost', 0.0), 2)

    def get_monthly_cost(self, month: Optional[str] = None) -> float:
        """
        Get cost for a specific month.

        Args:
            month: Month in 'YYYY-MM' format (default: current month)

        Returns:
            Monthly cost in USD
        """
        if not month:
            month = datetime.now().strftime('%Y-%m')

        monthly = self.data['monthly_stats'].get(month, {})
        return round(monthly.get('cost', 0.0), 2)

    def get_user_cost(self, user_id: int, days: int = 30) -> Dict:
        """
        Get cost statistics for a specific user.

        Args:
            user_id: User ID
            days: Number of days to look back

        Returns:
            Dictionary with user cost stats
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        user_requests = [
            r for r in self.data['requests']
            if r['user_id'] == user_id and
            datetime.fromisoformat(r['timestamp']) >= cutoff_date
        ]

        if not user_requests:
            return {
                'user_id': user_id,
                'requests': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'total_cost': 0.0
            }

        total_input = sum(r['input_tokens'] for r in user_requests)
        total_output = sum(r['output_tokens'] for r in user_requests)
        total_cost = sum(r['total_cost'] for r in user_requests)

        return {
            'user_id': user_id,
            'requests': len(user_requests),
            'input_tokens': total_input,
            'output_tokens': total_output,
            'total_cost': round(total_cost, 2)
        }

    def get_summary(self) -> Dict:
        """
        Get comprehensive cost summary.

        Returns:
            Dictionary with cost statistics
        """
        today = datetime.now().strftime('%Y-%m-%d')
        this_month = datetime.now().strftime('%Y-%m')

        return {
            'total': {
                'requests': self.data['total_requests'],
                'input_tokens': self.data['total_input_tokens'],
                'output_tokens': self.data['total_output_tokens'],
                'total_tokens': self.data['total_input_tokens'] + self.data['total_output_tokens'],
                'cost': round(self.data['total_cost'], 2)
            },
            'today': self.data['daily_stats'].get(today, {
                'requests': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'cost': 0.0
            }),
            'this_month': self.data['monthly_stats'].get(this_month, {
                'requests': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'cost': 0.0
            }),
            'average_cost_per_request': round(
                self.data['total_cost'] / max(self.data['total_requests'], 1),
                4
            )
        }

    def get_cost_alert_status(self, daily_limit: float = 5.0, monthly_limit: float = 50.0) -> Dict:
        """
        Check if costs are approaching limits.

        Args:
            daily_limit: Daily cost limit in USD
            monthly_limit: Monthly cost limit in USD

        Returns:
            Dictionary with alert status
        """
        daily_cost = self.get_daily_cost()
        monthly_cost = self.get_monthly_cost()

        daily_percentage = (daily_cost / daily_limit) * 100 if daily_limit > 0 else 0
        monthly_percentage = (monthly_cost / monthly_limit) * 100 if monthly_limit > 0 else 0

        return {
            'daily': {
                'cost': daily_cost,
                'limit': daily_limit,
                'percentage': round(daily_percentage, 1),
                'alert': daily_percentage >= 80
            },
            'monthly': {
                'cost': monthly_cost,
                'limit': monthly_limit,
                'percentage': round(monthly_percentage, 1),
                'alert': monthly_percentage >= 80
            }
        }

    def reset_stats(self) -> None:
        """
        Reset all cost tracking statistics.
        WARNING: This deletes all historical data.
        """
        logger.warning("Resetting all cost tracking data")

        self.data = {
            'total_requests': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_cost': 0.0,
            'requests': [],
            'daily_stats': {},
            'monthly_stats': {}
        }

        self._save_data(self.data)
