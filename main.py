"""
HydraPing - Main Controller
MVC Controller + Event-driven architecture (tray removed)
"""

import sys
import os
import time
from datetime import datetime
from PySide6 import QtCore, QtWidgets, QtGui

from core.data_manager import get_data_manager
from core.auto_launch import is_auto_launch_enabled, enable_auto_launch, disable_auto_launch
from overlay_window import OverlayWindow
from settings_dialog import SettingsDialog


class HydraPingController(QtCore.QObject):
    """Main controller managing business logic, timers, and state coordination"""
    
    def __init__(self, data_manager, user):
        super().__init__()
        
        self.data_manager = data_manager
        self.user = user
        self.paused = False
        self.overlay_is_visible = False  # Start hidden
        
        # Tray signals removed
        
        # Load settings and state
        self.settings = self.data_manager.get_settings()
        self.today_intake = self.data_manager.get_today_total()
        
        # Create overlay window with theme (but don't show yet)
        theme = self.settings.get('theme', 'Dark Glassmorphic')
        overlay_x = self.settings.get('overlay_x')
        overlay_y = self.settings.get('overlay_y', 20)
        self._overlay = OverlayWindow(theme_name=theme)
        
        # Apply window shape from settings
        window_shape = self.settings.get('window_shape', 'rectangular')
        self._overlay.set_window_shape(window_shape, save_preference=True)
        
        if overlay_x is not None:
            self._overlay.move(overlay_x, overlay_y)
        self._overlay.update_consumption(self.today_intake, self.settings['daily_goal_ml'])
        
        # Connect overlay signals to handlers
        self._overlay.drink_now_clicked.connect(self._handle_drink_now)
        self._overlay.snooze_clicked.connect(self._handle_snooze)
        self._overlay.position_changed.connect(self._persist_overlay_position)
        self._overlay.close_requested.connect(self._handle_overlay_close)
        self._overlay.settings_requested.connect(self.open_settings)
        self._overlay.manual_drink_requested.connect(self._handle_manual_drink)
        
        # Fast timer for countdown display (1 second)
        self._countdown_timer = QtCore.QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._update_countdown)
        
        # Slow timer for system checks (60 seconds)
        self._system_check_timer = QtCore.QTimer(self)
        self._system_check_timer.setInterval(60000)  # 1 minute
        self._system_check_timer.timeout.connect(self._system_checks)
        
        # Tracking
        self.last_reminder_time = time.time()
        self.last_date = datetime.now().date()
        self._in_sleep_hours = False
        self._bedtime_warning_shown = False
        self._is_snoozed = False
        self._snooze_end_time = 0
        
        # Tray removed
        
    def start(self):
        """Start the application - show overlay"""
        self._countdown_timer.start()
        self._system_check_timer.start()
        self._system_checks()  # Run initial check
        self._overlay.show()
        self.overlay_is_visible = True
        
    def _update_countdown(self):
        """Fast timer: Update countdown display every second"""
        if not self.paused and not self._in_sleep_hours:
            # Check if snoozed
            if self._is_snoozed:
                snooze_remaining = int(self._snooze_end_time - time.time())
                if snooze_remaining <= 0:
                    # Snooze ended, trigger alert
                    self._is_snoozed = False
                    self._trigger_alert()
                    self.last_reminder_time = time.time()
                else:
                    # Show snooze countdown
                    mins = snooze_remaining // 60
                    secs = snooze_remaining % 60
                    self._overlay.update_countdown(f"Snoozed: {mins:02d}:{secs:02d}")
            else:
                interval = self.settings.get('reminder_interval_minutes', 45)
                elapsed_seconds = time.time() - self.last_reminder_time
                remaining_seconds = int((interval * 60) - elapsed_seconds)
                
                # Check if time to trigger alert
                if remaining_seconds <= 0:
                    self._trigger_alert()
                    self.last_reminder_time = time.time()
                    remaining_seconds = interval * 60
                
                # Update display
                if remaining_seconds > 0:
                    mins = remaining_seconds // 60
                    secs = remaining_seconds % 60
                    self._overlay.update_countdown(f"Next: {mins:02d}:{secs:02d}")
                else:
                    self._overlay.update_countdown("Next: 00:00")
        elif self._in_sleep_hours:
            self._overlay.update_countdown("Sleep Mode")
    
    def _system_checks(self):
        """Slow timer: Check date rollover, sleep hours, bedtime warning every minute"""
        # Check for daily reset (midnight rollover)
        current_date = datetime.now().date()
        if current_date != self.last_date:
            self.last_date = current_date
            self.data_manager.reset_today()
            self.today_intake = 0
            self._overlay.update_consumption(self.today_intake, self.settings['daily_goal_ml'])
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto-reset: New day detected, water intake reset to 0 ml")
        
        # Check if in sleep hours
        current_hour = datetime.now().hour
        sleep_start = self.settings.get('sleep_start_hour', 22)
        sleep_end = self.settings.get('sleep_end_hour', 7)
        
        if sleep_start < sleep_end:
            self._in_sleep_hours = sleep_start <= current_hour < sleep_end
        else:  # Sleep hours span midnight
            self._in_sleep_hours = current_hour >= sleep_start or current_hour < sleep_end
        
        # Check for bedtime warning (30 min before sleep)
        if self.settings.get('bedtime_warning_enabled', True):
            warning_hour = (sleep_start - 1) % 24
            warning_min_start = 30
            if current_hour == warning_hour and datetime.now().minute >= warning_min_start:
                if not self._bedtime_warning_shown and self.today_intake < self.settings['daily_goal_ml']:
                    self._show_bedtime_warning()
                    self._bedtime_warning_shown = True
            else:
                self._bedtime_warning_shown = False
                
    def _trigger_alert(self):
        """Trigger hydration alert"""
        custom_sound_path = self.settings.get('custom_sound_path')
        loop_sound = self.settings.get('loop_alert_sound', False)
        self._overlay.set_alert_mode(True, custom_sound_path, loop_sound)
        
        # Sound is now handled by overlay's set_alert_mode method
        
            
    def _handle_drink_now(self):
        """Handle drink now button click"""
        default_amount = self.settings.get('default_sip_ml', 250)
        self._log_water(default_amount)
        self._overlay.set_alert_mode(False)
        self._is_snoozed = False
        self.last_reminder_time = time.time()
        
    def _handle_snooze(self):
        """Handle snooze button click"""
        snooze_minutes = self.settings.get('snooze_duration_minutes', 5)
        self._is_snoozed = True
        self._snooze_end_time = time.time() + (snooze_minutes * 60)
        self._overlay.set_alert_mode(False)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Snoozed for {snooze_minutes} minutes")
        
    def _handle_manual_drink(self, amount):
        """Handle manual drink logging from menu"""
        self._log_water(amount)
        if self._overlay._alert_mode:
            self._overlay.set_alert_mode(False)
            self._is_snoozed = False
            self.last_reminder_time = time.time()
            
    def _log_water(self, amount):
        """Log water intake and update UI"""
        was_below_goal = self.today_intake < self.settings['daily_goal_ml']
        
        self.data_manager.log_water(amount)
        self.today_intake += amount
        self._overlay.update_consumption(self.today_intake, self.settings['daily_goal_ml'])
        self._overlay.flash_success()
        
        # Check if goal achieved (trigger confetti only on first time reaching goal)
        if was_below_goal and self.today_intake >= self.settings['daily_goal_ml']:
            self._overlay.celebrate_goal()  # Trigger confetti animation only
            
        # Dashboard removed; no additional UI to refresh
    
    def _show_bedtime_warning(self):
        """Show warning to drink before bed"""
        remaining = self.settings['daily_goal_ml'] - self.today_intake
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Bedtime Reminder")
        msg_box.setText(f"You're {remaining}ml away from your goal!\\nDrink some water before bed?")
        msg_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg_box.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        msg_box.setStyleSheet("""
            QMessageBox {
                background: rgba(30,30,40,250);
            }
            QLabel {
                color: rgba(255,255,255,250);
                font-size: 12px;
            }
            QPushButton {
                background: rgba(255,255,255,25);
                color: rgba(255,255,255,250);
                border: 1px solid rgba(255,255,255,50);
                border-radius: 6px;
                padding: 6px 16px;
                min-width: 60px;
            }
        """)
        
        if msg_box.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            self._handle_drink_now()
            
    def _show_goal_achieved(self):
        """Show goal achievement notification"""
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Goal Achieved!")
        msg_box.setText("Congratulations! You've reached your daily hydration goal!")
        msg_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg_box.setStyleSheet("""
            QMessageBox {
                background: rgba(30,30,40,250);
            }
            QLabel {
                color: rgba(255,255,255,250);
                font-size: 12px;
            }
            QPushButton {
                background: rgba(255,255,255,25);
                color: rgba(255,255,255,250);
                border: 1px solid rgba(255,255,255,50);
                border-radius: 6px;
                padding: 6px 16px;
            }
        """)
        msg_box.exec()
        
    def _persist_overlay_position(self, x, y):
        """Save overlay position to database"""
        self.data_manager.set_setting('overlay_x', x)
        self.data_manager.set_setting('overlay_y', y)
        
    def _handle_overlay_close(self):
        """Handle overlay close request - exit app and tray too."""
        try:
            QtWidgets.QApplication.instance().quit()
        except Exception:
            # As a fallback, hide overlay
            self._overlay.hide()
            self.overlay_is_visible = False
            
        
    @QtCore.Slot()
    def open_settings(self):
        """Open settings dialog"""
        try:
            dialog = SettingsDialog(self.data_manager, parent=self._overlay)
            dialog.settings_updated.connect(self._apply_settings)
            dialog.water_reset.connect(self._handle_water_reset)
            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                # Settings were saved
                self.settings = self.data_manager.get_settings()
                self.today_intake = self.data_manager.get_today_total()
                self._overlay.update_consumption(self.today_intake, self.settings['daily_goal_ml'])
        except Exception as e:
            print(f"Error opening settings: {e}")
            import traceback
            traceback.print_exc()
    
    @QtCore.Slot()
    def launch_overlay(self):
        """Launch overlay mode"""
        if not self.overlay_is_visible:
            self._overlay.show()
            self.overlay_is_visible = True
            
    
    @QtCore.Slot()
    def _handle_water_reset(self):
        """Handle water reset from settings dialog"""
        self.today_intake = 0
        self._overlay.update_consumption(self.today_intake, self.settings['daily_goal_ml'])
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Manual reset: Water intake reset to 0 ml")
    
    @QtCore.Slot(dict)
    def _apply_settings(self, updated_settings):
        """Apply updated settings from dialog"""
        self.settings = updated_settings
        self._overlay.update_consumption(self.today_intake, self.settings['daily_goal_ml'])
        
        # Update theme if changed
        new_theme = updated_settings.get('theme', 'Dark Glassmorphic')
        self._overlay.set_theme(new_theme)
        
        # Update window shape if changed
        new_shape = updated_settings.get('window_shape', 'rectangular')
        self._overlay.set_window_shape(new_shape, save_preference=True)
        
        if not self.paused:
            self.last_reminder_time = time.time()  # Reset reminder timer with new interval
    
    @QtCore.Slot()
    def _handle_intake_reset(self):
        """Handle intake reset from settings"""
        self.today_intake = 0
        self._overlay.update_consumption(self.today_intake, self.settings['daily_goal_ml'])
        
            
    def toggle_overlay_visibility(self):
        """Toggle overlay visibility"""
        if self.overlay_is_visible:
            self._overlay.hide()
            self.overlay_is_visible = False
        else:
            self._overlay.show()
            self.overlay_is_visible = True
        
            
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        
            
    def trigger_drink_now(self):
        """Manually trigger drink now (from tray)"""
        self._handle_drink_now()
        
    # Tray integration methods removed
    
    def cleanup(self):
        """Cleanup resources before exit"""
        print("[HydraPing] Starting cleanup...")
        
        # Stop timers
        if hasattr(self, '_countdown_timer') and self._countdown_timer:
            self._countdown_timer.stop()
        if hasattr(self, '_system_check_timer') and self._system_check_timer:
            self._system_check_timer.stop()
            print("[HydraPing] Timers stopped")
        
        # Hide and cleanup overlay
        if hasattr(self, '_overlay') and self._overlay:
            self._overlay.hide()
            self._overlay.deleteLater()
            self._overlay = None
            print("[HydraPing] Overlay closed")
        
        # Tray removed
        
        print("[HydraPing] Cleanup complete - Application will exit")
        


class HydraPingApp:
    """Main application entry point"""
    
    def __init__(self):
        self.data_manager = get_data_manager()
        self.current_user = None
        self.app = None
        
        # Create default user if not exists
        self._ensure_default_user()
        
        # Set user context in data manager
        self.data_manager.set_user(self.current_user)
        
    def _ensure_default_user(self):
        """Ensure a default user exists for the app"""
        user = self.data_manager.get_or_create_default_user()
        self.current_user = {'id': user['id']}
        
    def start(self):
        """Start the application"""
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setApplicationName("HydraPing")
        # Tray removed; quit when last window closes
        self.app.setQuitOnLastWindowClosed(True)
        
        # Create controller
        self.controller = HydraPingController(self.data_manager, self.current_user)
        
        # Connect cleanup on application quit
        self.app.aboutToQuit.connect(self.controller.cleanup)
        
        self.controller.start()
        
        sys.exit(self.app.exec())
    



if __name__ == "__main__":
    app = HydraPingApp()
    app.start()
