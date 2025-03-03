"""
Mage player class
"""
import random
import pygame
from entities.base_character import BaseCharacter
from game.config import CLASS_MODIFIERS, MAGIC_RESISTANCE_BASE

class Mage(BaseCharacter):
    """
    Mage class - High magic and moderate speed, low HP and defense
    Special ability: Magical attacks and spell effects
    """
    def __init__(self, name="Mage", level=1):
        """Initialize mage character"""
        super().__init__(name, level)
        
        # Apply class modifiers to base stats
        modifiers = CLASS_MODIFIERS["mage"]
        self.base_hp = int(self.base_hp * modifiers["hp"])
        self.base_attack = int(self.base_attack * modifiers["attack"])
        self.base_defense = int(self.base_defense * modifiers["defense"])
        self.base_magic = int(self.base_magic * modifiers["magic"])
        self.base_speed = int(self.base_speed * modifiers["speed"])
        
        # Recalculate actual stats
        self.max_hp = self._calculate_max_hp()
        self.attack = self._calculate_attack()
        self.defense = self._calculate_defense()
        self.magic = self._calculate_magic()
        self.speed = self._calculate_speed()
        self.current_hp = self.max_hp
        
        # Special mage properties
        self.spell_effects = {
            "fireball": {"chance": 0.7, "damage_multiplier": 1.0},
            "ice_shard": {"chance": 0.2, "damage_multiplier": 0.8, "slow_effect": 0.5},
            "lightning": {"chance": 0.1, "damage_multiplier": 1.5}
        }
        
        # Replace colored square with ASCII sprite
        from ui.ascii_sprites import get_class_sprite
        self.sprite = get_class_sprite("mage", (0, 0, 200)).surface
    
    def attack_target(self, target):
        """
        Attack a target with a magical spell
        
        Args:
            target (BaseCharacter): The character to attack
            
        Returns:
            dict: Attack result
        """
        if not self.can_attack() or not target.is_alive():
            return {"damage": 0, "hit": False, "spell": None}
        
        # Choose a spell based on random chance
        spell_roll = random.random()
        spell_effect = None
        
        if spell_roll < self.spell_effects["lightning"]["chance"]:
            spell = "lightning"
            damage_multiplier = self.spell_effects["lightning"]["damage_multiplier"]
        elif spell_roll < self.spell_effects["lightning"]["chance"] + self.spell_effects["ice_shard"]["chance"]:
            spell = "ice_shard"
            damage_multiplier = self.spell_effects["ice_shard"]["damage_multiplier"]
            spell_effect = "slow"
        else:
            spell = "fireball"
            damage_multiplier = self.spell_effects["fireball"]["damage_multiplier"]
        
        # Calculate damage (based on magic stat)
        base_damage = int(self.magic * damage_multiplier)
        
        # Apply damage to target (as magical damage)
        damage_result = target.take_damage(base_damage, damage_type="magical")
        
        # Apply spell effect if any
        if spell_effect == "slow" and target.is_alive():
            # Slow the target (increase their cooldown)
            target.attack_cooldown += target.get_attack_cooldown() * self.spell_effects["ice_shard"]["slow_effect"]
        
        # Reset cooldown
        self.attack_cooldown = self.get_attack_cooldown()
        
        # Return attack details
        return {
            "damage": damage_result["damage"],
            "hit": damage_result["hit"],
            "spell": spell,
            "effect": spell_effect
        }
    
    def take_damage(self, damage, damage_type="physical"):
        """
        Take damage with mage's magical resistance
        
        Args:
            damage (int): Amount of damage
            damage_type (str): Type of damage ("physical" or "magical")
            
        Returns:
            dict: Damage result
        """
        if not self.is_alive():
            return {"damage": 0, "hit": False}
        
        # Mages have better magical resistance
        if damage_type == "magical":
            magic_resistance = MAGIC_RESISTANCE_BASE + (self.magic * 0.01)
            damage = int(damage * (1 - magic_resistance))
        
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

    def get_animation_type(self):
        """Get the animation type for mages"""
        return "spell"
