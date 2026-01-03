# HydraPing Layout System

## Overview
The layout system has been refactored to use a **configuration-based approach** for maximum flexibility and maintainability.

## Architecture

### Core Files
- **`layouts/layout_config.py`** - Layout configurations and widget properties
- **`layouts/layout_manager.py`** - Manages layout application and transitions
- **`layouts/__init__.py`** - Exports the new system

### Legacy Files (for backward compatibility)
- `layouts/base_layout.py` - Abstract base class (deprecated)
- `layouts/normal_layout.py` - Normal layout (deprecated)
- `layouts/minimal_layout.py` - Minimal layout (deprecated)

## How It Works

### 1. Layout Configuration
Layouts are defined as dataclass configurations in `layout_config.py`:

```python
@dataclass
class LayoutConfig:
    window_size: Tuple[int, int]  # (width, height)
    window_shape: str              # "rectangle" or "circle"
    layout_direction: str          # "horizontal" or "vertical"
    layout_spacing: int
    layout_margins: Tuple[int, int, int, int]
    
    # Widget configurations
    progress_widget: WidgetConfig
    message_label: WidgetConfig
    # ... etc
    
    # Behavior
    alert_switches_layout: bool
    alert_target_layout: Optional[str]
    show_buttons_in_alert: bool
```

### 2. Widget Configuration
Each widget has its own configuration:

```python
@dataclass
class WidgetConfig:
    visible: bool = True
    size: Optional[Tuple[int, int]] = None
    alignment: QtCore.Qt.AlignmentFlag
    stretch: int = 0
```

### 3. Predefined Layouts
Two layouts are currently defined:

#### Rectangular (Normal)
- 416x44 window
- Horizontal layout
- All widgets visible
- Shows buttons in alert mode

#### Circular (Minimal)
- 44x44 window  
- Vertical layout
- Only progress widget visible
- Auto-switches to rectangular on alert

## Adding New Layouts

Simply add a new configuration to `LAYOUT_CONFIGS` in `layout_config.py`:

```python
LAYOUT_CONFIGS = {
    # ...existing layouts...
    
    "compact": LayoutConfig(
        window_size=(200, 44),
        window_shape="rectangle",
        layout_direction="horizontal",
        layout_spacing=3,
        
        progress_widget=WidgetConfig(visible=True, size=(30, 30)),
        message_label=WidgetConfig(visible=False),
        info_label=WidgetConfig(visible=True, stretch=1),
        # ...etc
    )
}
```

## Usage

### In OverlayWindow
```python
# Initialize
self._layout_manager = LayoutManager(self)

# Apply a layout
self._layout_manager.apply_layout("rectangular")

# Handle alert mode
self._layout_manager.set_alert_mode(True)
```

### Querying Layout Properties
```python
config = self._layout_manager.get_current_config()

if self._layout_manager.should_show_info_label():
    # Show info label

if self._layout_manager.should_show_buttons_in_alert():
    # Show drink/snooze buttons
```

## Benefits

✅ **Separation of Concerns** - Configuration separate from implementation
✅ **Easy to Add Layouts** - Just add configuration dictionary
✅ **Flexible** - Change any property without touching core code
✅ **Maintainable** - All layout logic centralized
✅ **Testable** - Configurations can be tested independently
✅ **Extensible** - Easy to add new widget properties
✅ **No Duplication** - Widgets created once, configs control them

## Future Enhancements

Potential additions to the layout system:

1. **Animation configs** - Control transitions between layouts
2. **Theme integration** - Layout-specific color schemes
3. **Layout presets** - User-savable layout configurations
4. **Dynamic sizing** - Responsive layouts based on content
5. **Plugin system** - Third-party layout extensions
6. **Layout templates** - Generate layouts from templates
7. **A/B testing** - Easy to test different layout variations

## Migration Notes

The old base_layout system still works for backward compatibility, but new layouts should use the configuration system.

To migrate old code:
- Replace `NormalLayout(self)` with `LayoutManager(self).apply_layout("rectangular")`
- Replace layout manager method calls with LayoutManager methods
- Remove manual widget size/visibility management - let the config handle it
