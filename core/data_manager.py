"""
Data Manager for HydraPing.
High-level API that encapsulates all data operations including:
- Settings persistence
- Hydration logging
- Analytics
- Log rotation
Simplified single-user version.
"""

from datetime import datetime, timedelta
from pathlib import Path
from core.config import (
    get_database_path,
    DEFAULT_DAILY_GOAL,
    DEFAULT_REMINDER_INTERVAL,
    DEFAULT_THEME,
    DEFAULT_DRINK_AMOUNT,
    LOG_RETENTION_DAYS
)
from db_schema import Database


class DataManager:
    """
    Centralized data management layer.
    Provides clean API for all persistence operations.
    Single-user simplified version.
    """
    
    def __init__(self):
        """Initialize data manager with database in user config directory."""
        db_path = get_database_path()
        print(f"[DataManager] Using database: {db_path}")
        
        self.db = Database(str(db_path))
        self._settings_cache = None
        self._cache_timestamp = 0
        self._cache_ttl = 5  # Cache settings for 5 seconds
        self._perform_maintenance()
    
    def _perform_maintenance(self):
        """Perform database maintenance tasks."""
        self._rotate_old_logs()
    
    def _rotate_old_logs(self):
        """Delete hydration logs older than LOG_RETENTION_DAYS."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
            
            cursor.execute('''
                DELETE FROM hydration_logs
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted > 0:
                print(f"[DataManager] Rotated {deleted} old log entries (older than {LOG_RETENTION_DAYS} days)")
        except Exception as e:
            print(f"[DataManager] Log rotation error: {e}")
    
    def get_settings(self):
        """
        Get user settings with defaults.
        Returns dict with all settings.
        """
        # Check cache first
        import time
        current_time = time.time()
        if self._settings_cache and (current_time - self._cache_timestamp) < self._cache_ttl:
            return self._settings_cache.copy()
        
        settings = self.db.get_user_settings()
        
        if settings is None:
            settings = {
                'daily_goal_ml': DEFAULT_DAILY_GOAL,
                'reminder_interval_minutes': DEFAULT_REMINDER_INTERVAL,
                'chime_enabled': True,
                'default_sip_ml': DEFAULT_DRINK_AMOUNT,
                'auto_start': False,
                'theme': DEFAULT_THEME,
                'window_shape': 'rectangular'
            }
        
        # Update cache
        self._settings_cache = settings.copy()
        self._cache_timestamp = time.time()
        
        return settings
    
    def update_settings(self, **kwargs):
        """
        Update user settings.
        Accepts: daily_goal_ml, reminder_interval_minutes, chime_enabled,
                default_sip_ml, auto_start, theme, window_shape, etc.
        """
        self.db.update_user_settings(**kwargs)
        
        # Invalidate cache
        self._settings_cache = None
        self._cache_timestamp = 0
    
    def get_setting(self, key, default=None):
        """Get a single setting value."""
        settings = self.get_settings()
        return settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set a single setting value."""
        self.update_settings(**{key: value})
    
    def log_water(self, amount_ml):
        """Log water intake."""
        self.db.log_water_intake(amount_ml)
    
    def get_today_total(self):
        """Get total water intake for today."""
        return self.db.get_today_intake()
    
    def get_recent_logs(self, limit=50, days=None):
        """
        Get recent hydration logs.
        If days is specified, get logs from the last N days instead of using limit.
        """
        if days is not None:
            cutoff_date = datetime.now() - timedelta(days=days)
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, amount_ml, timestamp
                FROM hydration_logs
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            ''', (cutoff_date,))
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'id': row[0],
                    'amount': row[1],
                    'timestamp': datetime.fromisoformat(row[2]) if isinstance(row[2], str) else row[2]
                })
            conn.close()
            return logs
        
        return self.db.get_recent_logs(limit)
    
    def get_today_logs(self):
        """Get all logs for today."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, amount_ml, timestamp
            FROM hydration_logs
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        ''', (today,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'id': row[0],
                'amount': row[1],
                'timestamp': datetime.fromisoformat(row[2]) if isinstance(row[2], str) else row[2]
            })
        conn.close()
        return logs
    
    def delete_log(self, log_id):
        """Delete a specific log entry."""
        self.db.delete_log_entry(log_id)
    
    def reset_today(self):
        """Reset today's water intake."""
        deleted = self.db.reset_today_intake()
        return deleted
    
    def get_daily_stats(self, days=7):
        """Get daily intake stats for the last N days."""
        return self.db.get_daily_stats(days=days)
    
    def get_database_path(self):
        """Get the path to the database file."""
        return Path(self.db.db_file)
    
    def close(self):
        """Close database connection (if needed)."""
        pass


_data_manager_instance = None


def get_data_manager():
    """
    Get singleton DataManager instance.
    Use this function throughout the app to access the data manager.
    """
    global _data_manager_instance
    if _data_manager_instance is None:
        _data_manager_instance = DataManager()
    return _data_manager_instance


def reset_data_manager():
    """Reset the singleton instance (useful for testing)."""
    global _data_manager_instance
    _data_manager_instance = None
