"""
Settings Dialog - Modal window for overlay settings
Accessible from overlay context menu
"""

import os
from PySide6 import QtWidgets, QtCore, QtGui
from core.auto_launch import is_auto_launch_enabled, enable_auto_launch, disable_auto_launch


class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog accessible from overlay"""
    
    settings_updated = QtCore.Signal(dict)
    water_reset = QtCore.Signal()
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.settings = self.data_manager.get_settings()
        
        self.setWindowTitle("HydraPing Settings")
        self.setModal(True)
        self.setFixedSize(525, 650)  # Increased height for new settings
        
        # Set window icon
        import os
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        
        self._setup_ui()
        self._load_settings()
        self._apply_monochrome_style()
        
    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        title = QtWidgets.QLabel("Settings")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #E8EAED;")
        layout.addWidget(title)
        
        # Scroll area for settings
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #202124;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #5F6368;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #8AB4F8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container widget for scrollable content
        scroll_content = QtWidgets.QWidget()
        scroll_content.setStyleSheet("background: #202124;")
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        
        # Settings form
        form_widget = QtWidgets.QWidget()
        form_widget.setObjectName("settingsForm")
        form_widget.setStyleSheet("""
            QWidget#settingsForm {
                background: #202124; /* Chrome dark background */
                border-radius: 8px;
                padding: 12px 12px 0px 12px;
            }
            /* Form labels (left column) */
            #settingsForm QLabel { color: #BDC1C6; font-size: 12px; }
        """)
        form_layout = QtWidgets.QFormLayout(form_widget)
        form_layout.setContentsMargins(12, 12, 12, 12)
        form_layout.setSpacing(0)
        form_layout.setHorizontalSpacing(16)
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # Daily Goal
        self.goal_spin = QtWidgets.QSpinBox()
        self.goal_spin.setRange(250, 10000)
        self.goal_spin.setSingleStep(50)
        self.goal_spin.setSuffix(" ml")
        self.goal_spin.setMinimumWidth(150)
        self.goal_spin.setStyleSheet("""
            QSpinBox {
                padding: 6px 10px;
                border: 2px solid #3C4043;
                border-radius: 6px;
                font-size: 13px;
                background: #2B2B2B;
                color: #E8EAED;
            }
            QSpinBox:focus {
                border-color: #5F6368; /* neutral focus */
            }
            QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                background: transparent;
            }
        """)
        form_layout.addRow("Daily Goal:", self.goal_spin)
        
        # Reminder Interval
        self.interval_spin = QtWidgets.QSpinBox()
        self.interval_spin.setRange(1, 240)
        self.interval_spin.setSingleStep(1)
        self.interval_spin.setSuffix(" min")
        self.interval_spin.setMinimumWidth(150)
        self.interval_spin.setStyleSheet(self.goal_spin.styleSheet())
        form_layout.addRow("Reminder Interval:", self.interval_spin)
        
        # Default Sip Size
        self.sip_spin = QtWidgets.QSpinBox()
        self.sip_spin.setRange(50, 1000)
        self.sip_spin.setSingleStep(50)
        self.sip_spin.setSuffix(" ml")
        self.sip_spin.setMinimumWidth(150)
        self.sip_spin.setStyleSheet(self.goal_spin.styleSheet())
        form_layout.addRow("Default Sip Size:", self.sip_spin)
        
        # Snooze Duration
        self.snooze_spin = QtWidgets.QSpinBox()
        self.snooze_spin.setRange(1, 30)
        self.snooze_spin.setSingleStep(1)
        self.snooze_spin.setSuffix(" min")
        self.snooze_spin.setMinimumWidth(150)
        self.snooze_spin.setStyleSheet(self.goal_spin.styleSheet())
        form_layout.addRow("Snooze Duration:", self.snooze_spin)
        
        # Theme Selection
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(['Dark Glassmorphic', 'Wine Red', 'Forest Green', 'Ocean Blue', 'Sunset Orange', 'Midnight Blue'])
        self.theme_combo.setMinimumWidth(150)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border: 2px solid #3C4043;
                border-radius: 6px;
                font-size: 13px;
                background: #2B2B2B;
                color: #E8EAED;
            }
            QComboBox:focus {
                border-color: #5F6368; /* neutral focus */
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkw4IDEwTDEyIDYiIHN0cm9rZT0iIzlBQTBBNiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
                width: 16px;
                height: 16px;
            }
            /* Popup list view */
            QComboBox QAbstractItemView {
                background: #202124;
                color: #E8EAED;
                selection-background-color: #3A3B3F;
                selection-color: #E8EAED;
                border: 1px solid #3C4043;
                outline: 0;
            }
        """)
        form_layout.addRow("Theme:", self.theme_combo)
        
        # Display Mode Selection (Radio Buttons)
        display_mode_widget = QtWidgets.QWidget()
        display_mode_widget.setStyleSheet("QWidget { background: transparent; }")
        display_mode_layout = QtWidgets.QHBoxLayout(display_mode_widget)
        display_mode_layout.setContentsMargins(0, 0, 0, 0)
        display_mode_layout.setSpacing(12)
        
        self.normal_mode_radio = QtWidgets.QRadioButton("Normal")
        self.normal_mode_radio.setStyleSheet("""
            QRadioButton {
                font-size: 13px;
                color: #E8EAED;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #5F6368;
                border-radius: 9px;
                background: #2B2B2B;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #8AB4F8;
                border-radius: 9px;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #8AB4F8, stop:0.5 #8AB4F8, stop:0.51 transparent);
            }
        """)
        
        self.minimal_mode_radio = QtWidgets.QRadioButton("Minimal")
        self.minimal_mode_radio.setStyleSheet(self.normal_mode_radio.styleSheet())
        
        # Set default checked
        self.normal_mode_radio.setChecked(True)
        
        display_mode_layout.addWidget(self.normal_mode_radio)
        display_mode_layout.addWidget(self.minimal_mode_radio)
        display_mode_layout.addStretch()
        
        form_layout.addRow("Display Mode:", display_mode_widget)
        
        # Auto-launch checkbox
        self.auto_launch_check = QtWidgets.QCheckBox("Launch on system startup")
        self.auto_launch_check.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #E8EAED;
                spacing: 8px; /* gap between box and text */
                padding-left: 2px; /* ensure text not clipped */
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3C4043;
                border-radius: 4px;
                background: #2B2B2B;
                margin-right: 8px;
            }
            QCheckBox::indicator:checked {
                background: #E8EAED; /* neutral check */
                border-color: #E8EAED;
            }
        """)
        form_layout.addRow("Auto Launch:", self.auto_launch_check)
        
        # Sound enabled checkbox
        self.sound_check = QtWidgets.QCheckBox("Enable reminder sounds")
        self.sound_check.setStyleSheet(self.auto_launch_check.styleSheet())
        form_layout.addRow("Sound:", self.sound_check)
        
        # Custom sound file picker
        sound_file_widget = QtWidgets.QWidget()
        sound_file_widget.setStyleSheet("QWidget { background: transparent; }")
        sound_file_layout = QtWidgets.QHBoxLayout(sound_file_widget)
        sound_file_layout.setContentsMargins(0, 0, 0, 0)
        sound_file_layout.setSpacing(8)
        
        self.sound_path_label = QtWidgets.QLabel("Default")
        self.sound_path_label.setStyleSheet("""
            QLabel {
                color: #9AA0A6;
                font-size: 11px;
                padding: 4px 8px;
                background: transparent;
            }
        """)
        self.sound_path_label.setMinimumWidth(120)
        self.sound_path_label.setWordWrap(False)
        self.sound_path_label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.sound_path_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        
        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.setFixedHeight(28)
        browse_btn.setStyleSheet("""
            QPushButton {
                padding: 4px 12px;
                border: 2px solid #3C4043;
                border-radius: 4px;
                font-size: 11px;
                background: #2B2B2B;
                color: #E8EAED;
            }
            QPushButton:hover {
                background: #3A3B3F;
                border-color: #5F6368;
            }
        """)
        browse_btn.clicked.connect(self._browse_sound_file)
        
        test_btn = QtWidgets.QPushButton("▶")
        test_btn.setFixedSize(28, 28)
        test_btn.setStyleSheet("""
            QPushButton {
                padding: 0px;
                border: 2px solid #3C4043;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                background: #2B2B2B;
                color: #E8EAED;
            }
            QPushButton:hover {
                background: #3A3B3F;
                border-color: #5F6368;
            }
        """)
        test_btn.setToolTip("Test sound")
        test_btn.clicked.connect(self._test_sound)
        
        self.loop_btn = QtWidgets.QPushButton("↻")
        self.loop_btn.setFixedSize(28, 28)
        self.loop_btn.setCheckable(True)
        self.loop_btn.setStyleSheet("""
            QPushButton {
                padding: 0px;
                border: 2px solid #3C4043;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                background: #2B2B2B;
                color: #E8EAED;
            }
            QPushButton:hover {
                background: #3A3B3F;
                border-color: #5F6368;
            }
            QPushButton:checked {
                background: #3A3B3F;
                border-color: #8AB4F8;
                color: #8AB4F8;
            }
        """)
        self.loop_btn.setToolTip("Loop alert sound")
        
        clear_btn = QtWidgets.QPushButton("×")
        clear_btn.setFixedSize(28, 28)
        clear_btn.setStyleSheet("""
            QPushButton {
                padding: 0px;
                border: 2px solid #3C4043;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                background: #2B2B2B;
                color: #E8EAED;
            }
            QPushButton:hover {
                background: rgba(255,100,100,35);
                border-color: #5F6368;
            }
        """)
        clear_btn.setToolTip("Clear custom sound")
        clear_btn.clicked.connect(self._clear_sound_file)
        
        sound_file_layout.addWidget(self.sound_path_label, 1)
        sound_file_layout.addWidget(browse_btn, 0)
        sound_file_layout.addWidget(test_btn, 0)
        sound_file_layout.addWidget(self.loop_btn, 0)
        sound_file_layout.addWidget(clear_btn, 0)
        
        form_layout.addRow("Custom Sound:", sound_file_widget)
        
        # Sleep Hours
        sleep_hours_widget = QtWidgets.QWidget()
        sleep_hours_widget.setStyleSheet("QWidget { background: transparent; }")
        sleep_hours_layout = QtWidgets.QHBoxLayout(sleep_hours_widget)
        sleep_hours_layout.setContentsMargins(0, 0, 0, 0)
        sleep_hours_layout.setSpacing(8)
        
        self.sleep_start_spin = QtWidgets.QSpinBox()
        self.sleep_start_spin.setRange(0, 23)
        self.sleep_start_spin.setSuffix(":00")
        self.sleep_start_spin.setMinimumWidth(70)
        self.sleep_start_spin.setStyleSheet(self.goal_spin.styleSheet())
        
        sleep_to_label = QtWidgets.QLabel("to")
        sleep_to_label.setStyleSheet("color: #9AA0A6; font-size: 11px; background: transparent;")
        
        self.sleep_end_spin = QtWidgets.QSpinBox()
        self.sleep_end_spin.setRange(0, 23)
        self.sleep_end_spin.setSuffix(":00")
        self.sleep_end_spin.setMinimumWidth(70)
        self.sleep_end_spin.setStyleSheet(self.goal_spin.styleSheet())
        
        sleep_hours_layout.addWidget(self.sleep_start_spin)
        sleep_hours_layout.addWidget(sleep_to_label)
        sleep_hours_layout.addWidget(self.sleep_end_spin)
        sleep_hours_layout.addStretch()
        
        form_layout.addRow("Sleep Hours:", sleep_hours_widget)
        
        # Bedtime Warning
        self.bedtime_warning_check = QtWidgets.QCheckBox("Remind before bedtime")
        self.bedtime_warning_check.setStyleSheet(self.auto_launch_check.styleSheet())
        form_layout.addRow("Bedtime Warning:", self.bedtime_warning_check)
        
        scroll_layout.addWidget(form_widget)
        
        # Goal Presets
        presets_label = QtWidgets.QLabel("Quick Presets")
        presets_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #E8EAED; margin: 1px 0px 0px 0px; padding: 0px; background: transparent;")
        scroll_layout.addWidget(presets_label)
        
        presets_layout = QtWidgets.QHBoxLayout()
        presets_layout.setSpacing(8)
        
        light_btn = QtWidgets.QPushButton("Light Activity\n2000ml")
        light_btn.setMinimumHeight(50)
        light_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                border: 2px solid #3C4043;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                background: #2B2B2B;
                color: #E8EAED;
            }
            QPushButton:hover {
                background: #3A3B3F;
                border-color: #8AB4F8;
            }
        """)
        light_btn.clicked.connect(lambda: self.goal_spin.setValue(2000))
        
        moderate_btn = QtWidgets.QPushButton("Moderate\n2500ml")
        moderate_btn.setMinimumHeight(50)
        moderate_btn.setStyleSheet(light_btn.styleSheet())
        moderate_btn.clicked.connect(lambda: self.goal_spin.setValue(2500))
        
        high_btn = QtWidgets.QPushButton("High Activity\n3000ml")
        high_btn.setMinimumHeight(50)
        high_btn.setStyleSheet(light_btn.styleSheet())
        high_btn.clicked.connect(lambda: self.goal_spin.setValue(3000))
        
        presets_layout.addWidget(light_btn)
        presets_layout.addWidget(moderate_btn)
        presets_layout.addWidget(high_btn)
        
        scroll_layout.addLayout(presets_layout)
        
        # Set scroll content and add to layout
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area, 1)  # Add stretch factor to take available space
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(8)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setMinimumHeight(32)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 18px;
                border: 2px solid #3C4043;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                background: #2D2F33;
                color: #E8EAED;
            }
            QPushButton:hover {
                background: #3A3B3F;
                border-color: #5F6368;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QtWidgets.QPushButton("Save Changes")
        save_btn.setMinimumHeight(32)
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 18px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                background: #303134; /* Chrome dark primary */
                color: #E8EAED;
            }
            QPushButton:hover {
                background: #3C4043;
            }
            QPushButton:pressed {
                background: #202124;
            }
        """)
        save_btn.clicked.connect(self._save_settings)
        
        reset_btn = QtWidgets.QPushButton("Reset to Defaults")
        reset_btn.setMinimumHeight(32)
        reset_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 18px;
                border: 2px solid #3C4043;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                background: rgba(232,71,71,25);
                color: #E8EAED;
            }
            QPushButton:hover {
                background: rgba(232,71,71,45);
                border-color: #E84747;
            }
        """)
        reset_btn.clicked.connect(self._reset_to_defaults)
        
        reset_water_btn = QtWidgets.QPushButton("Reset Water")
        reset_water_btn.setMinimumHeight(32)
        reset_water_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 18px;
                border: 2px solid #3C4043;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                background: rgba(100,150,232,25);
                color: #E8EAED;
            }
            QPushButton:hover {
                background: rgba(100,150,232,45);
                border-color: #6496E8;
            }
        """)
        reset_water_btn.clicked.connect(self._reset_water)
        
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(reset_water_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)

    def _apply_monochrome_style(self):
        """Apply grayscale, dialog-scoped styling only to settings window.
        Keeps app theme intact elsewhere.
        """
        self.setStyleSheet(self.styleSheet() + """
            /* Dialog background */
            QDialog {
                background: #202124; /* Chrome dark */
            }
            /* Generic labels if not overridden */
            QLabel { color: #E8EAED; }
        """)
        
    def _browse_sound_file(self):
        """Open file dialog to select custom sound file"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Sound File",
            "",
            "Sound Files (*.wav *.mp3 *.ogg *.flac);;All Files (*.*)"
        )
        
        if file_path:
            import os
            self.sound_path_label.setText(os.path.basename(file_path))
            self.sound_path_label.setToolTip(file_path)
    
    def _clear_sound_file(self):
        """Clear custom sound file selection"""
        self.sound_path_label.setText("Default")
        self.sound_path_label.setToolTip("")
    
    def _test_sound(self):
        """Test the selected sound file"""
        custom_sound_path = None
        if self.sound_path_label.text() != "Default" and self.sound_path_label.toolTip():
            custom_sound_path = self.sound_path_label.toolTip()
        
        if custom_sound_path and os.path.exists(custom_sound_path):
            try:
                import winsound
                import ctypes
                
                # Use MCI for MP3/other formats, fallback to winsound for WAV
                if custom_sound_path.lower().endswith('.wav'):
                    winsound.PlaySound(custom_sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:
                    # Use Windows MCI for MP3/OGG/FLAC
                    winmm = ctypes.windll.winmm
                    winmm.mciSendStringW(f'open "{custom_sound_path}" type mpegvideo alias mp3', None, 0, None)
                    winmm.mciSendStringW('play mp3 from 0', None, 0, None)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'Sound Test', 
                    f'Could not play sound: {str(e)}')
        else:
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except:
                QtWidgets.QMessageBox.information(self, 'Sound Test', 
                    'Playing default system beep')
    
    def _load_settings(self):
        """Load current settings into form"""
        self.goal_spin.setValue(self.settings.get('daily_goal_ml', 2000))
        self.interval_spin.setValue(self.settings.get('reminder_interval_minutes', 60))
        self.sip_spin.setValue(self.settings.get('default_sip_ml', 250))
        self.snooze_spin.setValue(self.settings.get('snooze_duration_minutes', 5))
        self.theme_combo.setCurrentText(self.settings.get('theme', 'Dark Glassmorphic'))
        self.auto_launch_check.setChecked(is_auto_launch_enabled())
        self.sound_check.setChecked(self.settings.get('chime_enabled', True))
        
        custom_sound = self.settings.get('custom_sound_path', None)
        if custom_sound:
            import os
            self.sound_path_label.setText(os.path.basename(custom_sound))
            self.sound_path_label.setToolTip(custom_sound)
        else:
            self.sound_path_label.setText("Default")
            self.sound_path_label.setToolTip("")
        
        self.loop_btn.setChecked(self.settings.get('loop_alert_sound', False))
        self.sleep_start_spin.setValue(self.settings.get('sleep_start_hour', 22))
        self.sleep_end_spin.setValue(self.settings.get('sleep_end_hour', 7))
        self.bedtime_warning_check.setChecked(self.settings.get('bedtime_warning_enabled', True))
        
        # Load window shape setting
        window_shape = self.settings.get('window_shape', 'rectangular')
        if window_shape == 'rectangular':
            self.normal_mode_radio.setChecked(True)
        else:
            self.minimal_mode_radio.setChecked(True)
    
    def _save_settings(self):
        """Save settings and close dialog"""
        # Get values
        new_goal = self.goal_spin.value()
        new_interval = self.interval_spin.value()
        new_sip = self.sip_spin.value()
        new_snooze = self.snooze_spin.value()
        new_theme = self.theme_combo.currentText()
        sound_enabled = self.sound_check.isChecked()
        
        # Get custom sound path
        custom_sound_path = None
        if self.sound_path_label.text() != "Default" and self.sound_path_label.toolTip():
            custom_sound_path = self.sound_path_label.toolTip()
        
        loop_enabled = self.loop_btn.isChecked()
        sleep_start = self.sleep_start_spin.value()
        sleep_end = self.sleep_end_spin.value()
        bedtime_warning = self.bedtime_warning_check.isChecked()
        window_shape = 'rectangular' if self.normal_mode_radio.isChecked() else 'circular'
        
        # Update via data_manager
        self.data_manager.update_settings(
            daily_goal_ml=new_goal,
            reminder_interval_minutes=new_interval,
            default_sip_ml=new_sip,
            snooze_duration_minutes=new_snooze,
            theme=new_theme,
            chime_enabled=sound_enabled,
            custom_sound_path=custom_sound_path,
            loop_alert_sound=loop_enabled,
            sleep_start_hour=sleep_start,
            sleep_end_hour=sleep_end,
            bedtime_warning_enabled=bedtime_warning,
            window_shape=window_shape
        )
        
        # Handle auto-launch
        if self.auto_launch_check.isChecked():
            success, message = enable_auto_launch()
            if not success:
                QtWidgets.QMessageBox.warning(self, 'Auto-Launch', 
                    f'Could not enable auto-launch: {message}')
        else:
            success, message = disable_auto_launch()
            if not success:
                QtWidgets.QMessageBox.warning(self, 'Auto-Launch', 
                    f'Could not disable auto-launch: {message}')
        
        # Emit signal with new settings
        updated_settings = {
            'daily_goal_ml': new_goal,
            'reminder_interval_minutes': new_interval,
            'default_sip_ml': new_sip,
            'snooze_duration_minutes': new_snooze,
            'theme': new_theme,
            'chime_enabled': sound_enabled,
            'custom_sound_path': custom_sound_path,
            'loop_alert_sound': loop_enabled,
            'sleep_start_hour': sleep_start,
            'sleep_end_hour': sleep_end,
            'bedtime_warning_enabled': bedtime_warning,
            'window_shape': window_shape
        }
        self.settings_updated.emit(updated_settings)
        
        self.accept()
    
    def _reset_to_defaults(self):
        """Reset all settings to default values"""
        reply = QtWidgets.QMessageBox.question(
            self,
            'Reset Settings',
            'Are you sure you want to reset all settings to defaults?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.goal_spin.setValue(2000)
            self.interval_spin.setValue(60)
            self.sip_spin.setValue(250)
            self.snooze_spin.setValue(5)
            self.theme_combo.setCurrentText('Dark Glassmorphic')
            self.sound_check.setChecked(True)
            self.sound_path_label.setText("Default")
            self.sound_path_label.setToolTip("")
            self.loop_btn.setChecked(False)
            self.sleep_start_spin.setValue(22)
            self.sleep_end_spin.setValue(7)
            self.bedtime_warning_check.setChecked(True)
            self.normal_mode_radio.setChecked(True)
    
    def _reset_water(self):
        """Reset today's water consumption to zero"""
        reply = QtWidgets.QMessageBox.question(
            self,
            'Reset Water Intake',
            'Are you sure you want to reset today\'s water consumption to zero?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # Clear today's hydration logs
            self.data_manager.reset_today()
            self.water_reset.emit()  # Notify controller to update overlay
            QtWidgets.QMessageBox.information(
                self,
                'Water Reset',
                'Today\'s water intake has been reset to zero.'
            )
