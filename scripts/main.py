import pygame
import sys

# Import our modules
from player import Player
from background import Background
from tile import Tile
from utils import load_level, get_file_path, FILETYPE
from audioplayer import play_background_music
from fireflies import FireflyParticleSystem

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

    firefly_particle_system = FireflyParticleSystem(SCREEN_WIDTH, SCREEN_HEIGHT, 10)

    # Create background
    background = Background(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Load level geometry (list of Tile objects)
    tiles = load_level(LEVEL_MAP, TILE_SIZE, Tile)

    # Create a player at x=50, y=50
    player = Player(50, 50)
    
    play_background_music(get_file_path("background.mp3", FILETYPE.AUDIO))

    running = True
    while running:
        # 1. Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # 2. Update game objects
        player.update(tiles)
        firefly_particle_system.update()

        # 3. Draw everything
        # Draw background
        background.draw(screen, player_rect=player.rect)

        # Draw the level tiles
        for tile in tiles:
            tile.draw(screen)

        # Draw the player
        player.draw(screen)
        firefly_particle_system.draw(screen)

        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
