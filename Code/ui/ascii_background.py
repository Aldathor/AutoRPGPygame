"""
ASCII forest background with animated elements
"""
import pygame
import random

class ASCIIBackground:
    """
    Animated ASCII background for the game
    """
    def __init__(self, screen_width, screen_height):
        """
        Initialize the ASCII background
        
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont("Courier New", 14)
        
        # Forest characters
        self.tree_chars = ["Y", "T", "^"]
        self.ground_chars = ["_", ".", ",", "`"]
        self.path_chars = [" ", ".", ","]
        
        # Generate forest
        self.forest = []
        path_center = screen_width // 2
        path_width = 200
        
        for y in range(0, screen_height, 14):
            row = []
            for x in range(0, screen_width, 14):
                # Determine if this position is on the path
                distance_from_path = abs(x - path_center)
                if distance_from_path < path_width // 2:
                    # On path
                    char = random.choice(self.path_chars)
                    color = (139, 69, 19)  # Brown
                    if char in [".", ","]:
                        color = (160, 82, 45)  # Sienna
                else:
                    # In forest
                    if random.random() < 0.1:
                        char = random.choice(self.tree_chars)
                        color = (0, 100, 0)  # Dark green
                    else:
                        char = random.choice(self.ground_chars)
                        color = (0, 128, 0)  # Green
                
                row.append({
                    "char": char,
                    "color": color,
                    "animation": random.random() < 0.05,  # 5% chance to animate
                    "animation_timer": random.random() * 2.0,
                    "animation_period": random.uniform(1.0, 3.0)
                })
            self.forest.append(row)
        
        # Path overlay for combat
        self.path = []
        for y in range(screen_height // 2 - 50, screen_height // 2 + 50, 14):
            row = []
            for x in range(path_center - path_width // 2, path_center + path_width // 2, 14):
                row.append({
                    "x": x,
                    "y": y,
                    "char": random.choice(self.path_chars),
                    "color": (139, 69, 19)  # Brown
                })
            self.path.append(row)
    
    def update(self, delta_time):
        """
        Update the background animation
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update animated elements
        for row in self.forest:
            for cell in row:
                if cell["animation"]:
                    cell["animation_timer"] += delta_time
                    if cell["animation_timer"] >= cell["animation_period"]:
                        cell["animation_timer"] = 0
                        # Change character for animation effect
                        if cell["char"] in self.tree_chars:
                            cell["char"] = random.choice(self.tree_chars)
                        elif cell["char"] in self.ground_chars:
                            cell["char"] = random.choice(self.ground_chars)
                        elif cell["char"] in self.path_chars:
                            cell["char"] = random.choice(self.path_chars)
    
    def render(self, screen):
        """
        Render the ASCII background
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        # Clear screen first
        screen.fill((0, 0, 0))
        
        # Render forest background with reduced alpha
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        
        for y, row in enumerate(self.forest):
            for x, cell in enumerate(row):
                text = self.font.render(cell["char"], True, cell["color"])
                # Add some alpha to the text to make it subtle
                text.set_alpha(128)
                screen.blit(text, (x * 14, y * 14))
        
        # Overlay to darken background
        screen.blit(overlay, (0, 0))
        
        # Render path (more visible)
        for row in self.path:
            for cell in row:
                text = self.font.render(cell["char"], True, cell["color"])
                screen.blit(text, (cell["x"], cell["y"]))
