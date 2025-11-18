# 💧 HydraPing

A minimalist hydration tracking companion built with Python and PySide6.

## ✨ Features

- 🎨 **Modern Glass-morphism UI** - Beautiful, elegant interface with 6 theme options
- ⏰ **Smart Reminders** - Customizable hydration reminders with optional sound alerts
- 📊 **Progress Tracking** - Monitor your daily water intake with visual progress bars
- 💪 **Motivational Messages** - Stay motivated with rotating inspirational quotes
- 🎮 **Overlay Mode** - Always-on-top floating bar for gaming or work
- 🔔 **Custom Sound Notifications** - Use your own audio files (WAV, MP3, OGG, FLAC)
- 😴 **Sleep Hours** - Automatically pause reminders during your sleep schedule
- 🎯 **Quick Presets** - Light, Moderate, and High Activity goal presets
- 📝 **Activity Log** - Track your hydration history
- 🔐 **User Authentication** - Secure sign-in and sign-up system
- 💾 **Local Database** - All data stored locally with SQLite

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download this repository**

2. **Navigate to the project directory:**
   ```bash
   cd HydraPing
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## Usage

### Choose Your Mode

**Regular Mode** (Full Window):
1. Launch the application
2. Sign in normally
3. Full-featured window with all options

**Overlay Mode** (Always-On-Top Bar):
1. Launch the application
2. Check ✅ "🎮 Launch in Overlay Mode"
3. Sign in
4. Enjoy the minimal floating bar!

### First Time Setup

1. Launch the application
2. Create an account with your email and password (minimum 6 characters)
3. Sign in with your credentials

### Main Features

**Logging Water Intake:**
- Click "+ 250ml" button to log a glass of water
- Click "+ 500ml" button to log a bottle
- Progress bar updates automatically
- Activity log shows recent intake

**Adjusting Settings:**
- Click the ⚙️ settings icon
- Customize your daily goal (250-10000ml)
- Set reminder interval (5-240 minutes)
- Choose your preferred theme
- Configure sleep hours to pause reminders
- Enable/disable sound notifications
- Add custom sound files
- Click "Save Changes"

**Overlay Mode Controls:**
- Press `Ctrl+Shift+H` to show/hide overlay
- Click and drag to reposition
- Click `─` to minimize
- Click `✕` to close

**Sound Notifications:**
- Click the 🔊 icon to toggle sound on/off
- Use custom sound files (Browse, Test, Loop options)
- Clear custom sound to revert to default

**Reset Options:**
- **Reset to Defaults** - Restore all settings to default values
- **Reset Water** - Clear today's water consumption

**Logout:**
- Click the 🚪 icon to sign out

## Project Structure

```
HydraPing/
├── main.py                     # Application entry point
├── database.py                 # SQLite database operations
├── auth_window.py              # Authentication UI
├── dashboard_window.py         # Main tracker window
├── overlay_window.py           # Always-on-top overlay mode
├── settings_dialog.py          # Settings configuration
├── theme_manager.py            # Theme system
├── icon_helper.py              # Icon utilities
├── confetti_widget.py          # Celebration animation
├── core/
│   ├── auto_launch.py          # System startup integration
│   └── db_schema.py            # Database schema and migrations
├── sounds/
│   └── default_chime.wav       # Default notification sound
├── icon.png                    # Application icon
├── requirements.txt            # Python dependencies
├── HydraPing.spec              # PyInstaller build configuration
└── README.md                   # This file
```

## Database Schema

The application uses SQLite with three tables:

- **users** - User accounts with hashed passwords
- **user_settings** - User preferences and customization
- **hydration_logs** - Water intake records with timestamps

## Customization

### Available Themes

- Dark Glassmorphic (default)
- Wine Red
- Forest Green
- Ocean Blue
- Sunset Orange
- Midnight Blue

### Goal Presets

- Light Activity: 2000ml
- Moderate Activity: 2500ml
- High Activity: 3000ml

### Custom Settings

All settings can be customized through the settings dialog:
- Daily goal (250-10000ml)
- Reminder interval (5-240 minutes)
- Default sip size (50-1000ml)
- Sleep hours (0-23)
- Bedtime warning (on/off)
- Auto-launch on startup (on/off)

## Building Executable

To create a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller HydraPing.spec
```

Or build from scratch:

```bash
pyinstaller --onefile --windowed --icon=icon.png --name="HydraPing" main.py
```

The executable will be in the `dist/` folder.

## Troubleshooting

### Missing PySide6 module
```bash
pip install --upgrade PySide6
```

### Sound not working
- Ensure you're on Windows (uses winsound module)
- Check system volume settings
- Toggle sound off/on in the app
- Test custom sound file with the play button

### Database errors
- Delete `hydra_ping.db` to reset the database
- Application will recreate tables on next launch

### Auto-launch not working
- Run application as administrator once
- Check Windows Task Scheduler for HydraPing entry

## Technologies Used

- **Python 3.8+** - Core programming language
- **PySide6 6.6.0** - Modern Qt-based UI framework
- **SQLite3** - Local database
- **Threading** - Background reminders
- **Winsound & MCI** - Sound notifications with looping support (Windows)
- **Hashlib** - Password hashing (SHA-256)
- **PyInstaller** - Standalone executable builder

## Features Overview

| Feature | Status |
|---------|--------|
| Water Intake Tracking | ✅ |
| Progress Visualization | ✅ |
| Customizable Goals | ✅ |
| Smart Reminders | ✅ |
| Sleep Mode | ✅ |
| Sound Notifications | ✅ |
| Custom Sound Files | ✅ |
| Multiple Themes | ✅ |
| Overlay Mode | ✅ |
| Activity History | ✅ |
| User Authentication | ✅ |
| Auto-Launch | ✅ |
| Goal Presets | ✅ |
| Confetti Celebration | ✅ |
| Reset Options | ✅ |

## License

This project is open source and available for personal and educational use.

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## Support

For issues or questions, please create an issue in the project repository.

---

**Made with ❤️ and Python**

Stay hydrated! 💧
