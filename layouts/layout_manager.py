"""
Flexible layout manager that applies configurations
"""

from PySide6 import QtCore, QtWidgets, QtGui
from .layout_config import LayoutConfig, get_layout_config


class LayoutManager:
    """Manages layout creation and updates based on configuration"""
    
    def __init__(self, parent_window):
        self.window = parent_window
        self.current_config = None
        self.current_layout_name = None
        self.preferred_layout = "rectangular"
        
    def apply_layout(self, layout_name: str):
        """Apply a layout configuration"""
        self.current_layout_name = layout_name
        self.current_config = get_layout_config(layout_name)
        
        # Apply window properties
        self._apply_window_properties()
        
        # Update widget configurations
        self._apply_widget_configs()
        
        # Apply window mask (for circular shape)
        self._apply_window_mask()
        
        # Update layout
        self._rebuild_layout()
        
        return self.current_config
    
    def _apply_window_properties(self):
        """Apply window size and basic properties"""
        config = self.current_config
        width, height = config.window_size
        
        # Resize window
        self.window.setFixedSize(width, height)
        
        # Update background box
        x, y, w, h = config.bg_box_geometry
        if hasattr(self.window, '_bg_box'):
            self.window._bg_box.setGeometry(x, y, w, h)
    
    def _apply_widget_configs(self):
        """Apply configuration to all widgets"""
        config = self.current_config
        
        widget_configs = [
            ('_progress_widget', config.progress_widget),
            ('_message_label', config.message_label),
            ('_info_label', config.info_label),
            ('_menu_button', config.menu_button),
            ('_drink_button', config.drink_button),
            ('_snooze_button', config.snooze_button),
        ]
        
        for widget_name, widget_config in widget_configs:
            if hasattr(self.window, widget_name):
                widget = getattr(self.window, widget_name)
                self._apply_widget_config(widget, widget_config)
    
    def _apply_widget_config(self, widget, config):
        """Apply configuration to a single widget"""
        # Visibility
        widget.setVisible(config.visible)
        
        # Size
        if config.size:
            width, height = config.size
            widget.setFixedSize(width, height)
    
    def _rebuild_layout(self):
        """Rebuild the container layout"""
        config = self.current_config
        
        if not hasattr(self.window, '_container'):
            return
        
        container = self.window._container
        
        # Clear existing layout
        old_layout = container.layout()
        if old_layout:
            # Remove all items from layout
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(container)
            QtWidgets.QWidget().setLayout(old_layout)
        
        # Create new layout
        if config.layout_direction == "horizontal":
            layout = QtWidgets.QHBoxLayout(container)
        else:
            layout = QtWidgets.QVBoxLayout(container)
        
        # Apply layout properties
        layout.setSpacing(config.layout_spacing)
        layout.setContentsMargins(*config.layout_margins)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Add widgets in order
        self._add_widgets_to_layout(layout)
    
    def _add_widgets_to_layout(self, layout):
        """Add widgets to layout based on configuration"""
        config = self.current_config
        
        # Define widget order and their configs
        widget_order = [
            ('_progress_widget', config.progress_widget),
            ('_menu_button', config.menu_button),
            ('_message_label', config.message_label),
            ('_snooze_button', config.snooze_button),
            ('_drink_button', config.drink_button),
            ('_info_label', config.info_label),
        ]
        
        for widget_name, widget_config in widget_order:
            if not hasattr(self.window, widget_name):
                continue
                
            widget = getattr(self.window, widget_name)
            
            # Add to layout if visible
            if widget_config.visible:
                if widget_config.stretch > 0:
                    layout.addWidget(widget, widget_config.stretch)
                else:
                    layout.addWidget(widget, 0, widget_config.alignment)
    
    def _apply_window_mask(self):
        """Clear any mask - rely on WA_TranslucentBackground + border-radius for smooth edges.
        QBitmap masks are 1-bit (pixel on/off) and cannot produce anti-aliased curves."""
        self.window.clearMask()
        self._update_shape_border_radius()
    
    def _update_shape_border_radius(self):
        """Update container/bg_box border-radius to match current shape for smooth edges"""
        config = self.current_config
        if not config:
            return

        if config.window_shape == "circle":
            w, h = config.window_size
            r = min(w, h) // 2
            container_radius = r
            bg_radius = r + 1
        else:
            container_radius = 12
            bg_radius = 14

        if hasattr(self.window, '_container') and hasattr(self.window, 'theme_manager'):
            theme = self.window.theme_manager.get_theme()
            self.window._container.setStyleSheet(f"""
                #overlayContainer {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {theme['overlay_bg_start']},
                        stop:1 {theme['overlay_bg_end']}
                    );
                    border-radius: {container_radius}px;
                    border: 1px solid {theme['overlay_border']};
                }}
            """)
        if hasattr(self.window, '_bg_box') and hasattr(self.window, 'theme_manager'):
            theme = self.window.theme_manager.get_theme()
            self.window._bg_box.setStyleSheet(f"""
                #hoverBackground {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {theme['hover_bg_start']},
                        stop:1 {theme['hover_bg_end']}
                    );
                    border-radius: {bg_radius}px;
                    border: 1px solid {theme['hover_border']};
                }}
            """)

    def set_alert_mode(self, is_alert: bool):
        """Handle alert mode transitions"""
        config = self.current_config
        
        if is_alert:
            # Switch to alert layout if configured
            if config.alert_switches_layout and config.alert_target_layout:
                self.apply_layout(config.alert_target_layout)
            
            # Show buttons if configured
            if config.show_buttons_in_alert:
                if hasattr(self.window, '_drink_button'):
                    self.window._drink_button.setVisible(True)
                if hasattr(self.window, '_snooze_button'):
                    self.window._snooze_button.setVisible(True)
        else:
            # Hide buttons
            if hasattr(self.window, '_drink_button'):
                self.window._drink_button.setVisible(False)
            if hasattr(self.window, '_snooze_button'):
                self.window._snooze_button.setVisible(False)
            
            # Return to preferred layout if we switched
            if config.alert_switches_layout and self.current_layout_name != self.preferred_layout:
                self.apply_layout(self.preferred_layout)
    
    def get_current_config(self) -> LayoutConfig:
        """Get current layout configuration"""
        return self.current_config
    
    def set_preferred_layout(self, layout_name: str):
        """Set user's preferred layout"""
        self.preferred_layout = layout_name
    
    def should_show_info_label(self):
        """Return True if info label should be visible on hover"""
        if self.current_config:
            return self.current_config.info_label.visible
        return True
    
    def should_show_message_label(self):
        """Return True if message label should be visible"""
        if self.current_config:
            return self.current_config.message_label.visible
        return True
    
    def should_show_buttons_in_alert(self):
        """Return True if buttons should show in alert mode"""
        if self.current_config:
            return self.current_config.show_buttons_in_alert
        return True
