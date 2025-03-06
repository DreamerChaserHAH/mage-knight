import pygame
from utils import load_image

class Tile:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        # Load tile image
        self.image = load_image('stile.png')
        
        # Default tile color as fallback
        self.color = (100, 100, 100)  # Gray
        
        # If image loaded successfully, scale it to match the tile size
        if self.image:
            self.image = pygame.transform.scale(self.image, (width, height))
        
    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the tile with camera offset applied."""
        draw_rect = pygame.Rect(
            self.rect.x - camera_x,
            self.rect.y - camera_y,
            self.rect.width,
            self.rect.height
        )
        
        if self.image:
            # Draw the tile image
            surface.blit(self.image, draw_rect)
        else:
            # Fallback to solid color rectangle
            pygame.draw.rect(surface, self.color, draw_rect)
