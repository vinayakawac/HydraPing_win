"""
Rectangular layout for HydraPing overlay
"""

from PySide6 import QtCore, QtWidgets, QtGui
from .base_layout import BaseLayout


class RectangularLayout(BaseLayout):
    """Traditional horizontal rectangular layout"""
    
    def get_window_size(self):
        """Return (width, height) for this layout"""
        return (416, 44)
    
    def create_container_layout(self, container):
        """Create and return the layout for the container widget"""
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(8)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        return layout
    
    def add_widgets_to_layout(self, layout, widgets):
        """Add widgets to the layout in horizontal arrangement"""
        # Horizontal layout: progress, menu, message, snooze, drink, info, close
        layout.addWidget(widgets['progress'], 0)
        layout.addWidget(widgets['menu'], 0)
        layout.addWidget(widgets['message'], 1)
        layout.addWidget(widgets['snooze'], 0)
        layout.addWidget(widgets['drink'], 0)
        layout.addWidget(widgets['info'], 0)
        layout.addWidget(widgets['close'], 0)
    
    def get_bg_box_geometry(self):
        """Return (x, y, width, height) for background box"""
        return (0, 0, 416, 44)
    
    def get_progress_widget_size(self):
        """Return (width, height) for progress widget"""
        return (35, 35)
    
    def should_show_message_label(self):
        """Return True if message label should be visible"""
        return True
    
    def should_show_info_label(self):
        """Return True if info label should be visible"""
        return True
    
    def should_show_buttons_in_alert(self):
        """Return True if drink/snooze buttons should show in alert mode"""
        return True
    
    def get_window_mask(self, width, height):
        """Return QRegion mask for window shape, or None for no mask"""
        return None  # No mask for rectangular
