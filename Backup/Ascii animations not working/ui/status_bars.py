"""
Status Bars - UI elements for health, XP, and other status indicators
"""
import pygame
from game.config import HEALTH_BAR_HEIGHT, XP_BAR_HEIGHT

class HealthBar:
    """
    Health bar UI component
    """
    def __init__(self, width=100, height=HEALTH_BAR_HEIGHT):
        """
        Initialize the health bar
        
        Args:
            width (int): Width of the bar
            height (int): Height of the bar
        """
        self.width = width
        self.height = height
        self.bg_color = (100, 100, 100)  # Gray background
        self.fg_color = (0, 255, 0)      # Green foreground
        self.border_color = (200, 200, 200)  # Light gray border
        self.text_color = (255, 255, 255)  # White text
    
    def render(self, screen, character, x, y, font, center=True):
        """
        Render the health bar
        
        Args:
            screen (pygame.Surface): The screen to render to
            character (BaseCharacter): Character to display health for
            x (int): X position
            y (int): Y position
            font (pygame.font.Font): Font for health text
            center (bool): If True, x,y is the center of the bar. If False, x,y is the top-left.
        """
        # If centered, adjust x,y to be top-left
        if center:
            x = x - self.width // 2
        
        # Background
        pygame.draw.rect(
            screen, 
            self.bg_color,
            (x, y, self.width, self.height)
        )
        
        # Health bar
        health_percentage = character.current_hp / character.max_hp
        current_width = int(self.width * health_percentage)
        
        pygame.draw.rect(
            screen, 
            self.fg_color,
            (x, y, current_width, self.height)
        )
        
        # Border
        pygame.draw.rect(
            screen, 
            self.border_color,
            (x, y, self.width, self.height),
            1  # Border width
        )
        
        # Health text
        health_text = f"{character.current_hp}/{character.max_hp}"
        text_surface = font.render(health_text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(x + self.width // 2, y + self.height // 2))
        screen.blit(text_surface, text_rect)

class XPBar:
    """
    Experience bar UI component
    """
    def __init__(self, width=100, height=XP_BAR_HEIGHT):
        """
        Initialize the XP bar
        
        Args:
            width (int): Width of the bar
            height (int): Height of the bar
        """
        self.width = width
        self.height = height
        self.bg_color = (50, 50, 100)    # Dark blue background
        self.fg_color = (0, 128, 255)    # Light blue foreground
        self.border_color = (200, 200, 200)  # Light gray border
        self.text_color = (255, 255, 255)  # White text
    
    def render(self, screen, character, x, y, font, center=True):
        """
        Render the XP bar
        
        Args:
            screen (pygame.Surface): The screen to render to
            character (BaseCharacter): Character to display XP for
            x (int): X position
            y (int): Y position
            font (pygame.font.Font): Font for XP text
            center (bool): If True, x,y is the center of the bar. If False, x,y is the top-left.
        """
        # If centered, adjust x,y to be top-left
        if center:
            x = x - self.width // 2
        
        # Background
        pygame.draw.rect(
            screen, 
            self.bg_color,
            (x, y, self.width, self.height)
        )
        
        # XP bar
        xp_percentage = character.xp / character.xp_to_next_level
        current_width = int(self.width * xp_percentage)
        
        pygame.draw.rect(
            screen, 
            self.fg_color,
            (x, y, current_width, self.height)
        )
        
        # Border
        pygame.draw.rect(
            screen, 
            self.border_color,
            (x, y, self.width, self.height),
            1  # Border width
        )
        
        # XP text (rendered below the bar)
        xp_text = f"Lv.{character.level} - {character.xp}/{character.xp_to_next_level} XP"
        text_surface = font.render(xp_text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(x + self.width // 2, y + self.height + 10))
        screen.blit(text_surface, text_rect)

class CooldownIndicator:
    """
    Cooldown indicator UI component
    """
    def __init__(self, radius=20):
        """
        Initialize the cooldown indicator
        
        Args:
            radius (int): Radius of the indicator
        """
        self.radius = radius
        self.bg_color = (50, 50, 50)      # Dark gray background
        self.fg_color = (255, 200, 0)     # Yellow-orange foreground
        self.border_color = (200, 200, 200)  # Light gray border
    
    def render(self, screen, character, x, y):
        """
        Render the cooldown indicator
        
        Args:
            screen (pygame.Surface): The screen to render to
            character (BaseCharacter): Character to display cooldown for
            x (int): X position (center)
            y (int): Y position (center)
        """
        # Background circle
        pygame.draw.circle(
            screen,
            self.bg_color,
            (x, y),
            self.radius
        )
        
        # If character has a cooldown, draw an arc to represent it
        if character.attack_cooldown > 0:
            cooldown_percent = character.attack_cooldown / character.get_attack_cooldown()
            
            # Convert to radians (0 at top, clockwise)
            angle = -90 + (360 * (1 - cooldown_percent))
            
            # Draw an arc representing remaining cooldown
            pygame.draw.arc(
                screen,
                self.fg_color,
                (x - self.radius, y - self.radius, self.radius * 2, self.radius * 2),
                pygame.math.radians(-90),  # Start at top
                pygame.math.radians(angle),  # End based on cooldown
                self.radius  # Width of arc
            )
        
        # Border
        pygame.draw.circle(
            screen,
            self.border_color,
            (x, y),
            self.radius,
            1  # Border width
        )
