import pygame
from utils import load_image

class Background:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Load background image
        self.image = load_image('background.jpeg', use_alpha=False)
        
        # Default background color
        self.bg_color = (30, 30, 30)  # Dark gray
        
        # Store level dimensions
        #self.level_width = level_width
        #self.level_height = level_height
        
        # If image loaded successfully
        #if self.image:
            # Scale to fit the level size - this could be a large image
        #    self.image = pygame.transform.scale(self.image, (level_width, level_height))
        
    def draw(self, surface, player_rect):
        if self.image:
            # Draw the background image
            surface.blit(self.image, (0, 0))
        else:
            # Fallback to solid color
            surface.fill(self.bg_color)

        filter = pygame.surface.Surface((self.screen_width, self.screen_height))
        filter_color = (150, 150, 150, 0)
        filter.fill(filter_color)
        
        for i in range(20):
            radius = 150 - i * 5
            color_value = 75 - i * 3
            pygame.draw.circle(filter, (color_value, color_value, color_value, 0), (player_rect.centerx, player_rect.centery), radius)
        #for i in range(5):
            #trans = i * 30
            #pygame.draw.circle(filter, (i, i, i, 0), (player_rect.centerx, player_rect.centery), i * 40)
        surface.blit(filter, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
