import pygame
import sys

# Fix import to use relative imports within the same package
from entities.player import Player
from fx.particlesystems.fog import FogManager
from utils.controls import Controls
from entities.background import Background, draw_overlay
from entities.tile import Tile
# ======================= IMPROVED MAP GENERATION IMPORT =======================
from utils.utils import parse_map, get_file_path, FILETYPE
# ===============================================================================
from utils.audioplayer import play_background_music
from fx.particlesystems.fireflies import FireflyParticleSystem
from camera import Camera  # Add camera import

# ======================= PLAYER KNOCKBACK IMPLEMENTATION - NEW IMPORT =======================
# Import the player extension to add the knockback method
import entities.player_extension  # This adds the apply_knockback method to Player class
# ===============================================================================

# ======================= ENEMY IMPLEMENTATION - FIXED IMPORT =======================
# Correct import path for Enemy class
from entities.enemy import Enemy  # Import from entities package without src prefix
# ===============================================================================

# --------------------------------------------------------------------------------
# CONFIG & LEVEL
# --------------------------------------------------------------------------------

# Screen dimensions and tile size
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TILE_SIZE = 32

# ======================= IMPROVED MAP CONFIGURATION =======================
# A much wider level map with specific entity markers
# S = Player spawn point
# E = Enemy spawn point
# X = Death zone (causes player to die on contact)
# # = Platform/solid tile
LEVEL_MAP = [
    "......................................................................................",
    "......................................................................................",
    "......................................................................................",
    "......................................................................................",
    "..............####.......#######............................####......................",
    ".......S..............................................................................",
    "......####....########################.........E..............................E.....",
    "......................................................................................",
    "..............#####...........................................####....................",
    "......................................................................................",
    "#####..............................####...............................................",
    "######.............E.............####...............................................",
    "#######################....#####################........##########################",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
]
# ===============================================================================

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

    # ======================= IMPROVED MAP LOADING =======================
    # Parse level map to get tiles, spawn positions, and death zones
    tiles, player_spawn, enemy_spawns, death_zones = parse_map(LEVEL_MAP, TILE_SIZE, Tile)

    # Create player at spawn position or default position if no spawn point defined
    if player_spawn:
        player = Player(player_spawn[0], player_spawn[1], controls, camera)
    else:
        # Default spawn position if no 'S' marker in map
        player = Player(50, 50, controls, camera)
    
    # Create enemies at spawn positions with varying patrol distances
    enemies = []
    patrol_distances = [150, 200, 250]  # Different patrol distances for variety
    
    for i, spawn in enumerate(enemy_spawns):
        patrol = patrol_distances[i % len(patrol_distances)]  # Cycle through patrol distances
        enemies.append(Enemy(spawn[0], spawn[1], patrol_distance=patrol))
    # ===============================================================================
    
    play_background_music(get_file_path("background.mp3", FILETYPE.AUDIO))

    # ======================= KNOCKBACK IMPLEMENTATION - NEW VARIABLE =======================
    # Variable to track player invulnerability after being hit
    invulnerable_timer = 0
    invulnerable_duration = 60  # Frames of invulnerability after being hit (1 second at 60 FPS)
    # ===============================================================================

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
        
        # ======================= FIXED DEATH ZONE COLLISION DETECTION =======================
        # Check if player is in a death zone
        player_rect = player.rect
        for death_zone in death_zones:
            # Now death_zone is already a pygame.Rect so we can use it directly
            if player_rect.colliderect(death_zone):
                player.health = 0
                # Reset player to spawn position
                if player_spawn:
                    player.rect.x = player_spawn[0]
                    player.rect.y = player_spawn[1]
                print("Player hit a death zone!")
        # ===============================================================================
        
        # ======================= KNOCKBACK IMPLEMENTATION - UPDATED COLLISION =======================
        # Update invulnerability timer
        if invulnerable_timer > 0:
            invulnerable_timer -= 1
        
        # Update all enemies
        for enemy in enemies:
            enemy.update(tiles)
            
            # Check for player-enemy collision only if player is not invulnerable
            if invulnerable_timer <= 0 and enemy.check_player_collision(player):
                # Calculate knockback direction (away from enemy)
                knockback_dir = 1 if player.rect.centerx > enemy.rect.centerx else -1
                
                # Apply knockback to player
                player.apply_knockback(knockback_dir, 10, -8)  # Parameters: direction, horizontal force, vertical force
                
                # Start invulnerability period
                invulnerable_timer = invulnerable_duration
                
                # Decrease player health
                player.health -= 1
                if player.health <= 0:
                    player.die()
                
                # Optional: Display hit effect or play sound
                print("Player knocked back by enemy!")
        # ===============================================================================
        
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

        # ======================= ENEMY IMPLEMENTATION - NEW CODE =======================
        # Draw all enemies with camera offset
        for enemy in enemies:
            enemy.draw(screen, camera)
        # ===============================================================================
            
        fog_manager.draw(screen)
        player_render_rect = camera.apply(player)
        draw_overlay(SCREEN_WIDTH, SCREEN_HEIGHT, screen, player_rect=player_render_rect)
        
        # Draw the player with camera offset
        #player_rect = camera.apply(player)
        #screen.blit(pygame.transform.flip(player.image, not player.is_facing_right, False), player_rect.topleft)
        
        # ======================= KNOCKBACK IMPLEMENTATION - VISUAL INDICATOR =======================
        # Optional: Flash the player sprite when invulnerable
        visible = True
        if invulnerable_timer > 0:
            # Make player flash by alternating visibility every 5 frames
            visible = (invulnerable_timer // 5) % 2 == 0
        
        # Draw the player only if visible
        if visible:
            player.draw(screen)
        # ===============================================================================
        
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

        # ======================= FIXED DEATH ZONE VISUALIZATION (DEBUG ONLY) =======================
        # Uncomment to visualize death zones during debugging
        # for death_zone in death_zones:
        #     # Apply camera offset
        #     adjusted_rect = pygame.Rect(
        #         death_zone.x - camera.x, 
        #         death_zone.y - camera.y,
        #         death_zone.width, 
        #         death_zone.height
        #     )
        #     pygame.draw.rect(screen, (255, 0, 0), adjusted_rect, 1)
        # ===============================================================================
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
