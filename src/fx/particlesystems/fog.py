import pygame
from utils.utils import load_image
import random

class Fog:
    """
    Continuously generate slow moving fog that moves across the screen
    """
    def __init__(self, screen_width, screen_height, x=0, y=0):
        # Load fog image
        self.image = load_image('images/fog/fog.png', use_alpha=True)
        self.image.set_alpha(40)

         # Fallback if loading failed
        if self.image is None:
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 255, 255))  # White color
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x_float = self.rect.x
        self.screen_width = screen_width
        # Set initial speed
        self.speed = 0.2
    
    def update(self):
        self.x_float = self.x_float + self.speed
        self.rect.x = int(self.x_float)
        if(self.rect.x > self.screen_width):
            self.rect.x = 0
            self.x_float = -200

    def draw(self, screen):
        # Draw the fog image
        screen.blit(self.image, self.rect, special_flags=pygame.BLEND_ALPHA_SDL2)
        # Set the alpha value for the fog image

class FogManager:
    """
    manage all of the fog sprites
    there will be around 20 fog sprites
    """
    def __init__(self, screen_width, screen_height, num_fog_sprites):
        self.fog_sprites = []
        for i in range(num_fog_sprites):
            x = random.randint(0, screen_width - 1)
            y = 0 
            fog = Fog(screen_width, screen_height, x, y)
            self.fog_sprites.append(fog)
    
    def draw(self, screen):
        for fog in self.fog_sprites:
            fog.draw(screen)
    
    def update(self):
        i = 0
        for fog in self.fog_sprites:
            i = i + 1
            fog.update()