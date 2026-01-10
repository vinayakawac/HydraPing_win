"""
Context Detector - Detects user activity context for smart reminder adjustments
Monitors active applications and adjusts hydration reminders accordingly
"""

import psutil
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum


class ActivityContext(Enum):
    """User activity contexts"""
    GAMING = "gaming"
    WORKING = "working"
    BROWSING = "browsing"
    IDLE = "idle"
    MEETING = "meeting"
    CREATIVE = "creative"
    UNKNOWN = "unknown"


class ContextDetector:
    """Detects user activity context based on running processes"""
    
    # Application categorization
    GAMING_APPS = {
        'steam.exe', 'steamwebhelper.exe', 'gameoverlayui.exe',
        'epicgameslauncher.exe', 'origin.exe', 'battle.net.exe',
        'gog galaxy.exe', 'ubisoft game launcher.exe',
        # Popular games
        'valorant.exe', 'league of legends.exe', 'dota2.exe',
        'csgo.exe', 'minecraft.exe', 'roblox.exe',
        'fortnite.exe', 'apex legends.exe', 'overwatch.exe',
        'gta5.exe', 'witcher3.exe', 'cyberpunk2077.exe',
        'eldenring.exe', 'wow.exe', 'ffxiv.exe'
    }
    
    WORK_APPS = {
        'excel.exe', 'winword.exe', 'powerpnt.exe', 'outlook.exe',
        'teams.exe', 'slack.exe', 'discord.exe',
        'code.exe', 'devenv.exe', 'pycharm64.exe', 'idea64.exe',
        'sublime_text.exe', 'notepad++.exe', 'atom.exe',
        'rider64.exe', 'webstorm64.exe', 'phpstorm64.exe',
        'datagrip64.exe', 'goland64.exe', 'rubymine64.exe'
    }
    
    BROWSER_APPS = {
        'chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe',
        'brave.exe', 'vivaldi.exe', 'safari.exe'
    }
    
    MEETING_APPS = {
        'teams.exe', 'zoom.exe', 'skype.exe', 'webexmta.exe',
        'gotomeeting.exe', 'slack.exe', 'discord.exe'
    }
    
    CREATIVE_APPS = {
        'photoshop.exe', 'illustrator.exe', 'indesign.exe',
        'premiere pro.exe', 'after effects.exe', 'audition.exe',
        'blender.exe', 'unity.exe', 'unrealengine.exe',
        'fl64.exe', 'ableton live.exe', 'cubase.exe',
        'gimp.exe', 'inkscape.exe', 'krita.exe'
    }
    
    def __init__(self):
        self._context_history: List[tuple] = []  # (timestamp, context)
        self._max_history = 100
        self._cache_duration = 10  # seconds
        self._last_check = None
        self._cached_context = None
    
    def get_running_processes(self) -> Set[str]:
        """Get set of currently running process names"""
        try:
            processes = set()
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name']
                    if name:
                        processes.add(name.lower())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return processes
        except Exception:
            return set()
    
    def detect_context(self) -> ActivityContext:
        """Detect current user activity context"""
        # Check cache
        if self._last_check and self._cached_context:
            if (datetime.now() - self._last_check).total_seconds() < self._cache_duration:
                return self._cached_context
        
        processes = self.get_running_processes()
        
        # Priority-based detection (gaming > meeting > work > creative > browsing)
        if processes & self.GAMING_APPS:
            context = ActivityContext.GAMING
        elif processes & self.MEETING_APPS:
            # Additional check for meeting apps
            context = ActivityContext.MEETING
        elif processes & self.WORK_APPS:
            context = ActivityContext.WORKING
        elif processes & self.CREATIVE_APPS:
            context = ActivityContext.CREATIVE
        elif processes & self.BROWSER_APPS:
            context = ActivityContext.BROWSING
        else:
            # Check CPU usage to detect idle
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                if cpu_percent < 10:
                    context = ActivityContext.IDLE
                else:
                    context = ActivityContext.UNKNOWN
            except Exception:
                context = ActivityContext.UNKNOWN
        
        # Update cache
        self._cached_context = context
        self._last_check = datetime.now()
        
        # Update history
        self._context_history.append((datetime.now(), context))
        if len(self._context_history) > self._max_history:
            self._context_history.pop(0)
        
        return context
    
    def get_context_duration(self) -> float:
        """Get how long user has been in current context (minutes)"""
        if len(self._context_history) < 2:
            return 0
        
        current_context = self._context_history[-1][1]
        start_time = None
        
        # Find when current context started
        for timestamp, context in reversed(self._context_history):
            if context != current_context:
                break
            start_time = timestamp
        
        if start_time:
            return (datetime.now() - start_time).total_seconds() / 60
        return 0
    
    def should_suppress_reminder(self) -> bool:
        """Determine if reminder should be suppressed based on context"""
        context = self.detect_context()
        duration = self.get_context_duration()
        
        # Suppress during intense gaming sessions
        if context == ActivityContext.GAMING and duration < 45:
            return True
        
        # Suppress during meetings (first 15 minutes)
        if context == ActivityContext.MEETING and duration < 15:
            return True
        
        return False
    
    def get_reminder_style(self) -> Dict[str, any]:
        """Get appropriate reminder style based on context"""
        context = self.detect_context()
        
        styles = {
            ActivityContext.GAMING: {
                'urgency': 'low',
                'sound_volume': 0.3,
                'visual_intensity': 'minimal',
                'duration': 3,  # seconds
                'can_skip': True,
                'description': 'Gentle reminder - gaming detected'
            },
            ActivityContext.WORKING: {
                'urgency': 'medium',
                'sound_volume': 0.6,
                'visual_intensity': 'normal',
                'duration': 5,
                'can_skip': False,
                'description': 'Standard reminder - work session'
            },
            ActivityContext.MEETING: {
                'urgency': 'low',
                'sound_volume': 0.2,
                'visual_intensity': 'minimal',
                'duration': 2,
                'can_skip': True,
                'description': 'Silent reminder - meeting in progress'
            },
            ActivityContext.CREATIVE: {
                'urgency': 'low',
                'sound_volume': 0.4,
                'visual_intensity': 'minimal',
                'duration': 3,
                'can_skip': True,
                'description': 'Gentle reminder - creative work'
            },
            ActivityContext.BROWSING: {
                'urgency': 'medium',
                'sound_volume': 0.7,
                'visual_intensity': 'normal',
                'duration': 5,
                'can_skip': False,
                'description': 'Standard reminder'
            },
            ActivityContext.IDLE: {
                'urgency': 'high',
                'sound_volume': 0.8,
                'visual_intensity': 'high',
                'duration': 7,
                'can_skip': False,
                'description': 'Perfect time for water!'
            },
            ActivityContext.UNKNOWN: {
                'urgency': 'medium',
                'sound_volume': 0.6,
                'visual_intensity': 'normal',
                'duration': 5,
                'can_skip': False,
                'description': 'Standard reminder'
            }
        }
        
        return styles.get(context, styles[ActivityContext.UNKNOWN])
    
    def get_adjusted_interval(self, base_interval: int) -> int:
        """
        Adjust reminder interval based on detected context
        Returns: adjusted interval in minutes
        """
        context = self.detect_context()
        duration = self.get_context_duration()
        
        adjustments = {
            ActivityContext.GAMING: 1.3,      # Longer intervals during gaming
            ActivityContext.WORKING: 1.0,     # Normal intervals for work
            ActivityContext.MEETING: 1.5,     # Much longer during meetings
            ActivityContext.CREATIVE: 1.2,    # Slightly longer for creative work
            ActivityContext.BROWSING: 0.9,    # Slightly shorter for browsing
            ActivityContext.IDLE: 0.8,        # Shorter when idle (good time to drink!)
            ActivityContext.UNKNOWN: 1.0      # Normal intervals
        }
        
        factor = adjustments.get(context, 1.0)
        
        # Further adjust for very long sessions
        if duration > 90:  # Over 90 minutes in same context
            factor *= 0.9  # Increase reminder frequency
        
        adjusted = int(base_interval * factor)
        
        # Ensure reasonable bounds
        return max(5, min(240, adjusted))
    
    def get_context_message(self) -> str:
        """Get context-aware message"""
        context = self.detect_context()
        duration = self.get_context_duration()
        
        messages = {
            ActivityContext.GAMING: [
                "GG! Time for a water break 🎮",
                "Hydrate to dominate! 💧",
                "Quick sip between rounds? 🥤"
            ],
            ActivityContext.WORKING: [
                "Stay productive - stay hydrated! 💼",
                "Brain fuel time! 🧠💧",
                "Quick water break for better focus 📊"
            ],
            ActivityContext.MEETING: [
                "Psst... quick water break? 🤫",
                "Hydration = better communication 🎤",
                "Subtle reminder to drink 💧"
            ],
            ActivityContext.CREATIVE: [
                "Creativity flows with hydration! 🎨",
                "Refresh your mind with water 💡",
                "Stay inspired, stay hydrated ✨"
            ],
            ActivityContext.BROWSING: [
                "Time for a water break! 🌐",
                "Hydrate while you navigate 💧",
                "Quick sip time! 💦"
            ],
            ActivityContext.IDLE: [
                "Perfect time for water! ⏰",
                "You're free - let's hydrate! 🎯",
                "Great moment for a drink! 💧"
            ],
            ActivityContext.UNKNOWN: [
                "Time to hydrate! 💧",
                "Water break time! 💦",
                "Don't forget to drink! 🥤"
            ]
        }
        
        context_messages = messages.get(context, messages[ActivityContext.UNKNOWN])
        
        # Add urgency for long sessions
        if duration > 120:
            return f"{context_messages[0]} (You've been at it for {int(duration)} min!)"
        
        # Rotate through messages
        index = int(datetime.now().timestamp() / 300) % len(context_messages)
        return context_messages[index]
    
    def get_stats(self) -> Dict[str, any]:
        """Get context detection statistics"""
        if not self._context_history:
            return {}
        
        # Count context occurrences
        context_counts = {}
        for _, context in self._context_history:
            context_name = context.value
            context_counts[context_name] = context_counts.get(context_name, 0) + 1
        
        return {
            'current_context': self.detect_context().value,
            'context_duration_minutes': self.get_context_duration(),
            'history_size': len(self._context_history),
            'context_distribution': context_counts
        }
