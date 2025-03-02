# enemy_base.py
"""
Base enemy class with party-system targeting support
"""
import random
import pygame
from entities.base_character import BaseCharacter
from game.config import XP_GAIN_BASE

class Enemy(BaseCharacter):
    """
    Base class for all enemies
    """
    def __init__(self, name, enemy_type, level=1):
        """
        Initialize an enemy
        
        Args:
            name (str): Enemy name
            enemy_type (str): Type of enemy
            level (int): Enemy level
        """
        super().__init__(name, level)
        self.enemy_type = enemy_type
        self.xp_value = int(XP_GAIN_BASE * level)
        self.targeting_priority = "random"  # Default targeting priority
        
        # Create placeholder sprite
        self.sprite = pygame.Surface((32, 48))
        self.sprite.fill((150, 150, 150))  # Gray for generic enemy
    
    def select_target(self, party):
        """
        Select a target from the party based on targeting priority
        
        Args:
            party (list): List of party members
            
        Returns:
            BaseCharacter: Selected target or None if no valid targets
        """
        # Filter to only living party members
        living_party = [char for char in party if char and char.is_alive()]
        
        if not living_party:
            return None
            
        # Select target based on priority
        if self.targeting_priority == "random":
            return random.choice(living_party)
        elif self.targeting_priority == "weakest":
            # Target character with lowest HP percentage
            return min(living_party, key=lambda char: char.current_hp / char.max_hp)
        elif self.targeting_priority == "strongest":
            # Target character with highest attack
            return max(living_party, key=lambda char: char.attack)
        elif self.targeting_priority == "magical":
            # Target character with highest magic
            return max(living_party, key=lambda char: char.magic)
        else:
            # Default to random if unknown priority
            return random.choice(living_party)
    
    def attack_target(self, target):
        """
        Basic enemy attack
        
        Args:
            target (BaseCharacter): The character to attack
            
        Returns:
            dict: Attack result
        """
        if not self.can_attack() or not target.is_alive():
            return {"damage": 0, "hit": False}
        
        # Calculate damage
        base_damage = self.attack
        
        # Apply damage to target
        damage_result = target.take_damage(base_damage)
        
        # Reset cooldown
        self.attack_cooldown = self.get_attack_cooldown()
        
        # Return attack details
        return {
            "damage": damage_result["damage"],
            "hit": damage_result["hit"]
        }
    
    def take_damage(self, damage, damage_type="physical"):
        """
        Take damage
        
        Args:
            damage (int): Amount of damage
            damage_type (str): Type of damage ("physical" or "magical")
            
        Returns:
            dict: Damage result
        """
        if not self.is_alive():
            return {"damage": 0, "hit": False}
        
        # Calculate damage reduction
        damage_reduction = self.defense
        
        # Calculate actual damage
        actual_damage = max(1, int(damage - damage_reduction))
        
        # Apply damage
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        # Check if dead
        if self.current_hp <= 0:
            self.alive = False
        
        return {"damage": actual_damage, "hit": True}
    
    def get_xp_value(self):
        """
        Get the XP value of defeating this enemy
        
        Returns:
            int: XP value
        """
        return self.xp_value