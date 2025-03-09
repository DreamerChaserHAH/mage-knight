import pygame
import os
from enum import Enum

class FILETYPE(Enum):
    IMAGE = 0
    AUDIO = 1

def get_file_path(filename, type: FILETYPE):
    if type == FILETYPE.IMAGE:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, '../assets', filename)
    elif type == FILETYPE.AUDIO:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, '../assets/audio', filename)

def load_image(filename, use_alpha=True):
    """
    Helper function to load images with proper error handling.
    Returns the loaded image or None if loading failed.
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, '../assets', filename)

        if use_alpha:
            return pygame.image.load(filepath).convert_alpha()
        else:
            return pygame.image.load(filepath).convert()
    except (pygame.error, FileNotFoundError) as e:
        print(f"Could not load image {filename}: {e}")
        return None


# ======================= FIXED MAP GENERATION LOGIC =======================
def parse_map(level_map, tile_size, tile_class):
    """
    Parse the level map and create corresponding game objects.
    
    Args:
        level_map (list): List of strings representing the level layout
        tile_size (int): Size of each tile in pixels
        tile_class (class): Class to use for creating tile objects
    
    Returns:
        tuple: (tiles, player_spawn, enemy_spawns, death_zones)
            - tiles: List of Tile objects
            - player_spawn: (x, y) position where player should spawn
            - enemy_spawns: List of (x, y) positions where enemies should spawn
            - death_zones: List of pygame.Rect objects representing death zones
    """
    tiles = []
    player_spawn = None
    enemy_spawns = []
    death_zones = []
    
    # Process each character in the map
    for row_index, row in enumerate(level_map):
        for col_index, cell in enumerate(row):
            # Calculate position
            x = col_index * tile_size
            y = row_index * tile_size
            
            # Process different tile types
            if cell == '#':
                # Regular platforms - pass both width and height as tile_size
                tiles.append(tile_class(x, y, tile_size, tile_size))
            elif cell == 'X':
                # Death zones
                death_zones.append(pygame.Rect(x, y, tile_size, tile_size))
            elif cell == 'S':
                # Player spawn point
                player_spawn = (x, y)
            elif cell == 'E':
                # Enemy spawn point
                enemy_spawns.append((x, y))
    
    return tiles, player_spawn, enemy_spawns, death_zones
# ===============================================================================

def load_level(level_data, tile_size, tile_class):
    """
    Given a list of strings, return a list of Tile objects for solid tiles.
    Each '#' in the level map is turned into a Tile with the size TILE_SIZE x TILE_SIZE.
    """
    tiles = []
    for row_index, row in enumerate(level_data):
        for col_index, char in enumerate(row):
            if char == '#':
                x = col_index * tile_size
                y = row_index * tile_size
                tile = tile_class(x, y, tile_size, tile_size)
                tiles.append(tile)
    return tiles
