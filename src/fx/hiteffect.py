import pygame
import random
import math

class HitEffect:
    """
    Class that represents a hit effect animation displayed when the player takes damage.
    The effect creates multiple particles that expand outward from the hit point.
    """
    def __init__(self, x, y, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.particles = []
        self.lifetime = 20  # Effect lasts for 20 frames
        self.current_frame = 0
        self.color = color
        
        # Create particles
        self.create_particles()
    
    def create_particles(self, count=15):
        """Create particles for the hit effect"""
        for _ in range(count):
            # Random angle and speed for each particle
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            size = random.uniform(2, 5)
            lifetime = random.randint(10, self.lifetime)
            
            # Calculate velocity components
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Add particle to list
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'vx': vx,
                'vy': vy,
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime
            })
    
    def update(self):
        """Update the hit effect animation"""
        self.current_frame += 1
        
        # Update each particle
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Gradually reduce size as lifetime decreases
            particle['size'] *= 0.95
            
            # Decrease lifetime
            particle['lifetime'] -= 1
    
    def draw(self, surface, camera=None):
        """Draw the hit effect on the given surface"""
        for particle in self.particles:
            # Skip particles that have expired
            if particle['lifetime'] <= 0:
                continue
                
            # Calculate alpha (fade out)
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            
            # Calculate position with camera offset if provided
            x, y = particle['x'], particle['y']
            if camera:
                x -= camera.x
                y -= camera.y
                
            # Create a surface for the particle with alpha
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            
            # Draw the particle
            pygame.draw.circle(
                particle_surface, 
                (*self.color, alpha),  # Color with alpha
                (particle['size'], particle['size']), 
                particle['size']
            )
            
            # Draw the particle on the main surface
            surface.blit(particle_surface, (x - particle['size'], y - particle['size']))
    
    def is_finished(self):
        """Check if the effect has completed its animation"""
        return self.current_frame > self.lifetime
