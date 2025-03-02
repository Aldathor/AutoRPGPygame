# enemy_types.py
"""
Specific enemy type implementations
"""
import random
import pygame
from entities.enemies.enemy_base import Enemy
from game.config import ENEMY_TYPE_MODIFIERS

class Goblin(Enemy):
    """
    Goblin enemy - Fast but weak
    """
    def __init__(self, level=1):
        """Initialize goblin enemy"""
        super().__init__("Goblin", "goblin", level)
        
        # Apply type modifiers
        modifiers = ENEMY_TYPE_MODIFIERS["goblin"]
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
        
        # Adjust XP value
        self.xp_value = int(self.xp_value * modifiers["xp_value"])
        
        # Create a simple placeholder sprite
        self.sprite = pygame.Surface((32, 36))
        self.sprite.fill((100, 200, 100))  # Light green for goblin
    
    def attack_target(self, target):
        """
        Goblin attack - Has a chance to attack twice due to speed
        
        Args:
            target (BaseCharacter): The character to attack
            
        Returns:
            dict: Attack result
        """
        result = super().attack_target(target)
        
        # Goblins have a chance for a quick second attack
        if result["hit"] and target.is_alive() and random.random() < 0.2:
            second_damage = int(self.attack * 0.5)  # Second attack is weaker
            second_result = target.take_damage(second_damage)
            
            result["damage"] += second_result["damage"]
            result["double_attack"] = True
        else:
            result["double_attack"] = False
        
        return result

class Orc(Enemy):
    """
    Orc enemy - Strong but slow
    """
    def __init__(self, level=1):
        """Initialize orc enemy"""
        super().__init__("Orc", "orc", level)
        
        # Apply type modifiers
        modifiers = ENEMY_TYPE_MODIFIERS["orc"]
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
        
        # Adjust XP value
        self.xp_value = int(self.xp_value * modifiers["xp_value"])
        
        # Create a simple placeholder sprite
        self.sprite = pygame.Surface((40, 48))
        self.sprite.fill((150, 100, 50))  # Brown for orc
    
    def attack_target(self, target):
        """
        Orc attack - Powerful with a chance to stun
        
        Args:
            target (BaseCharacter): The character to attack
            
        Returns:
            dict: Attack result
        """
        result = super().attack_target(target)
        
        # Orcs have a chance to stun the target
        if result["hit"] and target.is_alive() and random.random() < 0.15:
            # Stun effect (increase target's cooldown)
            target.attack_cooldown += target.get_attack_cooldown() * 0.5
            result["stun"] = True
        else:
            result["stun"] = False
        
        return result

class Troll(Enemy):
    """
    Troll enemy - Very strong with high HP
    """
    def __init__(self, level=1):
        """Initialize troll enemy"""
        super().__init__("Troll", "troll", level)
        
        # Apply type modifiers
        modifiers = ENEMY_TYPE_MODIFIERS["troll"]
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
        
        # Adjust XP value
        self.xp_value = int(self.xp_value * modifiers["xp_value"])
        
        # Trolls have regeneration
        self.regeneration_rate = int(self.max_hp * 0.02)  # 2% HP regeneration per turn
        
        # Create a simple placeholder sprite
        self.sprite = pygame.Surface((48, 64))
        self.sprite.fill((50, 150, 50))  # Dark green for troll
    
    def update(self, delta_time):
        """
        Update troll with regeneration
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        super().update(delta_time)
        
        # Regenerate health over time if alive
        if self.is_alive() and self.current_hp < self.max_hp:
            # Scale regeneration by time
            regen_amount = int(self.regeneration_rate * delta_time)
            if regen_amount > 0:
                self.heal(regen_amount)

class Skeleton(Enemy):
    """
    Skeleton enemy - Resistant to physical damage but weak against magic
    """
    def __init__(self, level=1):
        """Initialize skeleton enemy"""
        super().__init__("Skeleton", "skeleton", level)
        
        # Apply type modifiers
        modifiers = ENEMY_TYPE_MODIFIERS["skeleton"]
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
        
        # Adjust XP value
        self.xp_value = int(self.xp_value * modifiers["xp_value"])
        
        # Create a simple placeholder sprite
        self.sprite = pygame.Surface((32, 48))
        self.sprite.fill((200, 200, 200))  # White for skeleton
    
    def take_damage(self, damage, damage_type="physical"):
        """
        Take damage with undead resistance
        
        Args:
            damage (int): Amount of damage
            damage_type (str): Type of damage ("physical" or "magical")
            
        Returns:
            dict: Damage result
        """
        if not self.is_alive():
            return {"damage": 0, "hit": False}
        
        # Skeletons resist physical damage but are weak to magic
        if damage_type == "physical":
            damage = int(damage * 0.7)  # 30% physical resistance
        elif damage_type == "magical":
            damage = int(damage * 1.5)  # 50% magical weakness
        
        # Calculate damage reduction
        damage_reduction = self.defense
        
        # Calculate actual damage
        actual_damage = max(1, int(damage - damage_reduction))
        
        # Apply damage
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        # Check if dead
        if self.current_hp <= 0:
            self.alive = False
        
        return {"damage": actual_damage, "hit": True, "damage_type": damage_type}

class Dragon(Enemy):
    """
    Dragon enemy - Powerful boss-like enemy with special abilities
    """
    def __init__(self, level=1):
        """Initialize dragon enemy"""
        super().__init__("Dragon", "dragon", level)
        
        # Apply type modifiers
        modifiers = ENEMY_TYPE_MODIFIERS["dragon"]
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
        
        # Adjust XP value
        self.xp_value = int(self.xp_value * modifiers["xp_value"])
        
        # Track breath weapon cooldown
        self.breath_cooldown = 3.0  # Seconds
        self.breath_timer = 0.0
        
        # Create a simple placeholder sprite
        self.sprite = pygame.Surface((64, 64))
        self.sprite.fill((200, 0, 0))  # Red for dragon
    
    def update(self, delta_time):
        """
        Update dragon state
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        super().update(delta_time)
        
        # Update breath weapon cooldown
        if self.breath_timer > 0:
            self.breath_timer = max(0, self.breath_timer - delta_time)
    
    def attack_target(self, target):
        """
        Dragon attack - Can use breath weapon
        
        Args:
            target (BaseCharacter): The character to attack
            
        Returns:
            dict: Attack result
        """
        if not self.can_attack() or not target.is_alive():
            return {"damage": 0, "hit": False}
        
        # Check if breath weapon is available
        if self.breath_timer <= 0 and random.random() < 0.3:
            # Use breath weapon (magical damage)
            damage = int(self.magic * 2.0)
            damage_result = target.take_damage(damage, damage_type="magical")
            
            # Set breath cooldown
            self.breath_timer = self.breath_cooldown
            
            # Return attack details
            return {
                "damage": damage_result["damage"],
                "hit": damage_result["hit"],
                "breath_weapon": True
            }
        else:
            # Normal attack (physical)
            result = super().attack_target(target)
            result["breath_weapon"] = False
            return result
