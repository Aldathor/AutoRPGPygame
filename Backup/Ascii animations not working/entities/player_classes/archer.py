"""
Archer player class
"""
import random
import pygame
from entities.base_character import BaseCharacter
from game.config import CLASS_MODIFIERS, DODGE_CHANCE_BASE, DODGE_CHANCE_PER_SPEED

class Archer(BaseCharacter):
    """
    Archer class - High speed and moderate attack, low HP and defense
    Special ability: Dodge chance and multi-hit attacks
    """
    def __init__(self, name="Archer", level=1):
        """Initialize archer character"""
        super().__init__(name, level)
        
        # Apply class modifiers to base stats
        modifiers = CLASS_MODIFIERS["archer"]
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
        
        # Special archer properties
        self.dodge_chance = DODGE_CHANCE_BASE + (self.speed * DODGE_CHANCE_PER_SPEED)
        self.multi_hit_chance = 0.3  # 30% chance to hit multiple times
        
        # Replace colored square with ASCII sprite
        from ui.ascii_sprites import get_class_sprite
        self.sprite = get_class_sprite("archer", (0, 200, 0)).surface
    
    def attack_target(self, target):
        """
        Attack a target with a chance for multiple hits
        
        Args:
            target (BaseCharacter): The character to attack
            
        Returns:
            dict: Attack result
        """
        if not self.can_attack() or not target.is_alive():
            return {"damage": 0, "hit": False, "multi_hit": False}
        
        # Calculate damage
        base_damage = int(self.attack * 0.8)  # Base hit is slightly weaker
        total_damage = 0
        hits = 1
        
        # Check for multi-hit
        is_multi_hit = random.random() < self.multi_hit_chance
        
        # Apply base hit
        damage_result = target.take_damage(base_damage)
        total_damage += damage_result["damage"]
        
        # Apply additional hits if multi-hit
        if is_multi_hit and target.is_alive():
            # Between 1-2 additional hits
            additional_hits = random.randint(1, 2)
            for _ in range(additional_hits):
                # Each additional hit does less damage
                hit_damage = int(base_damage * 0.5)
                hit_result = target.take_damage(hit_damage)
                total_damage += hit_result["damage"]
                hits += 1
                if not target.is_alive():
                    break
        
        # Reset cooldown
        self.attack_cooldown = self.get_attack_cooldown()
        
        # Return attack details
        return {
            "damage": total_damage,
            "hit": damage_result["hit"],
            "multi_hit": is_multi_hit,
            "hits": hits
        }
    
    def take_damage(self, damage, damage_type="physical"):
        """
        Take damage with chance to dodge
        
        Args:
            damage (int): Amount of damage
            damage_type (str): Type of damage ("physical" or "magical")
            
        Returns:
            dict: Damage result
        """
        if not self.is_alive():
            return {"damage": 0, "hit": False}
        
        # Check for dodge
        dodge_roll = random.random()
        if dodge_roll < self.dodge_chance:
            return {"damage": 0, "hit": False, "dodged": True}
        
        # Calculate damage reduction
        damage_reduction = self.defense
        
        # Calculate actual damage
        actual_damage = max(1, int(damage - damage_reduction))
        
        # Apply damage
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        # Check if dead
        if self.current_hp <= 0:
            self.alive = False
        
        return {"damage": actual_damage, "hit": True, "dodged": False}

    def get_animation_type(self):
        """Get the animation type for archers"""
        return "arrow"
