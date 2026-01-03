"""
Circular layout for HydraPing overlay
"""

from PySide6 import QtCore, QtWidgets, QtGui
from .base_layout import BaseLayout


class CircularLayout(BaseLayout):
    """Minimal circular layout for compact display"""
    
    def get_window_size(self):
        """Return (width, height) for this layout"""
        return (150, 150)
    
    def create_container_layout(self, container):
        """Create and return the layout for the container widget"""
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        return layout
    
    def add_widgets_to_layout(self, layout, widgets):
        """Add widgets to the layout in circular arrangement"""
        # Circular layout: ONLY centered progress, nothing else
        layout.addWidget(widgets['progress'], 0, QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Hide ALL other elements in circular mode
        widgets['menu'].setVisible(False)
        widgets['close'].setVisible(False)
        widgets['message'].setVisible(False)
        widgets['info'].setVisible(False)
        widgets['drink'].setVisible(False)
        widgets['snooze'].setVisible(False)
    
    def get_bg_box_geometry(self):
        """Return (x, y, width, height) for background box"""
        return (0, 0, 150, 150)
    
    def get_progress_widget_size(self):
        """Return (width, height) for progress widget"""
        return (130, 130)
    
    def should_show_message_label(self):
        """Return True if message label should be visible"""
        return False
    
    def should_show_info_label(self):
        """Return True if info label should be visible"""
        return False
    
    def should_show_buttons_in_alert(self):
        """Return True if drink/snooze buttons should show in alert mode"""
        return False  # In circular mode, click anywhere to drink
    
    def get_window_mask(self, width, height):
        """Return QRegion mask for window shape, or None for no mask"""
        # Create circular mask
        return QtGui.QRegion(0, 0, width, height, QtGui.QRegion.RegionType.Ellipse)
