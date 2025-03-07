import pygame
import random
import math


class Firefly:
    def __init__(self, WIDTH, HEIGHT):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(2, 5)
        self.brightness = random.randint(100, 255)
        self.speed = random.uniform(0.5, 1.0)
        self.angle = random.uniform(0, 2 * math.pi)
        self.visible = True
        self.visibility_timer = random.randint(30, 300)
        self.fade_speed = random.uniform(1, 5)

    def move(self):
        # Add a small random angle change to simulate vibration
        self.angle += random.uniform(-0.1, 0.1)
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.x %= self.WIDTH
        self.y %= self.HEIGHT
        self.visibility_timer -= 1
        if self.visibility_timer <= 0:
            self.visible = not self.visible
            self.visibility_timer = random.randint(30, 300)

        if not self.visible:
            self.brightness -= self.fade_speed
            if self.brightness < 0:
                self.brightness = 0
        else:
            self.brightness += self.fade_speed
            if self.brightness > 255:
                self.brightness = 255

    def draw(self, screen):
        if self.brightness > 0:
            color = (200, 200, 200, int(self.brightness))  # Yellow color with alpha for brightness
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (self.size, self.size), self.size)
            screen.blit(surface, (int(self.x - self.size), int(self.y - self.size)))


class FireflyParticleSystem:
    def __init__(self, WIDTH, HEIGHT, num_fireflies):
        self.fireflies = [Firefly(WIDTH, HEIGHT) for _ in range(num_fireflies)]

    def update(self):
        for firefly in self.fireflies:
            firefly.move()

    def draw(self, screen):
        for firefly in self.fireflies:
            firefly.draw(screen)
