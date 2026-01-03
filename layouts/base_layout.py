"""
Base layout class for HydraPing overlay layouts
"""

from abc import ABC, abstractmethod
from PySide6 import QtCore, QtWidgets


class BaseLayout(ABC):
    """Abstract base class for overlay layouts"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.widgets = {}
        
    @abstractmethod
    def get_window_size(self):
        """Return (width, height) for this layout"""
        pass
    
    @abstractmethod
    def create_container_layout(self, container):
        """Create and return the layout for the container widget"""
        pass
    
    @abstractmethod
    def add_widgets_to_layout(self, layout, widgets):
        """Add widgets to the layout in the appropriate arrangement"""
        pass
    
    @abstractmethod
    def get_bg_box_geometry(self):
        """Return (x, y, width, height) for background box"""
        pass
    
    @abstractmethod
    def get_progress_widget_size(self):
        """Return (width, height) for progress widget"""
        pass
    
    @abstractmethod
    def should_show_message_label(self):
        """Return True if message label should be visible"""
        pass
    
    @abstractmethod
    def should_show_info_label(self):
        """Return True if info label should be visible"""
        pass
    
    @abstractmethod
    def should_show_buttons_in_alert(self):
        """Return True if drink/snooze buttons should show in alert mode"""
        pass
    
    @abstractmethod
    def get_window_mask(self, width, height):
        """Return QRegion mask for window shape, or None for no mask"""
        pass
