import pygame
import random

from pygame import Rect
from utils.controls import Controls

from utils.audioplayer import play_audio_clip
from utils.utils import FILETYPE, load_image,get_file_path

from camera import Camera

class Particle:
    def __init__(self, pos):
        self.x, self.y = pos
        self.size = random.randint(2, 5)
        self.color = (200, 200, 200)
        self.lifetime = random.randint(20, 50)
        self.velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        self.size -= 0.1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))


class FootStepAudioPlayer:
    def __init__(self):
        self.last_play_time = 0
        self.play_interval = 300
        self.playing_side = "l"
        self.current_audio_index = 0;

    def increase_audio_index(self):
        self.current_audio_index = (self.current_audio_index + 1) % 3

    def play(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_play_time > self.play_interval:
            play_audio_clip(get_file_path('footsteps/footstep-'+self.playing_side+str(self.current_audio_index)+'.ogg', FILETYPE.AUDIO))
            if self.playing_side == "l":
                self.playing_side = "r"
            else:
                self.playing_side = "l"
                self.increase_audio_index()
            self.last_play_time = current_time

class Sword:
    def __init__(self, x, y, x_offset, y_offset, camera: Camera):

        self.sword_idle = load_image('images/sword/Sword-Idle.png')
        self.sword_attack = load_image('images/sword/Sword-Attack.png')

        self.x = x
        self.y = y
        self.x_offset = x_offset
        self.y_offset = y_offset

        self.sword_idle_frames = []
        for i in range(6):
            frame = self.sword_idle.subsurface(pygame.Rect(i * 16, 0, 16, 16))
            frame = pygame.transform.scale(frame, (16 * 2, 16 * 2))
            self.sword_idle_frames.append(frame)
        
        self.sword_attack_frames = []
        for i in range(6):
            frame = self.sword_attack.subsurface(pygame.Rect(i * 16, 0, 16, 16))
            frame = pygame.transform.scale(frame, (16 * 2, 16 * 2))
            self.sword_attack_frames.append(frame)
        

        self.current_frame = 0
        self.image = self.sword_idle_frames[self.current_frame]

        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_attacking = False

        self.animation_timer = 0
        self.animation_interval = 1000 / 15
        self.last_update_time = 0

        self.camera = camera
    
    def update(self, player_rect, is_looking_right):
        self.rect.center = (player_rect.centerx + (self.x_offset if is_looking_right else -self.x_offset), player_rect.centery + self.y_offset)

        self.animation_timer += pygame.time.get_ticks() - self.last_update_time
        self.last_update_time = pygame.time.get_ticks()
        if self.is_attacking and self.animation_timer >= self.animation_interval:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.sword_attack_frames)
            self.image = self.sword_attack_frames[self.current_frame]
            if self.current_frame == 5:
                self.is_attacking = False
                self.image = self.sword_idle_frames[0]
                self.current_frame = 0
    
    def attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.current_frame = 0
            play_audio_clip(get_file_path("sword.wav", FILETYPE.AUDIO), 2)

    def draw(self, surface, is_looking_right):
        render_rect = self.camera.apply(self)
        surface.blit(pygame.transform.flip(self.image, not is_looking_right, False), render_rect.topleft)

class Player:
    def __init__(self, x, y, controls, camera: Camera):
        # Store initial position as spawn point
        self.spawn_x = x
        self.spawn_y = y
        
        # Load the player sprite from assets folder
        self.footstep_particles = []
        self.normal_idle = load_image('images/player/Normal-Idle.png')
        self.normal_moving = load_image('images/player/Normal-Moving.png')
        self.demon_idle = load_image('images/player/Demon-Idle.png')
        self.demon_moving = load_image('images/player/Demon-Moving.png')

        if self.normal_idle is None:
            self.normal_idle = pygame.Surface((16 * 6, 16))
            self.normal_idle.fill((255, 255, 255))

        if self.normal_moving is None:
            self.normal_moving = pygame.Surface((16 * 6, 16))
            self.normal_moving.fill((255, 255, 255))
        
        if self.demon_idle is None:
            self.demon_idle = pygame.Surface((16 * 6, 16))
            self.demon_idle.fill((255, 255, 255))
        
        if self.demon_moving is None:
            self.demon_moving = pygame.Surface((16 * 6, 16))
            self.demon_moving.fill((255, 255, 255))
        
        self.normal_idle_frames = []
        for i in range(6):
            frame = self.normal_idle.subsurface(pygame.Rect(i * 16, 0, 16, 16))
            frame = pygame.transform.scale(frame, (16 * 4, 16 * 4))
            self.normal_idle_frames.append(frame)
        
        self.normal_moving_frames = []
        for i in range(6):
            frame = self.normal_moving.subsurface(pygame.Rect(i * 16, 0, 16, 16))
            frame = pygame.transform.scale(frame, (16 * 4, 16 * 4))
            self.normal_moving_frames.append(frame)
        
        self.demon_idle_frames = []
        for i in range(6):
            frame = self.demon_idle.subsurface(pygame.Rect(i * 16, 0, 16, 16))
            frame = pygame.transform.scale(frame, (16 * 4, 16 * 4))
            self.demon_idle_frames.append(frame)
        
        self.demon_moving_frames = []
        for i in range(6):
            frame = self.demon_moving.subsurface(pygame.Rect(i * 16, 0, 16, 16))
            frame = pygame.transform.scale(frame, (16 * 4, 16 * 4))
            self.demon_moving_frames.append(frame)
        
        self.current_frame = 0
        self.image = self.normal_idle_frames[self.current_frame]
        # Fallback if loading failed
        if self.image is None:
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 255, 255))  # White color
            
        self.rect = self.image.get_rect(topleft=(x, y))

        # Player velocity
        self.vx = 0
        self.vy = 0

        # Used to track if we're on the ground
        self.on_ground = False
        
        # Constants
        self.SPEED = 4
        self.GRAVITY = 1
        self.JUMP_SPEED = -20

        # Animation timer
        self.last_update_time = 0
        self.animation_timer = 0
        self.animation_interval = 1000 / 6  # 6 FPS
        self.is_facing_right = True
        self.is_moving = False
        self.current_frames = self.normal_idle_frames

        self.health = 100

        self.footstep_audio_player = FootStepAudioPlayer()

        self.controls = controls
        self.camera = camera

        self.sword = Sword(self.rect.x, self.rect.y, 20, 5, camera)

    def handle_input(self):
        """Check input using the controls system."""
        
        self.vx = 0
        self.current_frames = self.normal_idle_frames
        self.is_moving = False
        
        if self.controls:
            # Using controls system

            if self.controls.is_pressed('move_left'):
                self.vx = -self.SPEED
                self.is_facing_right = False
                self.current_frames = self.normal_moving_frames
                self.is_moving = True
                
            if self.controls.is_pressed('move_right'):
                self.vx = self.SPEED
                self.is_facing_right = True
                self.current_frames = self.normal_moving_frames
                self.is_moving = True

            # Jump only if on the ground
            if self.controls.is_pressed('jump') and self.on_ground:
                self.vy = self.JUMP_SPEED
                play_audio_clip(get_file_path('jump.wav', FILETYPE.AUDIO))
            
            if self.controls.is_pressed('attack'):
                self.sword.attack()
        else:
            # Fallback to direct key checking if controls not provided
            keys = pygame.key.get_pressed()

            if keys[pygame.K_a]:
                self.vx = -self.SPEED
                self.is_facing_right = False
                self.current_frames = self.normal_moving_frames
                self.is_moving = True
                
            if keys[pygame.K_d]:
                self.vx = self.SPEED
                self.is_facing_right = True
                self.current_frames = self.normal_moving_frames
                self.is_moving = True

            # Jump only if on the ground
            if keys[pygame.K_w] and self.on_ground:
                self.vy = self.JUMP_SPEED
                play_audio_clip(get_file_path('jump.wav', FILETYPE.AUDIO))

            # Jump only if on the ground
            if keys[pygame.K_w] and self.on_ground:
                self.vy = self.JUMP_SPEED
                play_audio_clip(get_file_path('jump.wav', FILETYPE.AUDIO))

    def apply_gravity(self):
        """Apply gravity to vy."""
        self.vy += self.GRAVITY

    def move_and_collide(self, tiles):
        """
        Move the player by (vx, vy). Then check collision with tiles.
        We'll handle x and y axes separately for reliable collisions.
        """
        # Move horizontally
        self.rect.x += self.vx
        # Check collisions on the X axis
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vx > 0:  # moving right
                    self.rect.right = tile.rect.left
                elif self.vx < 0:  # moving left
                    self.rect.left = tile.rect.right

        # Move vertically
        self.rect.y += self.vy
        # Check collisions on the Y axis
        self.on_ground = False  # We'll set this to True if we land on something
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vy > 0:  # falling down
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:  # moving up
                    self.rect.top = tile.rect.bottom
                    self.vy = 0
    
    def check_death(self, level_height, death_zones=None):
        """Check if player has died from falling or hitting a death zone."""
        # Die if fallen off the level
        if self.rect.y > level_height:
            self.die()
        
        # Check for collision with death zones if provided
        if death_zones:
            for zone in death_zones:
                if self.rect.colliderect(zone):
                    self.die()
    
    def die(self):
        """Handle player death."""
        if not self.is_dead:
            self.is_dead = True
            self.respawn_timer = 0
            # You could add sound effects or death animation here
    
    def respawn(self):
        """Reset player to spawn position."""
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.vx = 0
        self.vy = 0
        self.is_dead = False
        # You could add spawn animation or invulnerability frames here
    
    def update(self, tiles):
            
        # 1. Handle keyboard input (movement, jump)
        self.handle_input()

        # 2. Gravity
        self.apply_gravity()

        # 3. Move and collide
        self.move_and_collide(tiles)

        # 4. Update animation frame
        self.animation_timer += pygame.time.get_ticks() - self.last_update_time
        self.last_update_time = pygame.time.get_ticks()
        if self.animation_timer >= self.animation_interval:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.normal_idle_frames)
            self.image = self.current_frames[self.current_frame]
            if self.is_moving and self.on_ground:
                self.footstep_audio_player.play()
                self.footstep_particles.append(Particle((self.rect.centerx, self.rect.bottom)))
        
        self.sword.update(self.rect, self.is_facing_right)
        


    def draw(self, surface):
        render_rect = self.camera.apply(self)
        surface.blit(pygame.transform.flip(self.image, not self.is_facing_right, False), render_rect.topleft)
        self.sword.draw(surface, self.is_facing_right)
        for particle in self.footstep_particles:
            particle.update()
            particle.draw(surface)

