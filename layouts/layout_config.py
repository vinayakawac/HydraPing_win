"""
Configuration-based layout system for flexible UI management
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from PySide6 import QtCore


@dataclass
class WidgetConfig:
    """Configuration for a single widget"""
    visible: bool = True
    size: Optional[Tuple[int, int]] = None  # (width, height)
    alignment: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignCenter
    stretch: int = 0


@dataclass
class LayoutConfig:
    """Complete layout configuration"""
    # Window properties
    window_size: Tuple[int, int]  # (width, height)
    window_shape: str  # "rectangle" or "circle"
    
    # Layout properties
    layout_direction: str  # "horizontal" or "vertical"
    layout_spacing: int = 8
    layout_margins: Tuple[int, int, int, int] = (12, 4, 12, 4)
    
    # Widget configurations
    progress_widget: WidgetConfig = None
    message_label: WidgetConfig = None
    info_label: WidgetConfig = None
    menu_button: WidgetConfig = None
    drink_button: WidgetConfig = None
    snooze_button: WidgetConfig = None
    
    # Alert mode behavior
    alert_switches_layout: bool = False
    alert_target_layout: Optional[str] = None
    show_buttons_in_alert: bool = True
    
    # Background box
    bg_box_geometry: Tuple[int, int, int, int] = (0, 0, 0, 0)
    
    def __post_init__(self):
        """Initialize default widget configs if not provided"""
        if self.progress_widget is None:
            self.progress_widget = WidgetConfig()
        if self.message_label is None:
            self.message_label = WidgetConfig()
        if self.info_label is None:
            self.info_label = WidgetConfig()
        if self.menu_button is None:
            self.menu_button = WidgetConfig()
        if self.drink_button is None:
            self.drink_button = WidgetConfig()
        if self.snooze_button is None:
            self.snooze_button = WidgetConfig()


# Predefined layout configurations
LAYOUT_CONFIGS = {
    "rectangular": LayoutConfig(
        window_size=(416, 44),
        window_shape="rectangle",
        layout_direction="horizontal",
        layout_spacing=8,
        layout_margins=(12, 4, 12, 4),
        
        progress_widget=WidgetConfig(
            visible=True,
            size=(35, 35),
            stretch=0
        ),
        
        menu_button=WidgetConfig(
            visible=True,
            size=(32, 32),
            stretch=0
        ),
        
        message_label=WidgetConfig(
            visible=True,
            stretch=1,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        ),
        
        snooze_button=WidgetConfig(
            visible=False,
            stretch=0
        ),
        
        drink_button=WidgetConfig(
            visible=False,
            stretch=0
        ),
        
        info_label=WidgetConfig(
            visible=True,
            stretch=0,
            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
        ),
        
        alert_switches_layout=False,
        show_buttons_in_alert=True,
        
        bg_box_geometry=(0, 0, 416, 44)
    ),
    
    "circular": LayoutConfig(
        window_size=(52, 52),
        window_shape="circle",
        layout_direction="vertical",
        layout_spacing=0,
        layout_margins=(3, 3, 3, 3),
        
        progress_widget=WidgetConfig(
            visible=True,
            size=(46, 46),
            stretch=0,
            alignment=QtCore.Qt.AlignmentFlag.AlignCenter
        ),
        
        message_label=WidgetConfig(visible=False),
        info_label=WidgetConfig(visible=False),
        menu_button=WidgetConfig(visible=False),
        drink_button=WidgetConfig(visible=False),
        snooze_button=WidgetConfig(visible=False),
        
        alert_switches_layout=True,
        alert_target_layout="rectangular",
        show_buttons_in_alert=False,
        
        bg_box_geometry=(0, 0, 52, 52)
    )
}


def get_layout_config(layout_name: str) -> LayoutConfig:
    """Get layout configuration by name"""
    return LAYOUT_CONFIGS.get(layout_name, LAYOUT_CONFIGS["rectangular"])
