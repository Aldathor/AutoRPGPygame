"""
Fire pit animation for rest periods
"""
import pygame
import random

class FirePitAnimation:
    """
    Fire pit ASCII animation
    """
    def __init__(self, screen_width, screen_height):
        """
        Initialize the fire pit animation
        
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont("Courier New", 16)
        
        # Fire pit ASCII frames
        self.fire_frames = [
            [
                "    {()))))}    ",
                "   {(()))))}))   ",
                "  {(((()))))))  ",
                "  {((((()))))))  ",
                " {((((()))))))} ",
                "{(((((()))))))}",
                " ~~~~~~~~~~~~~~ ",
                "                "
            ],
            [
                "    {()))))}    ",
                "   {(()))))}))   ",
                "  {(((()))))))}  ",
                "  {((((()))))))}  ",
                " {((((()))))))))} ",
                "{((((((()))))))))}",
                " ~~~~~~~~~~~~~~ ",
                "                "
            ],
            [
                "    {()))))}    ",
                "   {(()))))))}   ",
                "  {(((()))))))}  ",
                "  {((((())))))))  ",
                " {(((((()))))))) ",
                "{((((((()))))))))}",
                " ~~~~~~~~~~~~~~ ",
                "                "
            ]
        ]
        
        # Fire colors
        self.fire_colors = [
            (255, 100, 0),    # Orange
            (255, 50, 0),     # Reddish orange
            (255, 150, 0),    # Lighter orange
            (200, 0, 0)       # Red
        ]
        
        # Sparks
        self.sparks = []
        for _ in range(20):
            self.sparks.append({
                "x": random.randint(0, self.screen_width),
                "y": random.randint(0, self.screen_height),
                "speed": random.uniform(0.5, 2.0),
                "color": random.choice(self.fire_colors),
                "char": random.choice(["'", ".", "*", "`"])
            })
        
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_duration = 0.3  # seconds between frames
    
    def update(self, delta_time):
        """
        Update the fire pit animation
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update frame
        self.frame_timer += delta_time
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.fire_frames)
        
        # Update sparks
        for spark in self.sparks:
            spark["y"] -= spark["speed"]
            if spark["y"] < 0:
                spark["y"] = self.screen_height
                spark["x"] = random.randint(0, self.screen_width)
    
    def render(self, screen):
        """
        Render the fire pit animation
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        # Draw dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Draw fire pit
        frame = self.fire_frames[self.current_frame]
        frame_width = len(frame[0]) * 10  # Approximate width
        frame_height = len(frame) * 20  # Approximate height
        
        # Center position
        x = (self.screen_width - frame_width) // 2
        y = (self.screen_height - frame_height) // 2
        
        for i, line in enumerate(frame):
            for j, char in enumerate(line):
                color = self.fire_colors[0]  # Default color
                if char in "{(}))":  # Fire characters
                    color = random.choice(self.fire_colors)
                elif char == "~":  # Log characters
                    color = (139, 69, 19)  # Brown
                
                text = self.font.render(char, True, color)
                screen.blit(text, (x + j * 10, y + i * 20))
        
        # Draw sparks
        for spark in self.sparks:
            text = self.font.render(spark["char"], True, spark["color"])
            screen.blit(text, (spark["x"], spark["y"]))
        
        # Draw campfire area - circle around the fire
        pygame.draw.circle(screen, (30, 30, 30), 
                         (self.screen_width // 2, self.screen_height // 2),
                         frame_height + 20, 3)
