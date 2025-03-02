"""
Combat Log - Handles displaying and managing combat events
"""
import pygame
from game.config import (
    COMBAT_LOG_LINES, COMBAT_LOG_WIDTH, COMBAT_LOG_HEIGHT, 
    COMBAT_LOG_BG_COLOR, COMBAT_LOG_TEXT_COLOR, UI_PADDING
)

class CombatLog:
    """
    Manages and displays combat events
    """
    def __init__(self, max_entries=100):
        """
        Initialize the combat log
        
        Args:
            max_entries (int): Maximum number of log entries to store
        """
        self.entries = []
        self.max_entries = max_entries
    
    def add_entry(self, message):
        """
        Add a message to the combat log
        
        Args:
            message (str): The message to log
        """
        self.entries.append(message)
        
        # Keep log at a reasonable size
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        
        # Print to console for debugging
        print(f"[COMBAT] {message}")
    
    def get_recent_entries(self, count=10):
        """
        Get the most recent log messages
        
        Args:
            count (int): Number of messages to return
            
        Returns:
            list: Recent combat log messages
        """
        return self.entries[-count:] if self.entries else []
    
    def clear(self):
        """Clear all log entries"""
        self.entries = []
    
    def render(self, screen, font, x, y):
        """
        Render the combat log
        
        Args:
            screen (pygame.Surface): The screen to render to
            font (pygame.font.Font): Font to use for text
            x (int): X position (top-left)
            y (int): Y position (top-left)
        """
        # Create a surface with alpha for the background
        log_surface = pygame.Surface((COMBAT_LOG_WIDTH, COMBAT_LOG_HEIGHT), pygame.SRCALPHA)
        log_surface.fill(COMBAT_LOG_BG_COLOR)
        screen.blit(log_surface, (x, y))
        
        # Draw log entries
        log_entries = self.get_recent_entries(COMBAT_LOG_LINES)
        line_height = font.get_height()
        
        for i, entry in enumerate(log_entries):
            # Word wrap long entries
            words = entry.split()
            line = ""
            x_text = x + 10
            y_text = y + 10 + (i * line_height)
            
            for word in words:
                test_line = line + word + " "
                test_width = font.size(test_line)[0]
                
                if test_width > COMBAT_LOG_WIDTH - 20:
                    text = font.render(line, True, COMBAT_LOG_TEXT_COLOR)
                    screen.blit(text, (x_text, y_text))
                    y_text += line_height
                    line = word + " "
                else:
                    line = test_line
            
            # Render last line
            if line:
                text = font.render(line, True, COMBAT_LOG_TEXT_COLOR)
                screen.blit(text, (x_text, y_text))
    
    def log_attack(self, attacker, target, result):
        """
        Log an attack to the combat log
        
        Args:
            attacker (BaseCharacter): The attacking character
            target (BaseCharacter): The target character
            result (dict): Attack result
        """
        if not result.get("hit", False):
            self.add_entry(f"{attacker.name} missed {target.name}!")
            return
        
        # Format attack message based on character type and result
        message = f"{attacker.name} "
        
        # Check for special attack types
        if "spell" in result and result["spell"]:
            message += f"cast {result['spell']} on "
        elif "breath_weapon" in result and result["breath_weapon"]:
            message += f"breathed fire on "
        elif "multi_hit" in result and result["multi_hit"]:
            message += f"fired {result['hits']} arrows at "
        elif "double_attack" in result and result["double_attack"]:
            message += f"quickly struck twice at "
        else:
            message += "attacked "
        
        message += f"{target.name} for {result['damage']} damage"
        
        # Add effects
        if "critical" in result and result["critical"]:
            message += " (Critical Hit!)"
        if "dodged" in result and result["dodged"]:
            message = f"{target.name} dodged {attacker.name}'s attack!"
        if "stun" in result and result["stun"]:
            message += " (Stunned)"
        if "effect" in result and result["effect"] == "slow":
            message += " (Slowed)"
        
        self.add_entry(message)
    
    def log_defeat(self, character):
        """
        Log a character defeat
        
        Args:
            character (BaseCharacter): The defeated character
        """
        self.add_entry(f"{character.name} has been defeated!")
    
    def log_level_up(self, character):
        """
        Log a character level up
        
        Args:
            character (BaseCharacter): The character that leveled up
        """
        self.add_entry(f"{character.name} leveled up to level {character.level}!")
    
    def log_enemy_defeated(self, enemy, xp_gained):
        """
        Log an enemy defeat with XP gain
        
        Args:
            enemy (Enemy): The defeated enemy
            xp_gained (int): XP gained from the defeat
        """
        self.add_entry(f"{enemy.name} has been defeated! +{xp_gained} XP")
