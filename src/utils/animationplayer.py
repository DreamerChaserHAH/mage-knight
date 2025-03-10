"""
Animation player for sprite sheet animations with Aseprite JSON support.
This module handles loading and playing animations from sprite sheets,
supporting variable frame counts, sizes, and timing information from JSON files.
"""

import pygame
import json
import os
from .utils import load_image

class Animation:
    """
    Represents a single animation with multiple frames and timing information.
    """
    def __init__(self, name, frames, durations=None, loop=True):
        """
        Initialize an animation

        Args:
            name (str): Name of the animation
            frames (list): List of pygame surfaces representing animation frames
            durations (list, optional): List of frame durations in milliseconds. Defaults to None.
            loop (bool, optional): Whether the animation should loop. Defaults to True.
        """
        self.name = name
        self.frames = frames
        self.frame_count = len(frames)
        
        # If durations not provided, default to 100ms per frame
        self.durations = durations if durations is not None else [100] * self.frame_count
        
        # Ensure durations list matches frame count
        if len(self.durations) != self.frame_count:
            print(f"Warning: Duration count ({len(self.durations)}) doesn't match frame count ({self.frame_count})")
            # Extend or trim durations list as needed
            if len(self.durations) < self.frame_count:
                self.durations.extend([100] * (self.frame_count - len(self.durations)))
            else:
                self.durations = self.durations[:self.frame_count]
                
        self.loop = loop
        self.total_duration = sum(self.durations)
        
    def get_frame_at_time(self, elapsed_time):
        """
        Get the frame to display at a given elapsed time.
        
        Args:
            elapsed_time (float): Elapsed time in milliseconds
            
        Returns:
            tuple: (frame surface, is_animation_complete)
        """
        # Handle completion for non-looping animations
        if not self.loop and elapsed_time >= self.total_duration:
            return self.frames[-1], True
        
        # For looping animations, wrap around the elapsed time
        if self.loop:
            elapsed_time = elapsed_time % self.total_duration
        
        # Find the correct frame based on the elapsed time
        current_time = 0
        for i, duration in enumerate(self.durations):
            current_time += duration
            if elapsed_time < current_time:
                return self.frames[i], False
        
        # Failsafe - return the last frame
        return self.frames[-1], False


class AnimationPlayer:
    """
    Manages and plays animations from sprite sheets and JSON metadata.
    """
    def __init__(self):
        """Initialize the animation player."""
        self.animations = {}  # Dictionary of loaded animations by name
        self.current_animation = None
        self.current_animation_name = None
        self.start_time = 0
        self.is_playing = False
        self.flip_x = False
        self.flip_y = False
        self.scaled_frames = {}  # Cache for scaled frames
        self.scale_factor = (1.0, 1.0)  # (width_factor, height_factor)
    
    def load_aseprite_animation(self, image_path, json_path=None, animation_name=None):
        """
        Load animation from an Aseprite sprite sheet and JSON metadata.
        
        Args:
            image_path (str): Path to the sprite sheet image
            json_path (str, optional): Path to the JSON metadata file.
                If None, tries to use the same path as image with .json extension.
            animation_name (str, optional): Name to give this animation.
                Defaults to the filename without extension.
                
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        # ======================= IMPROVED IMAGE LOADING WITH DETAILED DEBUGGING =======================
        # Load the sprite sheet image with better debug info
        sprite_sheet = load_image(image_path)
        if sprite_sheet is None:
            print(f"Error: Failed to load sprite sheet: {image_path}")
            return False
        
        # Print the image dimensions for debugging
        img_width, img_height = sprite_sheet.get_size()
        print(f"Loaded sprite sheet: {image_path} - Size: {img_width}x{img_height}")
        # If json_path is not provided, try to infer it from image_path
        if json_path is None:
            base_path = os.path.splitext(image_path)[0]
            json_path = base_path + ".json"
        
        # If animation_name is not provided, use the filename without extension
        if animation_name is None:
            animation_name = os.path.basename(os.path.splitext(image_path)[0])
        
        # Try to load and parse the JSON metadata
        frames = []
        frame_durations = []
        
        try:
            # Get the absolute path of the JSON file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_path_abs = os.path.join(base_dir, '../assets', json_path)
            
            if not os.path.exists(json_path_abs):
                # Try relative path as well
                json_path_abs = json_path
                
            with open(json_path_abs, 'r') as f:
                json_data = json.load(f)
                
            # Check if this is an Aseprite JSON file
            if "frames" not in json_data or "meta" not in json_data:
                raise ValueError("Not a valid Aseprite JSON file format")
                
            # Get frame data
            frame_data = json_data["frames"]
            meta_data = json_data["meta"]
            
            # Sort the frames by their number if they have numeric suffixes
            sorted_frames = sorted(frame_data.items(), key=lambda x: self._extract_frame_number(x[0]))
            
            # Extract frames and durations with better error reporting
            for name, data in sorted_frames:
                try:
                    # Extract frame rectangle
                    frame_rect = pygame.Rect(
                        data["frame"]["x"],
                        data["frame"]["y"],
                        data["frame"]["w"],
                        data["frame"]["h"]
                    )
                    
                    # Debug the frame rect
                    print(f"Frame {name}: rect={frame_rect}, sprite_sheet={sprite_sheet.get_size()}")
                    
                    # Validate rectangle is within image bounds before extracting
                    if (frame_rect.right <= sprite_sheet.get_width() and 
                        frame_rect.bottom <= sprite_sheet.get_height()):
                        # Extract the frame from the sprite sheet
                        frame_surface = sprite_sheet.subsurface(frame_rect)
                        frames.append(frame_surface)
                        
                        # Get frame duration
                        duration = data.get("duration", 100)  # Default to 100ms if not specified
                        frame_durations.append(duration)
                    else:
                        print(f"Warning: Frame rect {frame_rect} is outside the sprite sheet bounds {sprite_sheet.get_size()}")
                except Exception as e:
                    print(f"Error extracting frame '{name}': {e}")
            
            print(f"Loaded animation '{animation_name}' with {len(frames)} frames")
            
            # Create the animation object
            self.animations[animation_name] = Animation(
                name=animation_name,
                frames=frames,
                durations=frame_durations,
                loop=True  # Default to looping, can be changed later
            )
            
            return True
            
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"Error loading JSON metadata: {e}")
            
            # Fallback to creating a simple animation from the sprite sheet
            # Try to determine if it's a horizontal or vertical sprite sheet
            width, height = sprite_sheet.get_size()
            frame_size = min(width, height)
            
            if width > height:
                # Horizontal sprite sheet
                num_frames = width // height
                frame_height = height
                frame_width = height
                
                for i in range(num_frames):
                    frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                    try:
                        frame = sprite_sheet.subsurface(frame_rect)
                        frames.append(frame)
                    except ValueError:
                        break
            else:
                # Vertical sprite sheet or single frame
                num_frames = height // width
                frame_width = width
                frame_height = width
                
                for i in range(num_frames):
                    frame_rect = pygame.Rect(0, i * frame_height, frame_width, frame_height)
                    try:
                        frame = sprite_sheet.subsurface(frame_rect)
                        frames.append(frame)
                    except ValueError:
                        break
            
            if len(frames) == 0:
                # If we couldn't extract any frames, just use the whole image as a single frame
                frames = [sprite_sheet]
            
            print(f"Created fallback animation '{animation_name}' with {len(frames)} frames")
            
            # Create a simple animation with default timing
            self.animations[animation_name] = Animation(
                name=animation_name,
                frames=frames,
                loop=True
            )
            
            return True
    
    def _extract_frame_number(self, frame_name):
        """
        Extract the frame number from a frame name like "walk 0.ase" or "frame_001"
        Used for sorting frames in the correct order.
        
        Args:
            frame_name (str): The frame name from the JSON file
            
        Returns:
            int: The extracted frame number, or 0 if none found
        """
        import re
        # Try to extract a number from the frame name
        match = re.search(r'(\d+)', frame_name)
        if match:
            return int(match.group(1))
        return 0
    
    def add_animation(self, name, frames, durations=None, loop=True):
        """
        Add a custom animation manually.
        
        Args:
            name (str): Name of the animation
            frames (list): List of pygame surfaces representing animation frames
            durations (list, optional): List of frame durations in milliseconds. Defaults to None.
            loop (bool, optional): Whether the animation should loop. Defaults to True.
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        if not frames:
            print(f"Error: No frames provided for animation '{name}'")
            return False
            
        self.animations[name] = Animation(name, frames, durations, loop)
        return True
    
    def play(self, animation_name, force_restart=False):
        """
        Start playing an animation.
        
        Args:
            animation_name (str): Name of the animation to play
            force_restart (bool, optional): Whether to restart the animation if it's already playing. 
            Defaults to False.
                
        Returns:
            bool: True if the animation started playing, False otherwise
        """
        if animation_name not in self.animations:
            print(f"Error: Animation '{animation_name}' not found")
            return False
            
        # Don't restart if already playing this animation
        if not force_restart and animation_name == self.current_animation_name and self.is_playing:
            return True
            
        self.current_animation = self.animations[animation_name]
        self.current_animation_name = animation_name
        self.start_time = pygame.time.get_ticks()
        self.is_playing = True
        return True
    
    def stop(self):
        """Stop the current animation."""
        self.is_playing = False
    
    def set_flip(self, flip_x=None, flip_y=None):
        """
        Set whether to flip the animation horizontally or vertically.
        
        Args:
            flip_x (bool, optional): Whether to flip horizontally. Defaults to None (no change).
            flip_y (bool, optional): Whether to flip vertically. Defaults to None (no change).
        """
        if flip_x is not None:
            self.flip_x = flip_x
        if flip_y is not None:
            self.flip_y = flip_y
            
        # Clear scaled frames cache when flipping changes
        self.scaled_frames = {}
    
    def set_scale(self, width_factor, height_factor=None):
        """
        Set scaling factors for the animation.
        
        Args:
            width_factor (float): Scale factor for width
            height_factor (float, optional): Scale factor for height. Defaults to same as width_factor.
        """
        height_factor = height_factor if height_factor is not None else width_factor
        
        # Only update and clear cache if scale actually changed
        if self.scale_factor != (width_factor, height_factor):
            self.scale_factor = (width_factor, height_factor)
            # Clear cache when scale changes
            self.scaled_frames = {}
    
    def update(self):
        """
        Update the animation state. Should be called once per frame.
        
        Returns:
            bool: True if the animation is playing, False otherwise
        """
        return self.is_playing
    
    def draw(self, surface, position, frame_time=None):
        """
        Draw the current frame of the animation at the specified position.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            position (tuple): (x, y) position to draw at
            frame_time (int, optional): Override the internal time tracking with a specific time. 
            Defaults to None.
                
        Returns:
            bool: True if successfully drawn, False otherwise
        """
        if not self.is_playing or not self.current_animation:
            return False
        
        # Calculate elapsed time
        current_time = pygame.time.get_ticks()
        elapsed = frame_time if frame_time is not None else (current_time - self.start_time)
        
        # Get the current frame
        frame, is_complete = self.current_animation.get_frame_at_time(elapsed)
        
        # Stop non-looping animations when complete
        if is_complete and not self.current_animation.loop:
            self.is_playing = False
        
        # ======================= FIXED FLIPPING AND SCALING =======================
        # Apply scaling and flipping - create a unique key for caching
        cache_key = (id(frame), self.scale_factor[0], self.scale_factor[1], self.flip_x, self.flip_y)
        
        # Check if we've already processed this frame
        if cache_key not in self.scaled_frames:
            # Process the frame
            processed_frame = frame
            
            # Apply scaling if needed
            if self.scale_factor != (1.0, 1.0):
                width = int(frame.get_width() * self.scale_factor[0])
                height = int(frame.get_height() * self.scale_factor[1])
                processed_frame = pygame.transform.scale(frame, (width, height))
            
            # Apply flipping if needed - using explicit flags for clarity
            if self.flip_x or self.flip_y:
                processed_frame = pygame.transform.flip(processed_frame, self.flip_x, self.flip_y)
            
            # Cache the processed frame
            self.scaled_frames[cache_key] = processed_frame
        
        # Get the processed frame from cache
        processed_frame = self.scaled_frames[cache_key]
        # ===============================================================================
        
        # Draw the frame
        surface.blit(processed_frame, position)
        return True
    
    def get_size(self):
        """
        Get the size of the current animation frame.
        
        Returns:
            tuple: (width, height) of the current frame, scaled if applicable
        """
        if not self.current_animation or not self.current_animation.frames:
            return (0, 0)
        
        frame = self.current_animation.frames[0]
        width = frame.get_width() * self.scale_factor[0]
        height = frame.get_height() * self.scale_factor[1]
        
        return (width, height)


# Example usage
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    
    player = AnimationPlayer()
    
    # Load a walking animation
    player.load_aseprite_animation(
        image_path="images/Player/player_walking.png",
        json_path="images/Player/player_walking.json",
        animation_name="walk"
    )
    
    # Load an attack animation
    player.load_aseprite_animation(
        image_path="images/Player/player_attack.png",
        json_path="images/Player/player_attack.json", 
        animation_name="attack"
    )
    
    # Default to walking animation
    player.play("walk")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Switch to attack animation
                    player.play("attack")
                elif event.key == pygame.K_w:
                    # Switch to walk animation
                    player.play("walk")
                elif event.key == pygame.K_f:
                    # Toggle horizontal flip
                    player.set_flip(not player.flip_x)
                elif event.key == pygame.K_s:
                    # Change scale
                    player.set_scale(1.5)
        
        screen.fill((0, 0, 0))
        
        # Draw the animation centered on screen
        player_size = player.get_size()
        position = (320 - player_size[0]/2, 240 - player_size[1]/2)
        player.draw(screen, position)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
