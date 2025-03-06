import json
import os
import pygame

class Config:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_dir, 'config.json')
        
        # Default settings
        self.settings = {
            'controls': {
                'move_left': pygame.K_a,
                'move_right': pygame.K_d,
                'jump': pygame.K_SPACE,
                'move_up': pygame.K_w,
                'move_down': pygame.K_s,
                'attack': pygame.K_j,
                'interact': pygame.K_e,
                'pause': pygame.K_ESCAPE
            },
            'sound': {
                'music_volume': 0.7,
                'sfx_volume': 1.0
            },
            'graphics': {
                'fullscreen': False,
                'resolution': (640, 480)
            }
        }
        
        # Load configuration if file exists
        self.load_config()
    
    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings, keeping defaults for any missing keys
                    for category, values in loaded_settings.items():
                        if category in self.settings:
                            self.settings[category].update(values)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_controls(self):
        """Get the current control settings."""
        return self.settings['controls']
    
    def update_controls(self, controls_dict):
        """Update control settings."""
        self.settings['controls'].update(controls_dict)
        self.save_config()
