import pygame
import random
import sys
import os

# Fix imports to work correctly within the project structure
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from utils.utils import load_image, get_file_path, FILETYPE
else:
    from utils.utils import load_image, get_file_path, FILETYPE

from utils.animationplayer import AnimationPlayer

class Enemy:
    """
    Enemy class for creating patrolling enemies that walk back and forth
    along a set path. Enemies will reverse direction when they hit obstacles
    or reach the end of their patrol path.
    """
    def __init__(self, x, y, width=64, height=64, patrol_distance=200):
        """Initialize a new enemy"""
        # Position and dimensions
        self.rect = pygame.Rect(x, y, width, height)
        self.spawn_x = x
        self.spawn_y = y
        
        # Movement variables
        self.direction = 1  # 1 for right, -1 for left
        self.speed = 1
        self.patrol_distance = patrol_distance
        self.is_facing_right = self.direction > 0
        
        # Physics variables
        self.vx = self.speed * self.direction
        self.vy = 0
        self.gravity = 0.5
        self.on_ground = False
        
        # Debug property
        self.debug_info = {
            "last_collision": None,
            "on_platform": False,
        }
        
        # ======================= ANIMATION SETUP - COMPLETELY NEW =======================
        # Create animation player - the ONLY animation system we'll use
        self.animation_player = AnimationPlayer()
        
        # Load walking animation
        self.animation_player.load_aseprite_animation(
            image_path="images/Enemy/Enemy0/enemy0_walking.png",
            json_path="images/Enemy/Enemy0/enemy0_walking.json",
            animation_name="walking"
        )
        
        # Load attack animation
        self.animation_player.load_aseprite_animation(
            image_path="images/Enemy/Enemy0/enemy0_attacking.png",
            json_path="images/Enemy/Enemy0/enemy0_attacking.json",
            animation_name="attack"
        )
        
        # Set scale to match desired dimensions
        self.animation_player.set_scale(width / 72, height / 88)
        
        # Set initial animation
        self.animation_player.play("walking")
        
        # State and attack properties
        self.state = "walking"  # Can be "walking" or "attacking"
        self.detection_range = 200  # Range to detect the player (in pixels)
        self.attack_speed = 3  # Speed multiplier during attack
        self.attack_duration = 45  # Frames that the attack lasts
        self.attack_cooldown = 0  # Frames until next attack is allowed
        self.cooldown_duration = 60  # Frames between attacks
        self.attack_timer = 0  # Current frame in attack sequence
        # ===============================================================================
    
    def update(self, tiles, player=None):
        """Update enemy position, animation, and handle collisions"""
        # Player detection and state management
        if player and self.state != "attacking" and self.attack_cooldown <= 0:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = (dx**2 + dy**2)**0.5
            
            if distance <= self.detection_range:
                self.state = "attacking"
                self.attack_timer = self.attack_duration
                self.is_facing_right = dx > 0
                self.direction = 1 if self.is_facing_right else -1
                print(f"Enemy detected player at distance {distance:.1f}, initiating attack!")
        
        # Handle attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        # Apply gravity
        if not self.on_ground:
            self.vy += self.gravity
            
        # Set velocity based on state
        if self.state == "attacking":
            self.vx = self.speed * self.direction * self.attack_speed
            self.attack_timer -= 1
            
            # Return to walking when attack finishes
            if self.attack_timer <= 0:
                self.state = "walking"
                self.attack_cooldown = self.cooldown_duration
                print("Attack finished, returning to patrol")
        else:
            self.vx = self.speed * self.direction
        
        # Move horizontally and handle collisions
        self.rect.x += self.vx
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
        
        # Move vertically and handle collisions
        self.rect.y += self.vy
        self.on_ground = False
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
        
        # Check for platform edges
        if self.on_ground and not horizontal_collision:
            look_ahead_dist = 10
            check_x = self.rect.x + (look_ahead_dist * self.direction)
            check_rect = pygame.Rect(check_x, self.rect.bottom, self.rect.width, 5)
            
            has_ground_ahead = False
            for tile in tiles:
                if check_rect.colliderect(tile.rect):
                    has_ground_ahead = True
                    break
            
            if not has_ground_ahead:
                self.direction *= -1
                self.is_facing_right = not self.is_facing_right
        
        # Check patrol distance limits
        if self.rect.x > self.spawn_x + self.patrol_distance:
            self.direction = -1
            self.is_facing_right = False
        elif self.rect.x < self.spawn_x - self.patrol_distance:
            self.direction = 1
            self.is_facing_right = True
        
        # ======================= UPDATE ANIMATION STATE BASED ON ENEMY STATE =======================
        # Choose animation based on state
        if self.state == "attacking":
            self.animation_player.play("attack")
        else:
            self.animation_player.play("walking")
        
        # Update flip direction for animation
        self.animation_player.set_flip(flip_x=self.is_facing_right)
        
        # Update animation player
        self.animation_player.update()
        # ===============================================================================
        
        # Check for out of bounds
        if self.rect.y > 2000:
            print(f"Enemy at ({self.rect.x}, {self.rect.y}) fell out of bounds")
            return False  # Signal that this enemy should be removed
            
        return True  # Enemy is still valid
    
    def check_player_collision(self, player):
        """Check if enemy collides with player"""
        return self.rect.colliderect(player.rect)
    
    def draw(self, surface, camera):
        """Draw the enemy with camera offset"""
        # Get camera-adjusted position
        enemy_rect = camera.apply(self)
        
        # ======================= DRAW ONLY USING ANIMATION PLAYER =======================
        # This is the ONLY drawing code - no direct surface blits or old animation code
        self.animation_player.draw(surface, enemy_rect.topleft)
        # ===============================================================================