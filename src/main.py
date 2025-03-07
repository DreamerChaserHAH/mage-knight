import pygame
import sys

# Import our modules

from entities.player import Player
from fx.particlesystems.fog import FogManager
from utils.controls import Controls
from entities.background import Background, draw_overlay
from entities.tile import Tile
from utils.utils import load_level, get_file_path, FILETYPE
from utils.audioplayer import play_background_music
from fx.particlesystems.fireflies import FireflyParticleSystem
from camera import Camera  # Add camera import

# --------------------------------------------------------------------------------
# CONFIG & LEVEL
# --------------------------------------------------------------------------------

# Screen dimensions and tile size
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TILE_SIZE = 32

# A much wider level map to enable continuous movement
# This level is wider than the screen, so we need a camera to follow the player
LEVEL_MAP = [
    "......................................................................................",
    "......................................................................................",
    "......................................................................................",
    "......................................................................................",
    "..............####.......#######............................####......................",
    ".......S..............................................................................",
    "......####........................######.............................................",
    "......................................................................................",
    "..............#####...........................................####....................",
    "......................................................................................",
    "#####..............................####...............................................",
    "######............................####...............................................",
    "#######################.............###############........##########################",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
]

# Calculate level dimensions based on the map
LEVEL_WIDTH = len(LEVEL_MAP[0]) * TILE_SIZE
LEVEL_HEIGHT = len(LEVEL_MAP) * TILE_SIZE

# --------------------------------------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------------------------------------

def main():
    pygame.init()
    
    pygame.mixer.init()
    pygame.mixer.set_num_channels(16)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("MAGE-KNIGHT")
    clock = pygame.time.Clock()

    # Initialize camera
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, LEVEL_WIDTH, LEVEL_HEIGHT)

    # Initialize controls system
    controls = Controls()

    firefly_particle_system = FireflyParticleSystem(SCREEN_WIDTH, SCREEN_HEIGHT, 10)
    fog_manager = FogManager(SCREEN_WIDTH, SCREEN_HEIGHT, 20)
    # Create background
    background = Background(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Load level geometry (list of Tile objects)
    tiles = load_level(LEVEL_MAP, TILE_SIZE, Tile)

    # Create a player at x=50, y=50
    player = Player(50, 50, controls, camera)
    
    play_background_music(get_file_path("background.mp3", FILETYPE.AUDIO))

    running = True
    while running:
    # 1. Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    controls.toggle_control_scheme()  # Allow toggling controls with Tab key
        
        # Update control states
        controls.update()
        
        # 2. Update game objects
        player.update(tiles)
        # Update camera to follow player
        camera.update(player)
        fog_manager.update()
        firefly_particle_system.update()

        # 3. Draw everything
        # Draw background
        background.draw(screen, player_rect=player.rect)

        # Draw the level tiles with camera offset
        for tile in tiles:
            # Apply camera offset to each tile
            tile_rect = camera.apply(tile)
            screen.blit(tile.image, tile_rect)

        fog_manager.draw(screen)
        player_render_rect = camera.apply(player)
        draw_overlay(SCREEN_WIDTH, SCREEN_HEIGHT, screen, player_rect=player_render_rect)
        
        # Draw the player with camera offset
        #player_rect = camera.apply(player)
        #screen.blit(pygame.transform.flip(player.image, not player.is_facing_right, False), player_rect.topleft)
        player.draw(screen)
        # Draw the sword with camera offset
        #sword_rect = camera.apply(player.sword)
        #screen.blit(pygame.transform.flip(player.sword.image, not player.is_facing_right, False), sword_rect.topleft)
        
        # Draw any footstep particles with camera offset
        for particle in player.footstep_particles:
            particle.update()
            # Draw at camera-adjusted position
            adjusted_x = particle.x - camera.x
            adjusted_y = particle.y - camera.y
            pygame.draw.circle(screen, particle.color, (int(adjusted_x), int(adjusted_y)), int(particle.size))
        
        firefly_particle_system.draw(screen)

        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
