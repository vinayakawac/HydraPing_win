"""
Pattern Analyzer - AI-powered hydration pattern detection and prediction
Analyzes drinking patterns to predict when user will need water next
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import statistics


class PatternAnalyzer:
    """Analyzes hydration patterns and predicts future needs"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self._prediction_cache = None
        self._cache_timestamp = None
        self._cache_duration = 300  # 5 minutes
    
    def get_drinking_intervals(self, days: int = 7) -> List[float]:
        """Get intervals between drinks in minutes for the past N days"""
        logs = self.data_manager.get_recent_logs(days=days)
        
        if len(logs) < 2:
            return []
        
        intervals = []
        for i in range(1, len(logs)):
            time_diff = (logs[i]['timestamp'] - logs[i-1]['timestamp']).total_seconds() / 60
            # Filter out unrealistic intervals (less than 1 min or more than 8 hours)
            if 1 <= time_diff <= 480:
                intervals.append(time_diff)
        
        return intervals
    
    def get_time_of_day_patterns(self, days: int = 14) -> Dict[int, List[float]]:
        """Analyze drinking patterns by hour of day"""
        logs = self.data_manager.get_recent_logs(days=days)
        
        # Group by hour
        hourly_data = {hour: [] for hour in range(24)}
        
        for log in logs:
            hour = log['timestamp'].hour
            hourly_data[hour].append(log['amount'])
        
        return hourly_data
    
    def predict_next_drink_time(self) -> Optional[Tuple[datetime, float, str]]:
        """
        Predict when user will likely need water next
        Returns: (predicted_time, confidence, reason)
        """
        # Check cache
        if self._prediction_cache and self._cache_timestamp:
            if (datetime.now() - self._cache_timestamp).total_seconds() < self._cache_duration:
                return self._prediction_cache
        
        # Get recent intervals
        intervals = self.get_drinking_intervals(days=7)
        
        if len(intervals) < 3:
            # Not enough data
            return None
        
        # Calculate statistics
        avg_interval = statistics.mean(intervals)
        median_interval = statistics.median(intervals)
        std_dev = statistics.stdev(intervals) if len(intervals) > 1 else 0
        
        # Get last drink time
        recent_logs = self.data_manager.get_recent_logs(days=1)
        if not recent_logs:
            return None
        
        last_drink = recent_logs[-1]['timestamp']
        time_since_last = (datetime.now() - last_drink).total_seconds() / 60
        
        # Choose prediction method based on consistency
        consistency = 1 - (std_dev / avg_interval) if avg_interval > 0 else 0
        consistency = max(0, min(1, consistency))
        
        # Use median for more stable predictions
        predicted_interval = median_interval
        
        # Time-of-day adjustment
        current_hour = datetime.now().hour
        hourly_patterns = self.get_time_of_day_patterns(days=14)
        
        # Check if current hour typically has more/less activity
        current_hour_drinks = len(hourly_patterns.get(current_hour, []))
        avg_hour_drinks = sum(len(drinks) for drinks in hourly_patterns.values()) / 24
        
        if avg_hour_drinks > 0:
            hour_factor = current_hour_drinks / avg_hour_drinks
            # Adjust prediction based on typical activity for this hour
            if hour_factor > 1.2:
                predicted_interval *= 0.85  # Drink sooner if active hour
            elif hour_factor < 0.8:
                predicted_interval *= 1.15  # Can wait longer if slow hour
        
        # Calculate predicted time
        minutes_until = predicted_interval - time_since_last
        predicted_time = datetime.now() + timedelta(minutes=minutes_until)
        
        # Confidence calculation
        confidence = consistency * 0.7 + (0.3 if len(intervals) > 10 else 0.15)
        confidence = max(0.3, min(0.95, confidence))
        
        # Generate reason
        if consistency > 0.7:
            reason = f"Based on your consistent pattern of drinking every {int(predicted_interval)} minutes"
        elif len(intervals) > 20:
            reason = f"Based on {len(intervals)} recent drinks, averaging {int(avg_interval)} minutes"
        else:
            reason = f"Early prediction based on {len(intervals)} recent drinks"
        
        result = (predicted_time, confidence, reason)
        
        # Cache result
        self._prediction_cache = result
        self._cache_timestamp = datetime.now()
        
        return result
    
    def get_hydration_velocity(self) -> Optional[float]:
        """Calculate current hydration rate (ml per hour)"""
        logs = self.data_manager.get_recent_logs(days=1)
        
        if len(logs) < 2:
            return None
        
        total_amount = sum(log['amount'] for log in logs)
        time_span = (logs[-1]['timestamp'] - logs[0]['timestamp']).total_seconds() / 3600
        
        if time_span < 0.5:  # Less than 30 minutes of data
            return None
        
        return total_amount / time_span
    
    def is_ahead_of_schedule(self) -> Optional[bool]:
        """Determine if user is ahead or behind their typical pace"""
        settings = self.data_manager.get_settings()
        daily_goal = settings.get('daily_goal', 2000)
        
        logs = self.data_manager.get_today_logs()
        current_amount = sum(log['amount'] for log in logs)
        
        # Calculate expected amount based on time of day
        now = datetime.now()
        seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        
        # Assume 16 active hours (8am to midnight)
        active_start = 8 * 3600  # 8 AM
        active_end = 24 * 3600   # Midnight
        
        if seconds_since_midnight < active_start:
            # Before active hours
            expected_amount = 0
        elif seconds_since_midnight > active_end:
            # After active hours
            expected_amount = daily_goal
        else:
            # During active hours
            progress = (seconds_since_midnight - active_start) / (active_end - active_start)
            expected_amount = daily_goal * progress
        
        if expected_amount == 0:
            return None
        
        return current_amount >= expected_amount * 0.9  # 10% tolerance
    
    def get_smart_reminder_delay(self, base_interval: int) -> int:
        """
        Adjust reminder interval based on patterns and current state
        Returns: adjusted interval in minutes
        """
        # Get prediction
        prediction = self.predict_next_drink_time()
        
        if not prediction:
            return base_interval
        
        predicted_time, confidence, _ = prediction
        minutes_until = (predicted_time - datetime.now()).total_seconds() / 60
        
        # If high confidence and prediction is soon, align reminder
        if confidence > 0.6 and 0 < minutes_until < base_interval * 1.5:
            return max(5, int(minutes_until * 0.8))  # Remind slightly before predicted time
        
        # Check if ahead of schedule
        ahead = self.is_ahead_of_schedule()
        
        if ahead is True:
            # User is doing well, can relax reminders slightly
            return int(base_interval * 1.2)
        elif ahead is False:
            # User is behind, increase reminder frequency
            return int(base_interval * 0.8)
        
        return base_interval
    
    def get_insights(self) -> Dict[str, any]:
        """Get comprehensive hydration insights"""
        intervals = self.get_drinking_intervals(days=7)
        velocity = self.get_hydration_velocity()
        ahead = self.is_ahead_of_schedule()
        prediction = self.predict_next_drink_time()
        
        insights = {
            'average_interval': statistics.mean(intervals) if intervals else None,
            'consistency': 1 - (statistics.stdev(intervals) / statistics.mean(intervals)) if len(intervals) > 1 and statistics.mean(intervals) > 0 else None,
            'hydration_velocity': velocity,
            'ahead_of_schedule': ahead,
            'prediction': prediction,
            'total_drinks_week': len(intervals) + 1 if intervals else 0
        }
        
        return insights
