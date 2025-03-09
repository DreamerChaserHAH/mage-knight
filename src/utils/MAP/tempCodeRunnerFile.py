"""
Temporary code runner file for testing map editor functionality.
"""

import sys
import os

# Add parent directory to path so we can import from there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the map editor
from src.utils.MAP.map_editor import MapEditor

# Example map data
example_map = [
    "................",
    "................",
    ".....#####......",
    "................",
    "...S............",
    "...#####........",
    "................",
    "...........E....",
    "......##########",
    "XXXXXXXXXXXXXXXX",
]

# Run the map editor with the example map
if __name__ == "__main__":
    editor = MapEditor(example_map)
    editor.run()