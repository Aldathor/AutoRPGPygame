"""
ASCII Sprites for characters and enemies
"""
import pygame

class ASCIISprite:
    """
    Class to handle ASCII character-based sprites
    """
    def __init__(self, ascii_art, fg_color=(255, 255, 255), bg_color=(0, 0, 0, 0)):
        """
        Initialize an ASCII sprite
        
        Args:
            ascii_art (list): List of strings representing ASCII art
            fg_color (tuple): Foreground color (RGB)
            bg_color (tuple): Background color (RGBA with alpha)
        """
        self.ascii_art = ascii_art
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.font = pygame.font.SysFont("Courier New", 14)  # Monospace font
        
        # Calculate dimensions
        self.width = max(len(line) for line in ascii_art) * 8  # Approximate width based on font
        self.height = len(ascii_art) * 16  # Approximate height based on font
        
        # Create the surface
        self.surface = self._create_surface()
    
    def _create_surface(self):
        """
        Create a pygame surface with the ASCII art
        
        Returns:
            pygame.Surface: The created surface
        """
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surface.fill(self.bg_color)
        
        for i, line in enumerate(self.ascii_art):
            text_surface = self.font.render(line, True, self.fg_color)
            surface.blit(text_surface, (0, i * 16))  # 16 is the approximate line height
        
        return surface
    
    def render(self, screen, position):
        """
        Render the ASCII sprite
        
        Args:
            screen (pygame.Surface): The screen to render to
            position (tuple): The position (x, y) to render at
        """
        screen.blit(self.surface, position)

# Character class sprites
WARRIOR_SPRITE = [
    "   O   ",
    "  /|\\  ",
    " _/ \\_ ",
    "   |   ",
    "  / \\  "
]

ARCHER_SPRITE = [
    "   O   ",
    "  /|---->",
    " _/ \\_  ",
    "   |   ",
    "  / \\  "
]

MAGE_SPRITE = [
    "   O   ",
    "  /|\\* ",
    " _/ \\_ ",
    "   |   ",
    "  / \\  "
]

# Enemy sprites
GOBLIN_SPRITE = [
    "  ^-^  ",
    "  |0|  ",
    "  / \\  "
]

ORC_SPRITE = [
    "  #-#  ",
    "  |O|  ",
    " // \\\\ "
]

TROLL_SPRITE = [
    "  @-@  ",
    "  |O|  ",
    " // \\\\ "
]

SKELETON_SPRITE = [
    "  X_X  ",
    "  |o|  ",
    "  / \\  "
]

DRAGON_SPRITE = [
    "   ^v^   ",
    "  <|O|>  ",
    "   /|\\   ",
    "  // \\\\ "
]

# Function to get sprite for a character class
def get_class_sprite(class_name, fg_color=(255, 255, 255)):
    if class_name.lower() == "warrior":
        return ASCIISprite(WARRIOR_SPRITE, fg_color)
    elif class_name.lower() == "archer":
        return ASCIISprite(ARCHER_SPRITE, fg_color)
    elif class_name.lower() == "mage":
        return ASCIISprite(MAGE_SPRITE, fg_color)
    return None

# Function to get sprite for an enemy type
def get_enemy_sprite(enemy_type, fg_color=(255, 255, 255)):
    if enemy_type.lower() == "goblin":
        return ASCIISprite(GOBLIN_SPRITE, fg_color)
    elif enemy_type.lower() == "orc":
        return ASCIISprite(ORC_SPRITE, fg_color)
    elif enemy_type.lower() == "troll":
        return ASCIISprite(TROLL_SPRITE, fg_color)
    elif enemy_type.lower() == "skeleton":
        return ASCIISprite(SKELETON_SPRITE, fg_color)
    elif enemy_type.lower() == "dragon":
        return ASCIISprite(DRAGON_SPRITE, fg_color)
    return None
