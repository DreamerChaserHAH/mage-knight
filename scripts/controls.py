import pygame

class Controls:
    def __init__(self):
        # Default control scheme (WASD + Space)
        self.key_bindings = {
            'move_left': pygame.K_a,
            'move_right': pygame.K_d,
            'jump': pygame.K_SPACE,
            'move_up': pygame.K_w,    # For menu navigation or climbing
            'move_down': pygame.K_s,  # For menu navigation or crouching
            'attack': pygame.K_j,     # Add attack action
            'interact': pygame.K_e,   # Add interact action
            'pause': pygame.K_ESCAPE  # Add pause action
        }
        
        # Alternative key bindings (arrow keys)
        self.alt_key_bindings = {
            'move_left': pygame.K_LEFT,
            'move_right': pygame.K_RIGHT,
            'jump': pygame.K_UP,
            'move_up': pygame.K_UP,
            'move_down': pygame.K_DOWN,
            'attack': pygame.K_z,
            'interact': pygame.K_x,
            'pause': pygame.K_p
        }
        
        # Active bindings (default to the primary set)
        self.active_bindings = self.key_bindings.copy()
        
        # For tracking key states
        self.pressed_keys = {}
        self.just_pressed_keys = {}
        
    def update(self):
        """Update key states for this frame."""
        # Get the current keyboard state
        key_state = pygame.key.get_pressed()
        
        # Store previous frame's key states
        prev_pressed = self.pressed_keys.copy()
        
        # Reset the dictionaries
        self.pressed_keys = {}
        self.just_pressed_keys = {}
        
        # Update pressed keys
        for action, key in self.active_bindings.items():
            # Is the key currently pressed?
            self.pressed_keys[action] = key_state[key]
            
            # Was the key just pressed this frame?
            self.just_pressed_keys[action] = key_state[key] and not prev_pressed.get(action, False)
    
    def is_pressed(self, action):
        """Check if an action's key is currently pressed."""
        return self.pressed_keys.get(action, False)
    
    def is_just_pressed(self, action):
        """Check if an action's key was just pressed this frame (for single trigger actions)."""
        return self.just_pressed_keys.get(action, False)
    
    def switch_to_alternate_controls(self):
        """Switch to alternate control scheme (arrow keys)."""
        self.active_bindings = self.alt_key_bindings.copy()
        
    def switch_to_default_controls(self):
        """Switch back to default control scheme (WASD)."""
        self.active_bindings = self.key_bindings.copy()
    
    def toggle_control_scheme(self):
        """Toggle between default and alternate control schemes."""
        if self.active_bindings == self.key_bindings:
            self.switch_to_alternate_controls()
        else:
            self.switch_to_default_controls()
    
    def get_key_name(self, action):
        """Get the name of the key bound to an action."""
        key = self.active_bindings.get(action)
        if key:
            return pygame.key.name(key).upper()
        return "NONE"
