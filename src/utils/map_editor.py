"""
Simple map editor utility for Mage Knight game.
This allows you to visualize and edit game maps more easily.
"""

import pygame
import sys
import os

# Allow running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

class MapEditor:
    def __init__(self, map_data=None, tile_size=32):
        """
        Initialize the map editor
        
        Args:
            map_data (list): Optional initial map data as list of strings
            tile_size (int): Size of each tile in pixels
        """
        pygame.init()
        self.tile_size = tile_size
        
        # Default empty map if none provided
        if map_data is None:
            self.map_data = [
                "." * 20,
                "." * 20,
                "." * 20,
                "." * 20,
                "." * 20,
                "." * 20,
                "." * 20,
                "." * 20,
                "." * 20,
                "." * 20,
            ]
        else:
            self.map_data = map_data.copy()  # Make a copy to avoid modifying original
            
        # Calculate dimensions
        self.map_width = len(self.map_data[0])
        self.map_height = len(self.map_data)
        
        # Set up display
        self.screen_width = min(self.map_width * self.tile_size, 800)
        self.screen_height = min(self.map_height * self.tile_size, 600)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Mage Knight Map Editor")
        
        # Tile types and their colors
        self.tile_types = {
            '.': (0, 0, 0),       # Empty space (black)
            '#': (100, 100, 100), # Platform (gray)
            'S': (0, 255, 0),     # Player spawn (green)
            'E': (255, 0, 0),     # Enemy spawn (red)
            'X': (255, 0, 255),   # Death zone (purple)
        }
        
        # Current selected tile type
        self.current_tile = '#'
        
        # Camera position (for scrolling larger maps)
        self.camera_x = 0
        self.camera_y = 0
        
        # Font for info display
        self.font = pygame.font.SysFont(None, 24)
    
    def save_map(self, filename="map.txt"):
        """Save the current map to a file"""
        with open(filename, 'w') as f:
            for row in self.map_data:
                f.write(row + "\n")
        print(f"Map saved to {filename}")
    
    def load_map(self, filename="map.txt"):
        """Load a map from a file"""
        try:
            with open(filename, 'r') as f:
                self.map_data = [line.strip() for line in f.readlines()]
            self.map_width = len(self.map_data[0])
            self.map_height = len(self.map_data)
            print(f"Map loaded from {filename}")
        except Exception as e:
            print(f"Error loading map: {e}")
    
    def draw(self):
        """Draw the map and UI"""
        self.screen.fill((30, 30, 30))  # Dark gray background
        
        # Draw the visible portion of the map
        visible_width = self.screen_width // self.tile_size
        visible_height = self.screen_height // self.tile_size
        
        for y in range(visible_height):
            map_y = y + self.camera_y
            if map_y >= self.map_height:
                continue
                
            for x in range(visible_width):
                map_x = x + self.camera_x
                if map_x >= self.map_width:
                    continue
                    
                tile_type = self.map_data[map_y][map_x]
                color = self.tile_types.get(tile_type, (50, 50, 50))
                
                rect = pygame.Rect(
                    x * self.tile_size, 
                    y * self.tile_size,
                    self.tile_size, 
                    self.tile_size
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)
                
                # Draw letter for special tiles
                if tile_type in ['S', 'E', 'X']:
                    text = self.font.render(tile_type, True, (255, 255, 255))
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
        
        # Draw UI information
        info_text = f"Current Tile: {self.current_tile} | Arrow Keys: Scroll | 1-5: Change Tile Type | S: Save | L: Load"
        info_surface = self.font.render(info_text, True, (255, 255, 255))
        self.screen.blit(info_surface, (10, self.screen_height - 30))
    
    def run(self):
        """Main loop for the map editor"""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    # Tile selection
                    if event.key == pygame.K_1:
                        self.current_tile = '.'
                    elif event.key == pygame.K_2:
                        self.current_tile = '#'
                    elif event.key == pygame.K_3:
                        self.current_tile = 'S'
                    elif event.key == pygame.K_4:
                        self.current_tile = 'E'
                    elif event.key == pygame.K_5:
                        self.current_tile = 'X'
                    
                    # Camera movement
                    elif event.key == pygame.K_LEFT:
                        self.camera_x = max(0, self.camera_x - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.camera_x = min(self.map_width - visible_width, self.camera_x + 1)
                    elif event.key == pygame.K_UP:
                        self.camera_y = max(0, self.camera_y - 1)
                    elif event.key == pygame.K_DOWN:
                        self.camera_y = min(self.map_height - visible_height, self.camera_y + 1)
                    
                    # Save/Load
                    elif event.key == pygame.K_s:
                        self.save_map()
                    elif event.key == pygame.K_l:
                        self.load_map()
                    
                    # Print map for copy/paste
                    elif event.key == pygame.K_p:
                        print("Map data for copy/paste:")
                        print("LEVEL_MAP = [")
                        for row in self.map_data:
                            print(f'    "{row}",')
                        print("]")
            
            # Handle mouse input for placing tiles
            if pygame.mouse.get_pressed()[0]:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                tile_x = mouse_pos[0] // self.tile_size + self.camera_x
                tile_y = mouse_pos[1] // self.tile_size + self.camera_y
                
                if 0 <= tile_x < self.map_width and 0 <= tile_y < self.map_height:
                    # Special handling for spawn points (only one allowed)
                    if self.current_tile == 'S':
                        # Remove any existing spawn points
                        for y in range(self.map_height):
                            row = self.map_data[y]
                            if 'S' in row:
                                # Replace S with empty space
                                index = row.index('S')
                                self.map_data[y] = row[:index] + '.' + row[index+1:]
                    
                    # Update the map
                    row = self.map_data[tile_y]
                    self.map_data[tile_y] = row[:tile_x] + self.current_tile + row[tile_x+1:]
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    # Example starting map - use empty map or load from file
    editor = MapEditor()
    editor.run()
