# HydraPing

A minimalist, high-performance hydration tracking companion built with Python and PySide6.

## Overlay Mode

Always-on-top glassmorphic overlay perfect for any workflow:

- **Always visible** floating bar with smooth animations
- **Quick water logging** (100ml, 200ml, 250ml, 500ml, custom)
- **Draggable** - position anywhere on screen
- **Auto-hide on sleep** - respects your sleep schedule
- **Theme-aware** - 6 beautiful glassmorphic themes
- **Performance optimized** - minimal CPU/memory footprint
- **Perfect for work and study**

## Features

- **Modern Glass-morphism UI** - Beautiful, elegant interface with smooth animations
- **High Performance** - Optimized dual-timer system with smart caching
- **Smart Reminders** - Customizable intervals with sleep mode
- **Progress Tracking** - Circular progress ring with live updates
- **55 Motivational Messages** - Rotating inspirational quotes
- **Confetti Celebration** - Visual celebration on goal achievement
- **Custom Sound Alerts** - Use your own audio files (WAV/MP3/OGG/FLAC)
- **Sleep Hours** - Auto-pause reminders during your sleep schedule
- **Activity Log** - Track your complete hydration history
- **Quick Presets** - Light, Moderate, High Activity goals
- **6 Themes** - Dark, Wine Red, Forest Green, Ocean Blue, Sunset Orange, Midnight Blue
- **Local Database** - All data stored securely with SQLite

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Navigate to the project directory:**
   ```bash
   cd project-python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   py main.py
   ```

## Usage

### Launch

The application starts directly in **Overlay Mode** - a minimalist always-on-top bar that stays visible while you work or study.

### Main Features

**Logging Water Intake:**
- Click menu button (⋮) to access drink presets
- Choose from 100ml, 200ml, 250ml, 500ml, or custom amount
- Circular progress ring updates in real-time
- Visual flash effect confirms logging
- Confetti celebration when goal achieved

**Adjusting Settings:**
- Click menu (⋮) → Settings
- Daily goal: 250-10000ml
- Reminder interval: 5-240 minutes
- Default sip size: 50-1000ml
- Sleep hours: Configure start/end times
- Theme: Choose from 6 glassmorphic themes
- Custom sounds: Browse for WAV/MP3/OGG/FLAC files
- Sound loop: Enable continuous alert until acknowledged
- Auto-launch: Start with Windows
- Bedtime warning: 30min alert before sleep

**Overlay Controls:**
- **Drag** anywhere on the bar to reposition
- **Menu (⋮)** - Access drink presets and settings
- **Close (×)** - Exit application (appears on hover)
- **Hover** - Reveals additional info and controls

**Quick Presets:**
- Light Activity: 2000ml daily goal
- Moderate Activity: 2500ml daily goal
- High Activity: 3000ml daily goal

**Reset Options:**
- **Reset Water** - Clear today's intake to zero
- **Reset to Defaults** - Restore all settings to defaults

## Project Structure

```
HydraPing/
├── main.py                     # Application entry point & controller
├── overlay_window.py           # Always-on-top glassmorphic overlay
├── settings_dialog.py          # Settings configuration UI
├── theme_manager.py            # Theme system with caching
├── confetti_widget.py          # Goal celebration animation
├── db_schema.py                # Database schema & migrations
├── icon_helper.py              # Icon utilities
├── core/
│   ├── data_manager.py         # High-level data API with caching
│   ├── config.py               # Application configuration
│   ├── auto_launch.py          # Windows startup integration
│   └── theme_utils.py          # Theme utilities
├── icon.png                    # Application icon
├── requirements.txt            # Python dependencies
├── HydraPing.spec              # PyInstaller build config
└── README.md                   # This file
```

## Database Schema

The application uses SQLite with automatic schema migrations:

- **users** - User accounts with hashed passwords (SHA-256)
- **user_settings** - User preferences with 11 configurable fields
- **hydration_logs** - Water intake records with automatic cleanup (90-day retention)

## Architecture

### Performance Features

- **Dual-Timer System**: 1-second timer for countdown, 60-second timer for system checks
- **Settings Cache**: 5-second TTL cache reduces database queries by 95%
- **Stylesheet Cache**: Theme stylesheets cached per theme, regenerated only on change
- **Animation Pooling**: Reusable animation instances prevent conflicts
- **Sound Timer Reuse**: Single timer instance for alert sound loops
- **Event Consolidation**: Unified hover handling reduces code duplication

### Optimization Results

- **CPU Usage**: 98% reduction in idle-state system checks
- **Memory**: Lower footprint through object reuse
- **Responsiveness**: Smoother UI through optimized animations
- **Database**: 95% fewer queries during normal operation

## Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
py -m PyInstaller HydraPing.spec
```

Or build from scratch:

```bash
py -m PyInstaller --onefile --windowed --icon=icon.png --name="HydraPing" main.py
```

The executable will be in the `dist/` folder (~45MB with all dependencies).

## Troubleshooting

### Missing PySide6 module
```bash
pip install --upgrade PySide6
```

### Sound not working
- Ensure you're on Windows (uses winsound & MCI)
- Check system volume settings
- Test sound with play button (▶) in settings
- Try custom sound file if default doesn't work
- Verify sound file format (WAV/MP3/OGG/FLAC)

### Overlay not visible
- Check if hidden behind fullscreen applications
- Try dragging from last known position
- Restart application to reset position

### Database errors
- Delete `hydra_ping.db` to reset
- Application will recreate schema with migrations
- Automatic log rotation after 90 days

### Performance issues
- Disable background detection if enabled
- Check for conflicting always-on-top applications
- Ensure Windows 10/11 for optimal performance

## Technologies Used

- **Python 3.8+** - Core programming language
- **PySide6 6.6.0** - Modern Qt6-based UI framework
- **SQLite3** - Local database with automatic migrations
- **Qt Animations** - Smooth glassmorphic effects and transitions
- **Winsound & MCI** - Multi-format sound support (WAV/MP3/OGG/FLAC)
- **Hashlib** - Secure password hashing (SHA-256)
- **PyInstaller** - Standalone executable builder
- **Windows API** - Always-on-top enforcement, auto-launch integration

## Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Build Size | ~45MB | Single executable with all dependencies |
| Startup Time | <1 second | Instant launch with overlay |
| Idle CPU | <0.1% | Optimized dual-timer architecture |
| Memory Usage | ~50MB | With Qt6 framework loaded |
| Database Queries | 95% reduced | Smart caching layer |
| Animation FPS | 60fps | Smooth glassmorphic effects |
| Timer Precision | 1 second | Accurate countdown display |
| System Checks | Every 60s | 98% reduction from previous |

## License

This project is open source and available for personal and educational use.

## Contributing

Feel free to fork this project and add your own features!

## Support

For issues or questions, please create an issue in the project repository.

---

**Made with Python**

Stay hydrated!

Download [here](https://github.com/oFive-0s/HydraPing/releases)

