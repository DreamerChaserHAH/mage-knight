import pygame
import os
from enum import Enum

class FILETYPE(Enum):
    IMAGE = 0
    AUDIO = 1

def get_file_path(filename, type: FILETYPE):
    if type == FILETYPE.IMAGE:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'assets', filename)
    elif type == FILETYPE.AUDIO:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'assets/audio', filename)

def load_image(filename, use_alpha=True):
    """
    Helper function to load images with proper error handling.
    Returns the loaded image or None if loading failed.
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, 'assets', filename)
        
        if use_alpha:
            return pygame.image.load(filepath).convert_alpha()
        else:
            return pygame.image.load(filepath).convert()
    except (pygame.error, FileNotFoundError) as e:
        print(f"Could not load image {filename}: {e}")
        return None


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
