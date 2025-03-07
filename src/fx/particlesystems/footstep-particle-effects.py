import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Footstep Particle Effects")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Particle class
class Particle:
    def __init__(self, pos):
        self.x, self.y = pos
        self.size = random.randint(2, 5)
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.lifetime = random.randint(20, 50)
        self.velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        self.size -= 0.1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

# Main loop
def main():
    clock = pygame.time.Clock()
    particles = []

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for _ in range(10):
                    particles.append(Particle(pygame.mouse.get_pos()))

        particles = [p for p in particles if p.lifetime > 0]

        for particle in particles:
            particle.update()
            particle.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()