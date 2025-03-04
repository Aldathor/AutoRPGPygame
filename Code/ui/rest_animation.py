"""
Placeholder for rest animation (to be replaced with sprite animation)
"""
import pygame
import random

class FirePitAnimation:
    """
    Placeholder for fire pit animation
    """
    def __init__(self, screen_width, screen_height):
        """
        Initialize a simple rest animation
        
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Fire particles
        self.particles = []
        for _ in range(50):
            self.particles.append({
                "x": screen_width // 2 + random.randint(-30, 30),
                "y": screen_height // 2 + random.randint(-10, 10),
                "size": random.randint(2, 8),
                "color": (random.randint(200, 255), random.randint(50, 150), 0),
                "speed": random.uniform(20, 60)
            })
    
    def update(self, delta_time):
        """
        Update the fire animation
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update fire particles
        for particle in self.particles:
            particle["y"] -= particle["speed"] * delta_time
            particle["size"] -= random.uniform(5, 15) * delta_time
            
            if particle["size"] <= 0:
                # Reset particle
                particle["x"] = self.screen_width // 2 + random.randint(-30, 30)
                particle["y"] = self.screen_height // 2 + random.randint(-10, 10)
                particle["size"] = random.randint(2, 8)
                particle["color"] = (random.randint(200, 255), random.randint(50, 150), 0)
    
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
        
        # Draw a "log" for the fire
        log_rect = pygame.Rect(
            self.screen_width // 2 - 50,
            self.screen_height // 2 + 20,
            100,
            20
        )
        pygame.draw.rect(screen, (139, 69, 19), log_rect)  # Brown log
        
        # Draw fire particles
        for particle in self.particles:
            if particle["size"] > 0:
                pygame.draw.circle(
                    screen,
                    particle["color"],
                    (int(particle["x"]), int(particle["y"])),
                    int(particle["size"])
                )
        
        # Draw a circle on the ground
        pygame.draw.circle(
            screen,
            (50, 50, 50),
            (self.screen_width // 2, self.screen_height // 2 + 30),
            70,
            3
        )