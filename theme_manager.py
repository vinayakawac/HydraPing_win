"""
Theme Manager for HydraPing
Handles color schemes and styling for the application
"""

class ThemeManager:
    """Manage application themes and color schemes"""
    
    THEMES = {
        'Light Glassmorphic': {
            'name': 'Light Glassmorphic',
            'overlay_bg_start': 'rgba(30,30,30,40)',
            'overlay_bg_end': 'rgba(20,20,20,30)',
            'overlay_border': 'rgba(0,0,0,90)',
            'hover_bg_start': 'rgba(30,30,30,60)',
            'hover_bg_end': 'rgba(20,20,20,50)',
            'hover_border': 'rgba(0,0,0,120)',
            'text_primary': 'rgba(0,0,0,250)',
            'text_secondary': 'rgba(0,0,0,200)',
            'text_tertiary': 'rgba(0,0,0,180)',
            'button_bg': 'rgba(0,0,0,25)',
            'button_hover': 'rgba(0,0,0,35)',
            'dialog_bg': 'rgba(240,240,240,250)',
            'progress_low': 'rgba(232,71,71,220)',
            'progress_mid': 'rgba(255,193,7,220)',
            'progress_high': 'rgba(76,175,80,220)',
        },
        'Dark Glassmorphic': {
            'name': 'Dark Glassmorphic',
            'overlay_bg_start': 'rgba(255,255,255,40)',
            'overlay_bg_end': 'rgba(255,255,255,30)',
            'overlay_border': 'rgba(255,255,255,90)',
            'hover_bg_start': 'rgba(255,255,255,60)',
            'hover_bg_end': 'rgba(255,255,255,50)',
            'hover_border': 'rgba(255,255,255,120)',
            'text_primary': 'rgba(255,255,255,250)',
            'text_secondary': 'rgba(255,255,255,200)',
            'text_tertiary': 'rgba(255,255,255,180)',
            'button_bg': 'rgba(255,255,255,25)',
            'button_hover': 'rgba(255,255,255,35)',
            'dialog_bg': 'rgba(30,30,40,250)',
            'progress_low': 'rgba(232,71,71,220)',
            'progress_mid': 'rgba(255,193,7,220)',
            'progress_high': 'rgba(76,175,80,220)',
        },
        'Wine Red': {
            'name': 'Wine Red',
            'overlay_bg_start': 'rgba(139,0,0,45)',
            'overlay_bg_end': 'rgba(115,0,0,35)',
            'overlay_border': 'rgba(178,34,34,100)',
            'hover_bg_start': 'rgba(139,0,0,65)',
            'hover_bg_end': 'rgba(115,0,0,55)',
            'hover_border': 'rgba(178,34,34,130)',
            'text_primary': 'rgba(255,255,255,250)',
            'text_secondary': 'rgba(255,255,255,220)',
            'text_tertiary': 'rgba(255,255,255,200)',
            'button_bg': 'rgba(139,0,0,30)',
            'button_hover': 'rgba(139,0,0,45)',
            'dialog_bg': 'rgba(80,0,0,250)',
            'progress_low': 'rgba(255,138,101,220)',
            'progress_mid': 'rgba(255,193,7,220)',
            'progress_high': 'rgba(255,182,193,220)',
        },
        'Forest Green': {
            'name': 'Forest Green',
            'overlay_bg_start': 'rgba(129,199,132,45)',
            'overlay_bg_end': 'rgba(102,187,106,35)',
            'overlay_border': 'rgba(165,214,167,100)',
            'hover_bg_start': 'rgba(129,199,132,65)',
            'hover_bg_end': 'rgba(102,187,106,55)',
            'hover_border': 'rgba(165,214,167,130)',
            'text_primary': 'rgba(255,255,255,250)',
            'text_secondary': 'rgba(255,255,255,220)',
            'text_tertiary': 'rgba(255,255,255,200)',
            'button_bg': 'rgba(129,199,132,30)',
            'button_hover': 'rgba(129,199,132,45)',
            'dialog_bg': 'rgba(27,94,32,250)',
            'progress_low': 'rgba(255,138,101,220)',
            'progress_mid': 'rgba(255,213,79,220)',
            'progress_high': 'rgba(165,214,167,220)',
        },
        'Ocean Blue': {
            'name': 'Ocean Blue',
            'overlay_bg_start': 'rgba(100,181,246,45)',
            'overlay_bg_end': 'rgba(66,165,245,35)',
            'overlay_border': 'rgba(129,212,250,100)',
            'hover_bg_start': 'rgba(100,181,246,65)',
            'hover_bg_end': 'rgba(66,165,245,55)',
            'hover_border': 'rgba(129,212,250,130)',
            'text_primary': 'rgba(255,255,255,250)',
            'text_secondary': 'rgba(255,255,255,220)',
            'text_tertiary': 'rgba(255,255,255,200)',
            'button_bg': 'rgba(100,181,246,30)',
            'button_hover': 'rgba(100,181,246,45)',
            'dialog_bg': 'rgba(13,71,161,250)',
            'progress_low': 'rgba(244,143,177,220)',
            'progress_mid': 'rgba(255,213,79,220)',
            'progress_high': 'rgba(129,212,250,220)',
        },
        'Sunset Orange': {
            'name': 'Sunset Orange',
            'overlay_bg_start': 'rgba(255,183,77,45)',
            'overlay_bg_end': 'rgba(255,167,38,35)',
            'overlay_border': 'rgba(255,204,128,100)',
            'hover_bg_start': 'rgba(255,183,77,65)',
            'hover_bg_end': 'rgba(255,167,38,55)',
            'hover_border': 'rgba(255,204,128,130)',
            'text_primary': 'rgba(255,255,255,250)',
            'text_secondary': 'rgba(255,255,255,220)',
            'text_tertiary': 'rgba(255,255,255,200)',
            'button_bg': 'rgba(255,183,77,30)',
            'button_hover': 'rgba(255,183,77,45)',
            'dialog_bg': 'rgba(191,54,12,250)',
            'progress_low': 'rgba(239,83,80,220)',
            'progress_mid': 'rgba(255,213,79,220)',
            'progress_high': 'rgba(255,183,77,220)',
        },
        'Light Overlay': {
            'name': 'Light Overlay',
            'overlay_bg_start': 'rgba(255,255,255,20)',
            'overlay_bg_end': 'rgba(250,250,250,15)',
            'overlay_border': 'rgba(200,200,200,80)',
            'hover_bg_start': 'rgba(255,255,255,40)',
            'hover_bg_end': 'rgba(250,250,250,30)',
            'hover_border': 'rgba(180,180,180,110)',
            'text_primary': 'rgba(33,33,33,250)',
            'text_secondary': 'rgba(66,66,66,220)',
            'text_tertiary': 'rgba(100,100,100,200)',
            'button_bg': 'rgba(220,220,220,30)',
            'button_hover': 'rgba(200,200,200,45)',
            'dialog_bg': 'rgba(255,255,255,250)',
            'progress_low': 'rgba(244,67,54,220)',
            'progress_mid': 'rgba(255,193,7,220)',
            'progress_high': 'rgba(76,175,80,220)',
        },
        'Midnight Blue': {
            'name': 'Midnight Blue',
            'overlay_bg_start': 'rgba(13,27,42,50)',
            'overlay_bg_end': 'rgba(27,38,59,40)',
            'overlay_border': 'rgba(65,105,225,100)',
            'hover_bg_start': 'rgba(13,27,42,70)',
            'hover_bg_end': 'rgba(27,38,59,60)',
            'hover_border': 'rgba(65,105,225,130)',
            'text_primary': 'rgba(255,255,255,250)',
            'text_secondary': 'rgba(220,230,255,220)',
            'text_tertiary': 'rgba(200,210,235,200)',
            'button_bg': 'rgba(65,105,225,30)',
            'button_hover': 'rgba(65,105,225,45)',
            'dialog_bg': 'rgba(13,27,42,250)',
            'progress_low': 'rgba(220,20,60,220)',
            'progress_mid': 'rgba(255,215,0,220)',
            'progress_high': 'rgba(100,149,237,220)',
        },
    }
    
    def __init__(self, theme_name='Dark Glassmorphic'):
        # Ensure attribute exists even if provided theme is invalid
        self.current_theme = 'Dark Glassmorphic'
        self.set_theme(theme_name)
        self.auto_switch_enabled = False  # Disable auto-switching to preserve user choice
        
    def get_theme(self, theme_name=None):
        """Get theme colors"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.THEMES.get(theme_name, self.THEMES['Dark Glassmorphic'])
        
    def set_theme(self, theme_name):
        """Set current theme"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            return True
        return False
        
    def get_theme_names(self):
        """Get list of available theme names"""
        return list(self.THEMES.keys())
        
    def get_overlay_stylesheet(self, theme_name=None):
        """Get overlay window stylesheet for the current theme"""
        theme = self.get_theme(theme_name)
        
        return f"""
            #overlayContainer {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme['overlay_bg_start']},
                    stop:1 {theme['overlay_bg_end']}
                );
                border-radius: 12px;
                border: 1px solid {theme['overlay_border']};
            }}
            #hoverBackground {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme['hover_bg_start']},
                    stop:1 {theme['hover_bg_end']}
                );
                border-radius: 14px;
                border: 1.5px solid {theme['hover_border']};
            }}
        """
        
    def get_dialog_stylesheet(self, theme_name=None):
        """Get dialog stylesheet for the current theme"""
        theme = self.get_theme(theme_name)
        
        return f"""
            QDialog {{ 
                background: {theme['dialog_bg']}; 
                border: 1px solid {theme['overlay_border']}; 
                border-radius: 12px; 
            }}
            QLabel {{ 
                color: {theme['text_primary']}; 
                font-size: 12px; 
                font-weight: 600; 
                background: transparent; 
            }}
            QSpinBox {{ 
                background: rgba(255,255,255,15); 
                color: {theme['text_primary']}; 
                border: 1px solid {theme['overlay_border']}; 
                border-radius: 6px; 
                padding: 8px; 
                font-size: 11px; 
                min-height: 28px; 
            }}
            QCheckBox {{ 
                color: {theme['text_primary']}; 
                font-size: 11px; 
            }}
            QCheckBox::indicator {{ 
                width: 18px; 
                height: 18px; 
                border-radius: 4px; 
                border: 1px solid {theme['overlay_border']}; 
                background: rgba(255,255,255,15); 
            }}
            QCheckBox::indicator:checked {{ 
                background: rgba(71,160,232,255); 
            }}
            QPushButton {{ 
                background: {theme['button_bg']}; 
                color: {theme['text_primary']}; 
                border: 1px solid {theme['overlay_border']}; 
                border-radius: 6px; 
                padding: 10px 20px; 
                font-size: 11px; 
                min-height: 32px; 
            }}
            QPushButton:hover {{ 
                background: {theme['button_hover']}; 
            }}
            QPushButton#primaryButton {{ 
                background: rgba(71,160,232,255); 
            }}
            QPushButton#resetButton {{ 
                background: rgba(232,71,71,200); 
            }}
            QPushButton#resetButton:hover {{ 
                background: rgba(232,71,71,255); 
            }}
            QComboBox {{
                background: rgba(255,255,255,15);
                color: {theme['text_primary']};
                border: 1px solid {theme['overlay_border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
                min-height: 28px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {theme['text_primary']};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background: {theme['dialog_bg']};
                color: {theme['text_primary']};
                selection-background-color: {theme['button_hover']};
                border: 1px solid {theme['overlay_border']};
                border-radius: 4px;
            }}
        """
        
    def get_progress_colors(self, theme_name=None):
        """Get progress bar colors"""
        theme = self.get_theme(theme_name)
        return {
            'low': theme['progress_low'],
            'mid': theme['progress_mid'],
            'high': theme['progress_high'],
        }
