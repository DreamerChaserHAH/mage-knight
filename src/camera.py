import pygame

class Camera:
    def __init__(self, width, height, level_width, level_height):
        # Camera dimensions (typically screen size)
        self.width = width
        self.height = height
        
        # Total level dimensions
        self.level_width = level_width
        self.level_height = level_height
        
        # Camera position (top-left corner)
        self.x = 0
        self.y = 0
        
    def update(self, target):
        """
        Update camera position to follow target (usually the player).
        Target should have a rect attribute with a center attribute.
        """
        # Center the camera on the target
        target_center_x, target_center_y = target.rect.center
        
        # Calculate desired camera position (centered on target)
        desired_x = target_center_x - self.width // 2
        desired_y = target_center_y - self.height // 2
        
        # Clamp camera position to level boundaries
        self.x = max(0, min(desired_x, self.level_width - self.width))
        self.y = max(0, min(desired_y, self.level_height - self.height))
    
    def apply(self, entity):
        """
        Apply camera offset to an entity's position.
        Returns the position at which the entity should be drawn.
        Entity should have a rect attribute.
        """
        if hasattr(entity, 'rect'):
            return pygame.Rect(entity.rect.x - self.x, 
                             entity.rect.y - self.y,
                             entity.rect.width, 
                             entity.rect.height)
        else:
            # If it doesn't have a rect, assume it's a rect itself
            return pygame.Rect(entity.x - self.x,
                             entity.y - self.y, 
                             entity.width, 
                             entity.height)
