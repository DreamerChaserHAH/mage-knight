"""
This file adds the apply_knockback method to the Player class.
To use it, import this file in your main.py file before using the player.
"""
from entities.player import Player
from utils.audioplayer import play_audio_clip
from utils.utils import get_file_path, FILETYPE

# Define the knockback method
def apply_knockback(self, direction, force_x, force_y=0):
    """
    Apply a knockback force to the player when hit by an enemy
    
    Args:
        direction (int): Direction of knockback (1 for right, -1 for left)
        force_x (float): Horizontal knockback force
        force_y (float): Vertical knockback force (negative for upward)
    """
    # Set horizontal velocity for knockback
    self.vx = force_x * direction
    
    # Set vertical velocity (negative is up)
    self.vy = force_y
    
    # Ensure player is not considered on_ground during knockback
    self.on_ground = False
    
    # Optional: Play hurt sound if available
    #try:
        #play_audio_clip(get_file_path("hurt.wav", FILETYPE.AUDIO), 0.7)
    #except (FileNotFoundError, AttributeError):
        # If sound file or audio module not available, just print
    print("Player hurt!")

# Add the method to the Player class
Player.apply_knockback = apply_knockback
