"""
Pattern Analyzer - AI-powered hydration pattern detection and prediction
Analyzes drinking patterns to predict when user will need water next
Enhanced with robust error handling, outlier detection, and fault tolerance
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import statistics
import logging


class PatternAnalyzer:
    """
    Analyzes hydration patterns and predicts future needs with robust error handling
    Features:
    - Outlier detection and removal
    - Multiple fallback prediction methods
    - Data quality validation
    - Comprehensive error handling
    - Smart caching with invalidation
    """
    
    # Configuration constants
    MIN_INTERVAL_MINUTES = 1
    MAX_INTERVAL_MINUTES = 480  # 8 hours
    MIN_SAMPLES_FOR_PREDICTION = 3
    MIN_SAMPLES_FOR_STDEV = 2
    OUTLIER_THRESHOLD_STDEV = 2.5  # Standard deviations for outlier detection
    CACHE_DURATION = 300  # 5 minutes
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self._prediction_cache = None
        self._cache_timestamp = None
        self._error_count = 0
        self._last_error_time = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _validate_timestamp(self, timestamp) -> bool:
        """Validate timestamp is reasonable"""
        try:
            if not isinstance(timestamp, datetime):
                return False
            # Check if timestamp is within reasonable range (not too old, not in future)
            now = datetime.now()
            if timestamp > now:
                return False
            if timestamp < (now - timedelta(days=365)):  # More than a year old
                return False
            return True
        except Exception:
            return False
    
    def _remove_outliers(self, data: List[float], threshold: float = None) -> List[float]:
        """
        Remove outliers using modified Z-score method
        Returns cleaned data with outliers removed
        """
        if len(data) < 3:
            return data
        
        try:
            threshold = threshold or self.OUTLIER_THRESHOLD_STDEV
            mean = statistics.mean(data)
            std_dev = statistics.stdev(data) if len(data) >= self.MIN_SAMPLES_FOR_STDEV else 0
            
            if std_dev == 0:
                return data
            
            # Calculate Z-scores and filter
            cleaned = [x for x in data if abs((x - mean) / std_dev) <= threshold]
            
            # Ensure we don't remove too much data
            if len(cleaned) >= max(3, len(data) * 0.5):
                return cleaned
            return data
            
        except Exception as e:
            self.logger.warning(f"Outlier removal failed: {e}")
            return data
    
    def get_drinking_intervals(self, days: int = 7) -> List[float]:
        """
        Get intervals between drinks in minutes for the past N days
        Enhanced with validation, outlier detection, and error handling
        """
        try:
            logs = self.data_manager.get_recent_logs(days=days)
            
            if not logs or len(logs) < 2:
                return []
            
            # Validate and filter logs
            valid_logs = []
            for log in logs:
                if self._validate_timestamp(log.get('timestamp')):
                    valid_logs.append(log)
            
            if len(valid_logs) < 2:
                return []
            
            # Calculate intervals
            intervals = []
            for i in range(1, len(valid_logs)):
                try:
                    time_diff = (valid_logs[i]['timestamp'] - valid_logs[i-1]['timestamp']).total_seconds() / 60
                    
                    # Filter realistic intervals
                    if self.MIN_INTERVAL_MINUTES <= time_diff <= self.MAX_INTERVAL_MINUTES:
                        intervals.append(time_diff)
                except (KeyError, TypeError, AttributeError) as e:
                    self.logger.warning(f"Skipping invalid log entry: {e}")
                    continue
            
            # Remove outliers for more accurate analysis
            if len(intervals) >= 5:
                intervals = self._remove_outliers(intervals)
            
            return intervals
            
        except Exception as e:
            self.logger.error(f"Error getting drinking intervals: {e}")
            self._record_error()
            return []
    
    def get_time_of_day_patterns(self, days: int = 14) -> Dict[int, List[float]]:
        """
        Analyze drinking patterns by hour of day with validation
        """
        try:
            logs = self.data_manager.get_recent_logs(days=days)
            
            # Initialize hourly data
            hourly_data = {hour: [] for hour in range(24)}
            
            if not logs:
                return hourly_data
            
            # Group by hour with validation
            for log in logs:
                try:
                    if not self._validate_timestamp(log.get('timestamp')):
                        continue
                    
                    hour = log['timestamp'].hour
                    amount = log.get('amount', 0)
                    
                    if 0 <= hour < 24 and amount > 0:
                        hourly_data[hour].append(amount)
                except (KeyError, TypeError, AttributeError, ValueError) as e:
                    self.logger.warning(f"Skipping invalid hourly log: {e}")
                    continue
            
            return hourly_data
            
        except Exception as e:
            self.logger.error(f"Error getting time-of-day patterns: {e}")
            self._record_error()
            return {hour: [] for hour in range(24)}
    
    def _record_error(self):
        """Record error occurrence for monitoring"""
        self._error_count += 1
        self._last_error_time = datetime.now()
    
    def _calculate_confidence(self, intervals: List[float], method: str = "consistency") -> float:
        """
        Calculate prediction confidence based on data quality
        Returns: confidence score between 0.0 and 1.0
        """
        try:
            if len(intervals) < self.MIN_SAMPLES_FOR_PREDICTION:
                return 0.0
            
            # Base confidence on sample size
            size_factor = min(1.0, len(intervals) / 20)  # Max confidence at 20+ samples
            
            # Consistency factor (lower std dev = higher confidence)
            if len(intervals) >= self.MIN_SAMPLES_FOR_STDEV:
                mean = statistics.mean(intervals)
                std_dev = statistics.stdev(intervals)
                
                if mean > 0:
                    consistency = 1 - min(1.0, std_dev / mean)
                else:
                    consistency = 0.0
            else:
                consistency = 0.5
            
            # Combine factors
            confidence = (size_factor * 0.4) + (consistency * 0.6)
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            self.logger.warning(f"Confidence calculation failed: {e}")
            return 0.3  # Default low confidence
    
    def predict_next_drink_time(self) -> Optional[Tuple[datetime, float, str]]:
        """
        Predict when user will likely need water next with robust error handling
        Returns: (predicted_time, confidence, reason) or None if prediction not possible
        
        Uses multiple fallback methods:
        1. Median-based prediction (most robust)
        2. Mean-based prediction (fallback)
        3. Recent interval prediction (last resort)
        """
        try:
            # Check cache
            if self._prediction_cache and self._cache_timestamp:
                cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
                if cache_age < self.CACHE_DURATION:
                    return self._prediction_cache
            
            # Get recent intervals with validation
            intervals = self.get_drinking_intervals(days=7)
            
            if len(intervals) < self.MIN_SAMPLES_FOR_PREDICTION:
                # Not enough data for prediction
                self.logger.info(f"Insufficient data: {len(intervals)} samples (need {self.MIN_SAMPLES_FOR_PREDICTION})")
                return None
            
            # Get last drink time with validation
            recent_logs = self.data_manager.get_recent_logs(days=1)
            if not recent_logs:
                self.logger.warning("No recent logs found")
                return None
            
            # Find the most recent valid log
            last_drink = None
            for log in reversed(recent_logs):
                if self._validate_timestamp(log.get('timestamp')):
                    last_drink = log['timestamp']
                    break
            
            if not last_drink:
                self.logger.warning("No valid timestamp in recent logs")
                return None
            
            time_since_last = (datetime.now() - last_drink).total_seconds() / 60
            
            # Validate time_since_last
            if time_since_last < 0 or time_since_last > self.MAX_INTERVAL_MINUTES * 2:
                self.logger.warning(f"Invalid time_since_last: {time_since_last}")
                return None
            
            # Calculate statistics with error handling
            try:
                median_interval = statistics.median(intervals)
                mean_interval = statistics.mean(intervals)
                
                if len(intervals) >= self.MIN_SAMPLES_FOR_STDEV:
                    std_dev = statistics.stdev(intervals)
                else:
                    std_dev = 0
                    
            except statistics.StatisticsError as e:
                self.logger.error(f"Statistics calculation failed: {e}")
                return None
            
            # Primary method: Median-based prediction (most robust against outliers)
            predicted_interval = median_interval
            prediction_method = "median"
            
            # Validate predicted interval
            if not (self.MIN_INTERVAL_MINUTES <= predicted_interval <= self.MAX_INTERVAL_MINUTES):
                # Fallback to mean if median is invalid
                if self.MIN_INTERVAL_MINUTES <= mean_interval <= self.MAX_INTERVAL_MINUTES:
                    predicted_interval = mean_interval
                    prediction_method = "mean"
                else:
                    # Last resort: use recent average
                    recent_intervals = intervals[-3:] if len(intervals) >= 3 else intervals
                    predicted_interval = statistics.mean(recent_intervals)
                    prediction_method = "recent"
            
            # Time-of-day adjustment with error handling
            try:
                current_hour = datetime.now().hour
                hourly_patterns = self.get_time_of_day_patterns(days=14)
                
                current_hour_drinks = len(hourly_patterns.get(current_hour, []))
                total_drinks = sum(len(drinks) for drinks in hourly_patterns.values())
                
                if total_drinks > 0:
                    avg_hour_drinks = total_drinks / 24
                    
                    if avg_hour_drinks > 0:
                        hour_factor = current_hour_drinks / avg_hour_drinks
                        
                        # Apply adjustment only if factor is reasonable
                        if 0.5 <= hour_factor <= 2.0:
                            if hour_factor > 1.2:
                                predicted_interval *= 0.85  # Drink sooner if active hour
                            elif hour_factor < 0.8:
                                predicted_interval *= 1.15  # Can wait longer if slow hour
            except Exception as e:
                self.logger.warning(f"Time-of-day adjustment failed: {e}")
                # Continue with unadjusted interval
            
            # Calculate predicted time
            minutes_until = max(1, predicted_interval - time_since_last)  # At least 1 minute
            predicted_time = datetime.now() + timedelta(minutes=minutes_until)
            
            # Calculate confidence
            confidence = self._calculate_confidence(intervals, method=prediction_method)
            
            # Adjust confidence based on time since last drink
            if time_since_last > predicted_interval * 1.5:
                confidence *= 0.8  # Lower confidence if overdue
            
            # Generate reason with method used
            if confidence > 0.7:
                reason = f"High confidence {prediction_method}-based prediction from {len(intervals)} samples"
            elif confidence > 0.5:
                reason = f"Moderate confidence based on {len(intervals)} recent drinks"
            else:
                reason = f"Early prediction from limited data ({len(intervals)} samples)"
            
            result = (predicted_time, confidence, reason)
            
            # Cache successful result
            self._prediction_cache = result
            self._cache_timestamp = datetime.now()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            self._record_error()
            self._prediction_cache = None
            return None
    
    def get_hydration_velocity(self) -> Optional[float]:
        """
        Calculate current hydration rate (ml per hour) with validation
        Returns: ml/hour or None if insufficient data
        """
        try:
            logs = self.data_manager.get_recent_logs(days=1)
            
            if not logs or len(logs) < 2:
                return None
            
            # Validate and sum amounts
            total_amount = 0
            valid_logs = []
            
            for log in logs:
                try:
                    if self._validate_timestamp(log.get('timestamp')):
                        amount = log.get('amount', 0)
                        if amount > 0:
                            total_amount += amount
                            valid_logs.append(log)
                except (KeyError, TypeError, ValueError):
                    continue
            
            if len(valid_logs) < 2:
                return None
            
            # Calculate time span
            time_span = (valid_logs[-1]['timestamp'] - valid_logs[0]['timestamp']).total_seconds() / 3600
            
            # Validate time span
            if time_span < 0.5:  # Less than 30 minutes of data
                return None
            
            if time_span > 24:  # More than a day (shouldn't happen but validate)
                return None
            
            # Calculate velocity
            velocity = total_amount / time_span
            
            # Sanity check (0-5000 ml/hour is reasonable)
            if 0 <= velocity <= 5000:
                return velocity
            
            return None
            
        except Exception as e:
            self.logger.error(f"Velocity calculation failed: {e}")
            self._record_error()
            return None
    
    def is_ahead_of_schedule(self) -> Optional[bool]:
        """
        Determine if user is ahead or behind their typical pace with error handling
        Returns: True if ahead, False if behind, None if cannot determine
        """
        try:
            settings = self.data_manager.get_settings()
            daily_goal = settings.get('daily_goal_ml', settings.get('daily_goal', 2000))
            
            # Validate daily goal
            if not isinstance(daily_goal, (int, float)) or daily_goal <= 0:
                self.logger.warning(f"Invalid daily goal: {daily_goal}")
                return None
            
            logs = self.data_manager.get_today_logs()
            
            if not logs:
                return False  # No water logged today = behind
            
            # Calculate current amount with validation
            current_amount = 0
            for log in logs:
                try:
                    amount = log.get('amount', 0)
                    if amount > 0:
                        current_amount += amount
                except (KeyError, TypeError, ValueError):
                    continue
            
            # Calculate expected amount based on time of day
            now = datetime.now()
            seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
            
            # Assume 16 active hours (8am to midnight)
            active_start = 8 * 3600  # 8 AM
            active_end = 24 * 3600   # Midnight
            
            if seconds_since_midnight < active_start:
                # Before active hours - any amount is ahead
                return current_amount > 0
            elif seconds_since_midnight > active_end:
                # After active hours - compare to full goal
                expected_amount = daily_goal
            else:
                # During active hours - calculate proportional progress
                progress = (seconds_since_midnight - active_start) / (active_end - active_start)
                expected_amount = daily_goal * progress
            
            if expected_amount <= 0:
                return None
            
            # 10% tolerance - ahead if within 90% of expected
            return current_amount >= expected_amount * 0.9
            
        except Exception as e:
            self.logger.error(f"Schedule check failed: {e}")
            self._record_error()
            return None
    
    def get_smart_reminder_delay(self, base_interval: int) -> int:
        """
        Adjust reminder interval based on patterns and current state with fallbacks
        Returns: adjusted interval in minutes (always returns a valid value)
        """
        try:
            # Validate base interval
            if not isinstance(base_interval, (int, float)) or base_interval < 5:
                base_interval = 30  # Default fallback
            
            # Get prediction with error handling
            try:
                prediction = self.predict_next_drink_time()
            except Exception as e:
                self.logger.warning(f"Prediction failed in smart delay: {e}")
                prediction = None
            
            if prediction:
                predicted_time, confidence, _ = prediction
                
                try:
                    minutes_until = (predicted_time - datetime.now()).total_seconds() / 60
                    
                    # If high confidence and prediction is soon, shorten reminder
                    # Never exceed base_interval - AI can only make it sooner
                    if confidence > 0.6 and 0 < minutes_until < base_interval:
                        adjusted = max(5, int(minutes_until * 0.8))
                        if 5 <= adjusted < base_interval:
                            return adjusted
                except (TypeError, AttributeError) as e:
                    self.logger.warning(f"Prediction time calculation failed: {e}")
            
            # Check if behind schedule - only shorten, never lengthen
            try:
                ahead = self.is_ahead_of_schedule()
                
                if ahead is False:
                    # User is behind, increase reminder frequency
                    adjusted = int(base_interval * 0.8)
                    return max(5, min(base_interval, adjusted))
            except Exception as e:
                self.logger.warning(f"Schedule check failed in smart delay: {e}")
            
            # Default: return base interval as-is
            return int(max(5, min(240, base_interval)))
            
        except Exception as e:
            self.logger.error(f"Smart delay calculation failed: {e}")
            self._record_error()
            # Always return a safe default
            return 30
    
    def get_insights(self) -> Dict[str, any]:
        """
        Get comprehensive hydration insights with complete error handling
        Always returns a dict, even if some insights fail
        """
        insights = {
            'average_interval': None,
            'consistency': None,
            'hydration_velocity': None,
            'ahead_of_schedule': None,
            'prediction': None,
            'total_drinks_week': 0,
            'error_count': self._error_count,
            'data_quality': 'unknown'
        }
        
        try:
            # Get intervals
            intervals = self.get_drinking_intervals(days=7)
            insights['total_drinks_week'] = len(intervals) + 1 if intervals else 0
            
            if intervals:
                try:
                    insights['average_interval'] = statistics.mean(intervals)
                    
                    if len(intervals) >= self.MIN_SAMPLES_FOR_STDEV:
                        mean = statistics.mean(intervals)
                        std_dev = statistics.stdev(intervals)
                        if mean > 0:
                            insights['consistency'] = 1 - min(1.0, std_dev / mean)
                except statistics.StatisticsError as e:
                    self.logger.warning(f"Interval statistics failed: {e}")
            
            # Get velocity
            try:
                insights['hydration_velocity'] = self.get_hydration_velocity()
            except Exception as e:
                self.logger.warning(f"Velocity calculation failed: {e}")
            
            # Check schedule
            try:
                insights['ahead_of_schedule'] = self.is_ahead_of_schedule()
            except Exception as e:
                self.logger.warning(f"Schedule check failed: {e}")
            
            # Get prediction
            try:
                insights['prediction'] = self.predict_next_drink_time()
            except Exception as e:
                self.logger.warning(f"Prediction failed: {e}")
            
            # Assess data quality
            if len(intervals) >= 20:
                insights['data_quality'] = 'excellent'
            elif len(intervals) >= 10:
                insights['data_quality'] = 'good'
            elif len(intervals) >= 5:
                insights['data_quality'] = 'fair'
            elif len(intervals) > 0:
                insights['data_quality'] = 'poor'
            else:
                insights['data_quality'] = 'insufficient'
                
        except Exception as e:
            self.logger.error(f"Insights gathering failed: {e}")
            self._record_error()
        
        return insights
    
    def reset_error_count(self):
        """Reset error counter (useful for testing/monitoring)"""
        self._error_count = 0
        self._last_error_time = None
    
    def invalidate_cache(self):
        """Manually invalidate prediction cache"""
        self._prediction_cache = None
        self._cache_timestamp = None
