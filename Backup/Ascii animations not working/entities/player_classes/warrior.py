"""
Warrior player class
"""
import random
import pygame
from entities.base_character import BaseCharacter
from game.config import CLASS_MODIFIERS, CRITICAL_HIT_CHANCE, CRITICAL_HIT_MULTIPLIER

class Warrior(BaseCharacter):
    """
    Warrior class - High HP and physical damage, low magic and speed
    Special ability: Higher critical hit chance
    """
    def __init__(self, name="Warrior", level=1):
        """Initialize warrior character"""
        super().__init__(name, level)
        
        # Apply class modifiers to base stats
        modifiers = CLASS_MODIFIERS["warrior"]
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
        
        # Special warrior properties
        self.critical_hit_chance = CRITICAL_HIT_CHANCE * 1.5  # 50% higher crit chance
        
        # Replace colored square with ASCII sprite
        from ui.ascii_sprites import get_class_sprite
        self.sprite = get_class_sprite("warrior", (200, 0, 0)).surface
    
    def attack_target(self, target):
        """
        Attack a target with a chance for critical hit
        
        Args:
            target (BaseCharacter): The character to attack
            
        Returns:
            dict: Attack result
        """
        if not self.can_attack() or not target.is_alive():
            return {"damage": 0, "hit": False, "critical": False}
        
        # Calculate damage
        base_damage = self.attack
        
        # Check for critical hit
        is_critical = random.random() < self.critical_hit_chance
        if is_critical:
            base_damage = int(base_damage * CRITICAL_HIT_MULTIPLIER)
        
        # Apply damage to target
        damage_result = target.take_damage(base_damage)
        
        # Reset cooldown
        self.attack_cooldown = self.get_attack_cooldown()
        
        # Return attack details
        return {
            "damage": damage_result["damage"],
            "hit": damage_result["hit"],
            "critical": is_critical
        }
    
    def take_damage(self, damage, damage_type="physical"):
        """
        Take damage with warrior's high physical resistance
        
        Args:
            damage (int): Amount of damage
            damage_type (str): Type of damage ("physical" or "magical")
            
        Returns:
            dict: Damage result
        """
        if not self.is_alive():
            return {"damage": 0, "hit": False}
        
        # Warriors have better physical resistance
        if damage_type == "physical":
            damage_reduction = self.defense * 1.2  # 20% better physical reduction
        else:
            damage_reduction = self.defense * 0.5  # 50% worse magical reduction
        
        # Calculate actual damage
        actual_damage = max(1, int(damage - damage_reduction))
        
        # Apply damage
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        # Check if dead
        if self.current_hp <= 0:
            self.alive = False
        
        return {"damage": actual_damage, "hit": True}

    def get_animation_type(self):
        """Get the animation type for warriors"""
        return "slash"
