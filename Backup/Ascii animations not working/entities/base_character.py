"""
Base character class (abstract)
"""
from abc import ABC, abstractmethod
import math
import pygame
from game.config import (
    BASE_HP, BASE_ATTACK, BASE_DEFENSE, BASE_MAGIC, BASE_SPEED,
    XP_PER_LEVEL, XP_LEVEL_MULTIPLIER, ATTACK_COOLDOWN_BASE
)

class BaseCharacter(ABC):
    """
    Abstract base class for all characters (players and enemies)
    """
    def __init__(self, name, level=1):
        """
        Initialize a character with base stats
        
        Args:
            name (str): Character name
            level (int): Starting level
        """
        self.name = name
        self.level = level
        self.xp = 0
        self.xp_to_next_level = self._calculate_xp_for_level(self.level + 1)
        
        # Base stats (to be modified by derived classes)
        self.base_hp = BASE_HP
        self.base_attack = BASE_ATTACK
        self.base_defense = BASE_DEFENSE
        self.base_magic = BASE_MAGIC
        self.base_speed = BASE_SPEED
        
        # Current stats (calculated from base stats and level)
        self.max_hp = self._calculate_max_hp()
        self.attack = self._calculate_attack()
        self.defense = self._calculate_defense()
        self.magic = self._calculate_magic()
        self.speed = self._calculate_speed()
        
        # Current state
        self.current_hp = self.max_hp
        self.attack_cooldown = 0
        self.alive = True
        
        # Visual representation
        self.sprite = None
        self.position = pygame.Vector2(0, 0)
    
    @abstractmethod
    def attack_target(self, target):
        """
        Attack a target character
        
        Args:
            target (BaseCharacter): The character to attack
            
        Returns:
            dict: Attack result containing damage and effects
        """
        pass
    
    @abstractmethod
    def take_damage(self, damage, damage_type="physical"):
        """
        Take damage from an attack
        
        Args:
            damage (int): Amount of damage
            damage_type (str): Type of damage ("physical" or "magical")
            
        Returns:
            dict: Damage result containing actual damage taken and effects
        """
        pass
    
    def update(self, delta_time):
        """
        Update character state
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0, self.attack_cooldown - delta_time)
    
    def render(self, screen, position=None):
        """
        Render the character
        
        Args:
            screen (pygame.Surface): Screen to render to
            position (tuple, optional): Position override
        """
        if position:
            self.position = pygame.Vector2(position)
        
        # If there's a sprite, render it
        if self.sprite:
            # Check if character is alive
            if self.is_alive():
                # Normal rendering
                screen.blit(self.sprite, self.position)
            else:
                # For defeated characters, render with reduced alpha
                sprite_copy = self.sprite.copy()
                sprite_copy.set_alpha(128)  # Semi-transparent
                screen.blit(sprite_copy, self.position)
                
                # Draw an X over defeated characters
                x1 = self.position[0]
                y1 = self.position[1]
                x2 = x1 + self.sprite.get_width()
                y2 = y1 + self.sprite.get_height()
                
                pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 2)
                pygame.draw.line(screen, (255, 0, 0), (x1, y2), (x2, y1), 2)
    
    def get_animation_type(self):
        """
        Get the appropriate animation type for this character
        
        Returns:
            str: Animation type ("slash", "arrow", "spell")
        """
        # Default implementation, overridden by subclasses
        return "slash"

    def can_attack(self):
        """Check if character can attack (cooldown expired)"""
        return self.attack_cooldown <= 0 and self.alive
    
    def is_alive(self):
        """Check if character is alive"""
        return self.current_hp > 0 and self.alive
    
    def gain_xp(self, amount):
        """
        Gain experience points and level up if needed
        
        Args:
            amount (int): Amount of XP to gain
            
        Returns:
            bool: True if leveled up, False otherwise
        """
        self.xp += amount
        leveled_up = False
        
        # Check for level up
        while self.xp >= self.xp_to_next_level:
            self.level_up()
            leveled_up = True
        
        return leveled_up
    
    def level_up(self):
        """Level up the character and increase stats"""
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = self._calculate_xp_for_level(self.level + 1)
        
        # Recalculate stats
        old_max_hp = self.max_hp
        self.max_hp = self._calculate_max_hp()
        self.attack = self._calculate_attack()
        self.defense = self._calculate_defense()
        self.magic = self._calculate_magic()
        self.speed = self._calculate_speed()
        
        # Heal on level up (only the difference in max HP)
        self.current_hp += (self.max_hp - old_max_hp)
        
        print(f"{self.name} leveled up to level {self.level}!")
    
    def heal(self, amount):
        """
        Heal the character
        
        Args:
            amount (int): Amount to heal
            
        Returns:
            int: Actual amount healed
        """
        if not self.is_alive():
            return 0
        
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
    
    def get_attack_cooldown(self):
        """
        Calculate attack cooldown based on speed
        
        Returns:
            float: Cooldown time in seconds
        """
        # Higher speed means lower cooldown
        cooldown = ATTACK_COOLDOWN_BASE * (1 - (self.speed / 100))
        # Ensure cooldown is at least 0.2 seconds
        return max(0.2, cooldown)
    
    def _calculate_xp_for_level(self, level):
        """
        Calculate XP required for a given level
        
        Args:
            level (int): The level to calculate XP for
            
        Returns:
            int: XP required to reach this level
        """
        return int(XP_PER_LEVEL * (level ** XP_LEVEL_MULTIPLIER))
    
    def _calculate_max_hp(self):
        """Calculate max HP based on level and base stats"""
        return int(self.base_hp * (1 + 0.1 * (self.level - 1)))
    
    def _calculate_attack(self):
        """Calculate attack based on level and base stats"""
        return int(self.base_attack * (1 + 0.1 * (self.level - 1)))
    
    def _calculate_defense(self):
        """Calculate defense based on level and base stats"""
        return int(self.base_defense * (1 + 0.1 * (self.level - 1)))
    
    def _calculate_magic(self):
        """Calculate magic based on level and base stats"""
        return int(self.base_magic * (1 + 0.1 * (self.level - 1)))
    
    def _calculate_speed(self):
        """Calculate speed based on level and base stats"""
        return int(self.base_speed * (1 + 0.05 * (self.level - 1)))
    
    def to_dict(self):
        """
        Convert character to dictionary for serialization
        
        Returns:
            dict: Character data
        """
        return {
            "name": self.name,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
            "base_hp": self.base_hp,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "base_magic": self.base_magic,
            "base_speed": self.base_speed,
            "current_hp": self.current_hp
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create character from dictionary
        
        Args:
            data (dict): Character data
            
        Returns:
            BaseCharacter: Character instance
        """
        character = cls(data["name"], data["level"])
        character.xp = data["xp"]
        character.xp_to_next_level = data["xp_to_next_level"]
        character.base_hp = data["base_hp"]
        character.base_attack = data["base_attack"]
        character.base_defense = data["base_defense"]
        character.base_magic = data["base_magic"]
        character.base_speed = data["base_speed"]
        
        # Recalculate derived stats
        character.max_hp = character._calculate_max_hp()
        character.attack = character._calculate_attack()
        character.defense = character._calculate_defense()
        character.magic = character._calculate_magic()
        character.speed = character._calculate_speed()
        
        # Set current state
        character.current_hp = data["current_hp"]
        character.alive = character.current_hp > 0
        
        return character
