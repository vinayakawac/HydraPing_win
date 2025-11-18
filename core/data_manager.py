"""
Data Manager for HydraPing.
High-level API that encapsulates all data operations including:
- User management
- Settings persistence
- Hydration logging
- Analytics
- Log rotation
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
    """
    
    def __init__(self, user=None):
        """Initialize data manager with database in user config directory."""
        db_path = get_database_path()
        print(f"[DataManager] Using database: {db_path}")
        
        self.db = Database(str(db_path))
        self.user = user
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
    
    def get_or_create_default_user(self):
        """
        Get or create default user for standalone app.
        Returns user dict with id and email.
        """
        try:
            success, result = self.db.authenticate_user('default@hydra.local', 'default123')
            if success:
                return result
        except:
            pass
        
        try:
            success, user_id = self.db.create_user('default@hydra.local', 'default123')
            if success:
                return {'id': user_id, 'email': 'default@hydra.local'}
        except:
            pass
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email FROM users LIMIT 1')
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {'id': user[0], 'email': user[1]}
        
        timestamp = int(datetime.now().timestamp())
        success, user_id = self.db.create_user(f'user{timestamp}@hydra.local', 'default')
        if success:
            return {'id': user_id, 'email': f'user{timestamp}@hydra.local'}
        
        raise Exception("Failed to create or retrieve user")
    
    def create_user(self, email, password):
        """Create new user account."""
        return self.db.create_user(email, password)
    
    def authenticate_user(self, email, password):
        """Authenticate user credentials."""
        return self.db.authenticate_user(email, password)
    
    def set_user(self, user):
        """Set the current user context."""
        self.user = user
    
    def get_settings(self):
        """
        Get user settings with defaults.
        Returns dict with all settings.
        """
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        
        settings = self.db.get_user_settings(self.user['id'])
        
        if settings is None:
            return {
                'daily_goal_ml': DEFAULT_DAILY_GOAL,
                'reminder_interval_minutes': DEFAULT_REMINDER_INTERVAL,
                'chime_enabled': True,
                'default_sip_ml': DEFAULT_DRINK_AMOUNT,
                'auto_start': False,
                'theme': DEFAULT_THEME
            }
        
        return settings
    
    def update_settings(self, **kwargs):
        """
        Update user settings.
        Accepts: daily_goal_ml, reminder_interval_minutes, chime_enabled,
                default_sip_ml, auto_start, theme
        """
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        
        self.db.update_user_settings(self.user['id'], **kwargs)
    
    def get_setting(self, key, default=None):
        """Get a single setting value."""
        settings = self.get_settings()
        return settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set a single setting value."""
        self.update_settings(**{key: value})
    
    def log_water(self, amount_ml):
        """Log water intake."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        self.db.log_water_intake(self.user['id'], amount_ml)
    
    def get_today_total(self):
        """Get total water intake for today."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.get_today_intake(self.user['id'])
    
    def get_recent_logs(self, limit=50):
        """Get recent hydration logs."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.get_recent_logs(self.user['id'], limit=limit)
    
    def delete_log(self, log_id):
        """Delete a specific log entry."""
        self.db.delete_log_entry(log_id)
    
    def reset_today(self):
        """Reset today's intake."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.reset_today_intake(self.user['id'])
    
    def get_daily_stats(self, days=7):
        """Get daily intake stats for the last N days."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.get_daily_stats(self.user['id'], days=days)
    
    def get_weekly_stats(self):
        """Get weekly hydration statistics."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.get_weekly_stats(self.user['id'])
    
    def get_hourly_distribution(self, days=7):
        """Get hourly distribution of water intake."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.get_hourly_distribution(self.user['id'], days=days)
    
    def get_hourly_matrix(self, days=7):
        """Get hourly distribution matrix for heatmap."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.get_hourly_distribution_matrix(self.user['id'], days=days)
    
    def get_today_hourly_breakdown(self):
        """Get today's intake broken down by hour."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.get_today_hourly_breakdown(self.user['id'])
    
    def get_streak(self):
        """Get current streak of days meeting daily goal."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.get_streak_count(self.user['id'])
    
    def get_achievement_data(self):
        """Get data for achievement calculations."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.get_achievement_data(self.user['id'])
    
    def get_weekly_comparison(self):
        """Compare this week vs last week."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.get_weekly_comparison(self.user['id'])
    
    def export_to_csv(self, filepath):
        """Export hydration logs to CSV file."""
        if not self.user:
            raise ValueError("No user context set. Call set_user() first.")
        return self.db.export_logs_csv(self.user['id'], filepath)
    
    def get_database_path(self):
        """Get the path to the database file."""
        return Path(self.db.db_file)
    
    def close(self):
        """Close database connection (if needed."""
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
