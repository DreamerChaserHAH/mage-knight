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
                "." * 100,  # Make default map wider
                "." * 100,
                "." * 100,
                "." * 100,
                "." * 100,
                "." * 100,
                "." * 100,
                "." * 100,
                "." * 100,
                "." * 100,
                "." * 100,
                "." * 100,
                "." * 100,
                "." * 100,
                "." * 100,
            ]
        else:
            self.map_data = map_data.copy()  # Make a copy to avoid modifying original
            
        # Calculate dimensions
        self.map_width = len(self.map_data[0])
        self.map_height = len(self.map_data)
        
        # ======================= IMPROVED SCREEN SETUP =======================
        # Set up display with reasonable window size
        self.screen_width = min(self.map_width * self.tile_size, 800)
        self.screen_height = min(self.map_height * self.tile_size, 600)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Mage Knight Map Editor")
        
        # Calculate visible dimensions
        self.visible_width = self.screen_width // self.tile_size
        self.visible_height = self.screen_height // self.tile_size
        # ===============================================================================
        
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
        
        # ======================= IMPROVED SCROLLING =======================
        # Scrolling speed and controls
        self.scroll_speed = 5  # Tiles per second
        self.scroll_timer = 0
        self.scroll_interval = 10  # Frames between scroll updates
        self.scrolling = {"left": False, "right": False, "up": False, "down": False}
        # ===============================================================================
        
        # Font for info display
        self.font = pygame.font.SysFont(None, 24)
        
        # ======================= MAP EXPANSION FEATURE =======================
        # Features for expanding the map
        self.can_expand_map = True  # Allow map expansion
        # ===============================================================================
    
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
            
            # Recalculate visible dimensions
            self.visible_width = self.screen_width // self.tile_size
            self.visible_height = self.screen_height // self.tile_size
            
            print(f"Map loaded from {filename}")
        except Exception as e:
            print(f"Error loading map: {e}")
    
    # ======================= EXPANDING MAP FUNCTIONS =======================
    def expand_map(self, direction):
        """
        Expand the map in the given direction
        
        Args:
            direction (str): 'left', 'right', 'up', or 'down'
        """
        if not self.can_expand_map:
            return
            
        if direction == 'right':
            # Add 10 columns to the right
            for i in range(len(self.map_data)):
                self.map_data[i] = self.map_data[i] + '.' * 10
        elif direction == 'left':
            # Add 10 columns to the left
            for i in range(len(self.map_data)):
                self.map_data[i] = '.' * 10 + self.map_data[i]
            # Adjust camera position
            self.camera_x += 10
        elif direction == 'down':
            # Add 5 rows to the bottom
            for _ in range(5):
                self.map_data.append('.' * len(self.map_data[0]))
        elif direction == 'up':
            # Add 5 rows to the top
            for _ in range(5):
                self.map_data.insert(0, '.' * len(self.map_data[0]))
            # Adjust camera position
            self.camera_y += 5
            
        # Update map dimensions
        self.map_width = len(self.map_data[0])
        self.map_height = len(self.map_data)
        print(f"Map expanded {direction}. New size: {self.map_width}x{self.map_height}")
    # ===============================================================================
    
    def draw(self):
        """Draw the map and UI"""
        self.screen.fill((30, 30, 30))  # Dark gray background
        
        # Draw the visible portion of the map
        for y in range(self.visible_height):
            map_y = y + self.camera_y
            if map_y >= self.map_height:
                continue
                
            for x in range(self.visible_width):
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
        
        # ======================= IMPROVED UI INFORMATION =======================
        # Draw UI information with more details
        current_pos = f"Camera: ({self.camera_x}, {self.camera_y}) | "
        map_size = f"Map: {self.map_width}x{self.map_height} | "
        controls = "Controls: Arrow=Scroll | WASD=Fast Scroll | 1-5=Tile | +/-=Expand Map"
        
        info_surface = self.font.render(current_pos + map_size + self.current_tile, True, (255, 255, 255))
        controls_surface = self.font.render(controls, True, (200, 200, 200))
        
        self.screen.blit(info_surface, (10, self.screen_height - 48))
        self.screen.blit(controls_surface, (10, self.screen_height - 24))
        # ===============================================================================
    
    # ======================= IMPROVED MAP SCROLLING =======================
    def update_scroll(self):
        """Update map scrolling based on current scroll state"""
        # Check if we need to scroll the map
        scroll_x, scroll_y = 0, 0
        
        # Handle ongoing scrolling
        if self.scrolling["left"]:
            scroll_x = -1
        elif self.scrolling["right"]:
            scroll_x = 1
            
        if self.scrolling["up"]:
            scroll_y = -1
        elif self.scrolling["down"]:
            scroll_y = 1
            
        # Apply scrolling with boundaries
        new_camera_x = max(0, min(self.map_width - self.visible_width, self.camera_x + scroll_x))
        new_camera_y = max(0, min(self.map_height - self.visible_height, self.camera_y + scroll_y))
        
        # Update camera position if it changed
        if new_camera_x != self.camera_x or new_camera_y != self.camera_y:
            self.camera_x = new_camera_x
            self.camera_y = new_camera_y
            return True  # Map view changed
            
        return False  # No change
    # ===============================================================================
    
    def run(self):
        """Main loop for the map editor"""
        running = True
        clock = pygame.time.Clock()
        
        # Show instructions at start
        print("Map Editor Instructions:")
        print("- Arrow keys: Scroll the map slowly")
        print("- WASD keys: Scroll the map quickly")
        print("- 1-5: Select different tile types")
        print("- Click: Place selected tile")
        print("- +/-: Expand map in different directions (Shift+=Right, -=Left, Ctrl+=Down, Ctrl+-=Up)")
        print("- P: Print map data for copy/paste")
        print("- S: Save map")
        print("- L: Load map")
        
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
                    
                    # ======================= IMPROVED KEY HANDLING =======================
                    # Arrow key scrolling - one tile at a time
                    elif event.key == pygame.K_LEFT:
                        self.scrolling["left"] = True
                        self.scrolling["right"] = False
                    elif event.key == pygame.K_RIGHT:
                        self.scrolling["right"] = True
                        self.scrolling["left"] = False
                    elif event.key == pygame.K_UP:
                        self.scrolling["up"] = True
                        self.scrolling["down"] = False
                    elif event.key == pygame.K_DOWN:
                        self.scrolling["down"] = True
                        self.scrolling["up"] = False
                        
                    # WASD key scrolling - faster scrolling (5 tiles at a time)
                    elif event.key == pygame.K_a:
                        self.camera_x = max(0, self.camera_x - 5)
                    elif event.key == pygame.K_d:
                        self.camera_x = min(self.map_width - self.visible_width, self.camera_x + 5)
                    elif event.key == pygame.K_w:
                        self.camera_y = max(0, self.camera_y - 5)
                    elif event.key == pygame.K_s:
                        self.camera_y = min(self.map_height - self.visible_height, self.camera_y + 5)
                    # ===============================================================================
                    
                    # ======================= MAP EXPANSION KEYS =======================
                    # Map expansion with +/- keys and modifiers
                    elif event.key == pygame.K_EQUALS:  # + key
                        mods = pygame.key.get_mods()
                        if mods & pygame.KMOD_SHIFT:
                            self.expand_map('right')
                        elif mods & pygame.KMOD_CTRL:
                            self.expand_map('up')
                        else:
                            self.expand_map('right')  # Default is expand right
                            
                    elif event.key == pygame.K_MINUS:  # - key
                        mods = pygame.key.get_mods()
                        if mods & pygame.KMOD_CTRL:
                            self.expand_map('down')
                        else:
                            self.expand_map('left')  # Default is expand left
                    # ===============================================================================
                    
                    # Save/Load
                    elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.save_map()
                    elif event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.load_map()
                    
                    # Print map for copy/paste
                    elif event.key == pygame.K_p and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        print("Map data for copy/paste:")
                        print("LEVEL_MAP = [")
                        for row in self.map_data:
                            print(f'    "{row}",')
                        print("]")
                        
                elif event.type == pygame.KEYUP:
                    # Stop scrolling when keys are released
                    if event.key == pygame.K_LEFT:
                        self.scrolling["left"] = False
                    elif event.key == pygame.K_RIGHT:
                        self.scrolling["right"] = False
                    elif event.key == pygame.K_UP:
                        self.scrolling["up"] = False
                    elif event.key == pygame.K_DOWN:
                        self.scrolling["down"] = False
            
            # ======================= IMPROVED MOUSE HANDLING =======================
            # Handle mouse input for placing tiles
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:  # Left mouse button
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
            # ===============================================================================
                    
            # Update continuous scrolling
            self.update_scroll()
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    # Example starting map - uncomment to test with a specific map
    # from main import LEVEL_MAP
    # editor = MapEditor(LEVEL_MAP)
    editor = MapEditor()
    editor.run()
