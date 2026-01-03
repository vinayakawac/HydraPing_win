"""
Database schema and operations for HydraPing.
Handles all SQLite database interactions.
Simplified single-user version without authentication.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


class Database:
    """SQLite database wrapper for HydraPing."""
    
    def __init__(self, db_file):
        """Initialize database connection and create tables if needed."""
        self.db_file = db_file
        Path(db_file).parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
    
    def get_connection(self):
        """Get a new database connection."""
        return sqlite3.connect(self.db_file)
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Single-user settings table (no user_id needed)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                daily_goal_ml INTEGER DEFAULT 2000,
                reminder_interval_minutes INTEGER DEFAULT 30,
                chime_enabled INTEGER DEFAULT 1,
                default_sip_ml INTEGER DEFAULT 250,
                auto_start INTEGER DEFAULT 0,
                theme TEXT DEFAULT 'Dark Glassmorphic',
                custom_sound_path TEXT,
                loop_alert_sound INTEGER DEFAULT 0,
                sleep_start_hour INTEGER DEFAULT 22,
                sleep_end_hour INTEGER DEFAULT 7,
                bedtime_warning_enabled INTEGER DEFAULT 1,
                snooze_duration_minutes INTEGER DEFAULT 5,
                window_shape TEXT DEFAULT 'rectangular',
                overlay_x INTEGER,
                overlay_y INTEGER
            )
        ''')
        
        # Hydration logs table (no user_id needed)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hydration_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount_ml INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_logs_timestamp 
            ON hydration_logs(timestamp)
        ''')
        
        self._migrate_schema(cursor)
        
        # Initialize settings if not exists
        cursor.execute('INSERT OR IGNORE INTO user_settings (id) VALUES (1)')
        
        conn.commit()
        conn.close()
    
    
    def _migrate_schema(self, cursor):
        """Migrate existing database schema to add missing columns and handle old schema."""
        try:
            # Check if old users table exists and migrate data
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if cursor.fetchone():
                print("[Database] Detected old multi-user schema, migrating to single-user...")
                
                # Store old settings values before dropping
                try:
                    cursor.execute("SELECT daily_goal_ml, reminder_interval_minutes, chime_enabled, default_sip_ml, auto_start, theme, custom_sound_path, loop_alert_sound, sleep_start_hour, sleep_end_hour, bedtime_warning_enabled, snooze_duration_minutes, window_shape FROM user_settings LIMIT 1")
                    old_settings = cursor.fetchone()
                except:
                    old_settings = None
                
                # Drop old tables
                cursor.execute('DROP TABLE IF EXISTS users')
                cursor.execute('DROP TABLE IF EXISTS user_settings')
                cursor.execute('DROP INDEX IF EXISTS idx_logs_user_timestamp')
                
                # Recreate tables with new schema (without user_id)
                cursor.execute('''
                    CREATE TABLE user_settings (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        daily_goal_ml INTEGER DEFAULT 2000,
                        reminder_interval_minutes INTEGER DEFAULT 30,
                        chime_enabled INTEGER DEFAULT 1,
                        default_sip_ml INTEGER DEFAULT 250,
                        auto_start INTEGER DEFAULT 0,
                        theme TEXT DEFAULT 'Dark Glassmorphic',
                        custom_sound_path TEXT,
                        loop_alert_sound INTEGER DEFAULT 0,
                        sleep_start_hour INTEGER DEFAULT 22,
                        sleep_end_hour INTEGER DEFAULT 7,
                        bedtime_warning_enabled INTEGER DEFAULT 1,
                        snooze_duration_minutes INTEGER DEFAULT 5,
                        window_shape TEXT DEFAULT 'rectangular',
                        overlay_x INTEGER,
                        overlay_y INTEGER
                    )
                ''')
                
                # Restore old settings if they existed
                if old_settings:
                    cursor.execute('''
                        INSERT INTO user_settings (id, daily_goal_ml, reminder_interval_minutes, chime_enabled, default_sip_ml, auto_start, theme, custom_sound_path, loop_alert_sound, sleep_start_hour, sleep_end_hour, bedtime_warning_enabled, snooze_duration_minutes, window_shape)
                        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', old_settings)
                else:
                    cursor.execute('INSERT INTO user_settings (id) VALUES (1)')
                
                # Migrate hydration logs (remove user_id column)
                try:
                    cursor.execute('ALTER TABLE hydration_logs RENAME TO hydration_logs_old')
                    cursor.execute('''
                        CREATE TABLE hydration_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            amount_ml INTEGER NOT NULL,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    cursor.execute('INSERT INTO hydration_logs (id, amount_ml, timestamp) SELECT id, amount_ml, timestamp FROM hydration_logs_old')
                    cursor.execute('DROP TABLE hydration_logs_old')
                    cursor.execute('CREATE INDEX idx_logs_timestamp ON hydration_logs(timestamp)')
                    print("[Database] Migration complete!")
                except:
                    pass
                
                return
            
            # Normal migrations for existing single-user schema
            cursor.execute("PRAGMA table_info(user_settings)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'chime_enabled' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN chime_enabled INTEGER DEFAULT 1')
            
            if 'default_sip_ml' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN default_sip_ml INTEGER DEFAULT 250')
            
            if 'auto_start' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN auto_start INTEGER DEFAULT 0')
            
            if 'theme' not in columns:
                cursor.execute("ALTER TABLE user_settings ADD COLUMN theme TEXT DEFAULT 'Dark Glassmorphic'")
            
            if 'custom_sound_path' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN custom_sound_path TEXT')
            
            if 'loop_alert_sound' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN loop_alert_sound INTEGER DEFAULT 0')
            
            if 'sleep_start_hour' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN sleep_start_hour INTEGER DEFAULT 22')
            
            if 'sleep_end_hour' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN sleep_end_hour INTEGER DEFAULT 7')
            
            if 'bedtime_warning_enabled' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN bedtime_warning_enabled INTEGER DEFAULT 1')
            
            if 'snooze_duration_minutes' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN snooze_duration_minutes INTEGER DEFAULT 5')
            
            if 'window_shape' not in columns:
                cursor.execute("ALTER TABLE user_settings ADD COLUMN window_shape TEXT DEFAULT 'rectangular'")
            
            if 'overlay_x' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN overlay_x INTEGER')
            
            if 'overlay_y' not in columns:
                cursor.execute('ALTER TABLE user_settings ADD COLUMN overlay_y INTEGER')
        except Exception as e:
            print(f"[Database] Schema migration note: {e}")
    
    
    def get_user_settings(self):
        """Get user settings."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT daily_goal_ml, reminder_interval_minutes, chime_enabled,
                   default_sip_ml, auto_start, theme, custom_sound_path, loop_alert_sound,
                   sleep_start_hour, sleep_end_hour, bedtime_warning_enabled, snooze_duration_minutes,
                   window_shape, overlay_x, overlay_y
            FROM user_settings
            WHERE id = 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'daily_goal_ml': row[0],
                'reminder_interval_minutes': row[1],
                'chime_enabled': bool(row[2]),
                'default_sip_ml': row[3],
                'auto_start': bool(row[4]),
                'theme': row[5],
                'custom_sound_path': row[6],
                'loop_alert_sound': bool(row[7]),
                'sleep_start_hour': row[8],
                'sleep_end_hour': row[9],
                'bedtime_warning_enabled': bool(row[10]),
                'snooze_duration_minutes': row[11],
                'window_shape': row[12] if len(row) > 12 else 'rectangular',
                'overlay_x': row[13] if len(row) > 13 else None,
                'overlay_y': row[14] if len(row) > 14 else None
            }
        return None
    
    def update_user_settings(self, **kwargs):
        """Update user settings."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            set_clauses.append(f"{key} = ?")
            if isinstance(value, bool):
                value = int(value)
            values.append(value)
        
        if set_clauses:
            query = f'''
                UPDATE user_settings
                SET {', '.join(set_clauses)}
                WHERE id = 1
            '''
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
    
    def log_water_intake(self, amount_ml):
        """Log water intake."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO hydration_logs (amount_ml)
            VALUES (?)
        ''', (amount_ml,))
        
        conn.commit()
        conn.close()
    
    def get_today_intake(self):
        """Get total water intake for today."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        cursor.execute('''
            SELECT COALESCE(SUM(amount_ml), 0)
            FROM hydration_logs
            WHERE timestamp >= ?
        ''', (today_start,))
        
        total = cursor.fetchone()[0]
        conn.close()
        
        return total
    
    def get_recent_logs(self, limit=50):
        """Get recent hydration logs."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, amount_ml, timestamp
            FROM hydration_logs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        logs = [{'id': row[0], 'amount_ml': row[1], 'timestamp': row[2]} 
                for row in cursor.fetchall()]
        
        conn.close()
        return logs
    
    def delete_log_entry(self, log_id):
        """Delete a specific log entry."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM hydration_logs WHERE id = ?', (log_id,))
        
        conn.commit()
        conn.close()
    
    def reset_today_intake(self, user_id):
        """Reset today's intake by deleting today's logs."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        cursor.execute('''
            DELETE FROM hydration_logs
            WHERE user_id = ? AND timestamp >= ?
        ''', (user_id, today_start))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_daily_stats(self, user_id, days=7):
        """Get daily intake stats for the last N days."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT DATE(timestamp) as date, SUM(amount_ml) as total
            FROM hydration_logs
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        ''', (user_id, start_date))
        
        stats = [{'date': row[0], 'total_ml': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        return stats
    
    def get_weekly_stats(self, user_id):
        """Get weekly hydration statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        week_start = datetime.now() - timedelta(days=7)
        
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT DATE(timestamp)) as days_logged,
                SUM(amount_ml) as total_ml,
                AVG(amount_ml) as avg_per_log
            FROM hydration_logs
            WHERE user_id = ? AND timestamp >= ?
        ''', (user_id, week_start))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'days_logged': row[0],
                'total_ml': row[1] or 0,
                'avg_per_log': row[2] or 0
            }
        return {'days_logged': 0, 'total_ml': 0, 'avg_per_log': 0}
    
    def get_hourly_distribution(self, user_id, days=7):
        """Get hourly distribution of water intake."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                CAST(strftime('%H', timestamp) AS INTEGER) as hour,
                SUM(amount_ml) as total
            FROM hydration_logs
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY hour
            ORDER BY hour
        ''', (user_id, start_date))
        
        distribution = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return distribution
    
    def get_hourly_distribution_matrix(self, user_id, days=7):
        """Get hourly distribution matrix for heatmap."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                DATE(timestamp) as date,
                CAST(strftime('%H', timestamp) AS INTEGER) as hour,
                SUM(amount_ml) as total
            FROM hydration_logs
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY date, hour
            ORDER BY date, hour
        ''', (user_id, start_date))
        
        matrix = {}
        for row in cursor.fetchall():
            date, hour, total = row
            if date not in matrix:
                matrix[date] = {}
            matrix[date][hour] = total
        
        conn.close()
        return matrix
    
    def get_today_hourly_breakdown(self, user_id):
        """Get today's intake broken down by hour."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        cursor.execute('''
            SELECT 
                CAST(strftime('%H', timestamp) AS INTEGER) as hour,
                SUM(amount_ml) as total
            FROM hydration_logs
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY hour
            ORDER BY hour
        ''', (user_id, today_start))
        
        breakdown = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return breakdown
    
    def get_streak_count(self, user_id):
        """Get current streak of days meeting daily goal."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT daily_goal_ml FROM user_settings WHERE user_id = ?', (user_id,))
        goal = cursor.fetchone()
        if not goal:
            conn.close()
            return 0
        
        daily_goal = goal[0]
        
        start_date = datetime.now() - timedelta(days=30)
        cursor.execute('''
            SELECT DATE(timestamp) as date, SUM(amount_ml) as total
            FROM hydration_logs
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        ''', (user_id, start_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        streak = 0
        current_date = datetime.now().date()
        
        for row in rows:
            log_date = datetime.strptime(row[0], '%Y-%m-%d').date()
            total = row[1]
            expected_date = current_date - timedelta(days=streak)
            
            if log_date == expected_date and total >= daily_goal:
                streak += 1
            else:
                break
        
        return streak
    
    def get_achievement_data(self, user_id):
        """Get data for achievement calculations."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM hydration_logs WHERE user_id = ?', (user_id,))
        total_logs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COALESCE(SUM(amount_ml), 0) FROM hydration_logs WHERE user_id = ?', (user_id,))
        total_ml = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(DISTINCT DATE(timestamp))
            FROM hydration_logs
            WHERE user_id = ?
        ''', (user_id,))
        days_active = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_logs': total_logs,
            'total_ml': total_ml,
            'days_active': days_active
        }
    
    def get_weekly_comparison(self, user_id):
        """Compare this week vs last week."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        this_week_start = datetime.now() - timedelta(days=7)
        last_week_start = datetime.now() - timedelta(days=14)
        
        cursor.execute('''
            SELECT COALESCE(SUM(amount_ml), 0)
            FROM hydration_logs
            WHERE user_id = ? AND timestamp >= ?
        ''', (user_id, this_week_start))
        this_week = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COALESCE(SUM(amount_ml), 0)
            FROM hydration_logs
            WHERE user_id = ? AND timestamp >= ? AND timestamp < ?
        ''', (user_id, last_week_start, this_week_start))
        last_week = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'this_week_ml': this_week,
            'last_week_ml': last_week
        }
    
    def export_logs_csv(self, user_id, filepath):
        """Export hydration logs to CSV file."""
        import csv
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT amount_ml, timestamp
            FROM hydration_logs
            WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Amount (ml)', 'Timestamp'])
                writer.writerows(rows)
            return True, f"Exported {len(rows)} logs"
        except Exception as e:
            return False, str(e)
