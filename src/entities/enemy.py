import pygame
import random
import sys
import os

# Fix imports to work correctly within the project structure
# When running directly vs when imported from main.py
if __name__ == "__main__":
    # When run directly, we need to add parent directories to path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from utils.utils import load_image, get_file_path, FILETYPE
else:
    # When imported from main.py, use relative imports
    from utils.utils import load_image, get_file_path, FILETYPE

class Enemy:
    """
    Enemy class for creating patrolling enemies that walk back and forth
    along a set path. Enemies will reverse direction when they hit obstacles
    or reach the end of their patrol path.
    """
    def __init__(self, x, y, width=64, height=64, patrol_distance=200):
        """
        Initialize a new enemy
        
        Args:
            x (int): Starting x-coordinate
            y (int): Starting y-coordinate
            width (int): Enemy width in pixels
            height (int): Enemy height in pixels
            patrol_distance (int): Maximum distance the enemy will move from its spawn point
        """
        # Position and dimensions
        self.rect = pygame.Rect(x, y, width, height)
        self.spawn_x = x
        self.spawn_y = y
        
        # Load enemy walking animation
        self.walking_image = load_image('images/Enemy/Enemy0/enemy0_walking.png')
        
        if self.walking_image is None:
            # Fallback if image loading fails
            self.walking_image = pygame.Surface((width, height))
            self.walking_image.fill((255, 0, 0))  # Red color for enemy
        
        # Create animation frames from spritesheet
        self.walking_frames = []
        # Using the frame dimensions from the JSON file
        frame_width = 72
        frame_height = 88
        
        for i in range(2):  # Two frames based on the JSON
            frame = self.walking_image.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            # Scale to desired size
            frame = pygame.transform.scale(frame, (width, height))
            self.walking_frames.append(frame)
        
        # Animation variables
        self.current_frame = 0
        self.animation_speed = 0.1
        self.animation_timer = 0
        
        # Movement variables
        self.direction = 1  # 1 for right, -1 for left
        self.speed = 1
        self.patrol_distance = patrol_distance
        # Fix: Initial facing should match the initial movement direction
        # If direction is 1 (moving right), is_facing_right should be True
        # If direction is -1 (moving left), is_facing_right should be False
        self.is_facing_right = self.direction > 0
        
        # Physics variables
        self.vx = self.speed * self.direction
        self.vy = 0
        self.gravity = 0.5
        self.on_ground = False
        
        # Set initial image
        self.image = self.walking_frames[self.current_frame]
        
        # ======================= ADDED DEBUG PROPERTY =======================
        # For debugging collision issues
        self.debug_info = {
            "last_collision": None,
            "on_platform": False,
        }
        # ===============================================================================
    
    def update(self, tiles, player=None):
        """
        Update enemy position, animation, and handle collisions
        
        Args:
            tiles (list): List of Tile objects to check for collisions
            player (Player): Player object to check for proximity
        """
        # Apply gravity
        if not self.on_ground:
            self.vy += self.gravity
        
        # Set horizontal velocity based on direction
        self.vx = self.speed * self.direction
        
        # Move horizontally
        self.rect.x += self.vx
        
        # ======================= IMPROVED HORIZONTAL COLLISION HANDLING =======================
        # Check horizontal collisions
        horizontal_collision = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                horizontal_collision = True
                if self.vx > 0:  # moving right
                    self.rect.right = tile.rect.left
                    self.direction = -1
                    self.is_facing_right = False
                elif self.vx < 0:  # moving left
                    self.rect.left = tile.rect.right
                    self.direction = 1
                    self.is_facing_right = True
                
                self.debug_info["last_collision"] = "horizontal"
        # ===============================================================================
        
        # Move vertically
        self.rect.y += self.vy
        self.on_ground = False
        
        # ======================= IMPROVED VERTICAL COLLISION HANDLING =======================
        # Check vertical collisions
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vy > 0:  # falling down
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                    self.on_ground = True
                    self.debug_info["on_platform"] = True
                    self.debug_info["last_collision"] = "vertical_bottom"
                elif self.vy < 0:  # moving up
                    self.rect.top = tile.rect.bottom
                    self.vy = 0
                    self.debug_info["last_collision"] = "vertical_top"
        # ===============================================================================
        
        # ======================= IMPROVED PLATFORM EDGE DETECTION =======================
        # Check if we're about to walk off a platform edge
        if self.on_ground and not horizontal_collision:
            # Look ahead to see if there's ground beneath the enemy's next step
            look_ahead_dist = 10  # pixels to look ahead
            check_x = self.rect.x + (look_ahead_dist * self.direction)
            check_rect = pygame.Rect(check_x, self.rect.bottom, self.rect.width, 5)  # 5 pixels down
            
            has_ground_ahead = False
            for tile in tiles:
                if check_rect.colliderect(tile.rect):
                    has_ground_ahead = True
                    break
            
            # If there's no ground ahead, turn around
            if not has_ground_ahead:
                self.direction *= -1
                self.is_facing_right = not self.is_facing_right
                # print(f"Enemy detected edge at ({self.rect.x}, {self.rect.y}), turning around")
        # ===============================================================================
        
        # Check if enemy has reached patrol distance limit
        if self.rect.x > self.spawn_x + self.patrol_distance:
            self.direction = -1
            self.is_facing_right = False
        elif self.rect.x < self.spawn_x - self.patrol_distance:
            self.direction = 1
            self.is_facing_right = True
        
        # Only animate if on the ground (walking)
        if self.on_ground:
            # Update animation frame
            self.animation_timer += 1
            if self.animation_timer >= 10:  # Adjust timing as needed
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames)
                self.image = self.walking_frames[self.current_frame]
        
        # ======================= IMPROVED BOUNDARY CHECK =======================
        # Check if enemy has fallen too far (below screen)
        if self.rect.y > 2000:  # Arbitrary large value
            print(f"Enemy at ({self.rect.x}, {self.rect.y}) fell out of bounds")
            return False  # Signal that this enemy should be removed
            
        return True  # Enemy is still valid
        # ===============================================================================
    
    def check_player_collision(self, player):
        """
        Check if enemy collides with player
        
        Args:
            player (Player): The player object to check collision against
            
        Returns:
            bool: True if collision occurred, False otherwise
        """
        if self.rect.colliderect(player.rect):
            # Enemy has collided with player
            return True
        return False
    
    def draw(self, surface, camera):
        """
        Draw the enemy with camera offset
        
        Args:
            surface (pygame.Surface): The surface to draw on
            camera (Camera): The camera object for position adjustments
        """
        # Get camera-adjusted position
        enemy_rect = camera.apply(self)
        
        # Fix: Correctly flip the sprite based on movement direction
        # If enemy is facing right, don't flip; if facing left, flip horizontally
        # The issue might be that the sprites are already facing the correct way,
        # so we may need to adjust this logic
        
        # Try this first - invert the flip logic
        surface.blit(pygame.transform.flip(self.image, self.is_facing_right, False), enemy_rect.topleft)
        
        # If that doesn't work, try this alternative:
        # surface.blit(pygame.transform.flip(self.image, not self.is_facing_right, False), enemy_rect.topleft)