"""
Combat Calculator - Handles damage calculations and combat mechanics
"""
import random
from game.config import (
    CRITICAL_HIT_CHANCE, CRITICAL_HIT_MULTIPLIER,
    DODGE_CHANCE_BASE, DODGE_CHANCE_PER_SPEED,
    MAGIC_RESISTANCE_BASE, MAGIC_RESISTANCE_PER_DEFENSE
)

class CombatCalculator:
    """
    Static class for combat calculations
    """
    @staticmethod
    def calculate_physical_damage(attacker, defender, base_damage=None):
        """
        Calculate physical damage
        
        Args:
            attacker (BaseCharacter): The attacking character
            defender (BaseCharacter): The defending character
            base_damage (int, optional): Override for base damage
            
        Returns:
            dict: Damage calculation result
        """
        # Use attacker's attack stat if base_damage not provided
        if base_damage is None:
            base_damage = attacker.attack
        
        # Check for dodge
        dodge_chance = CombatCalculator.calculate_dodge_chance(defender)
        if random.random() < dodge_chance:
            return {
                "damage": 0,
                "hit": False,
                "dodged": True,
                "critical": False
            }
        
        # Check for critical hit
        is_critical = random.random() < CRITICAL_HIT_CHANCE
        damage_multiplier = CRITICAL_HIT_MULTIPLIER if is_critical else 1.0
        
        # Calculate damage reduction from defense
        damage_reduction = defender.defense
        
        # Calculate final damage
        damage = max(1, int((base_damage * damage_multiplier) - damage_reduction))
        
        return {
            "damage": damage,
            "hit": True,
            "dodged": False,
            "critical": is_critical
        }
    
    @staticmethod
    def calculate_magical_damage(attacker, defender, base_damage=None):
        """
        Calculate magical damage
        
        Args:
            attacker (BaseCharacter): The attacking character
            defender (BaseCharacter): The defending character
            base_damage (int, optional): Override for base damage
            
        Returns:
            dict: Damage calculation result
        """
        # Use attacker's magic stat if base_damage not provided
        if base_damage is None:
            base_damage = attacker.magic
        
        # Calculate magic resistance
        magic_resistance = CombatCalculator.calculate_magic_resistance(defender)
        
        # Apply resistance
        damage = int(base_damage * (1 - magic_resistance))
        
        # Ensure minimum damage
        damage = max(1, damage)
        
        return {
            "damage": damage,
            "hit": True,
            "magical": True
        }
    
    @staticmethod
    def calculate_dodge_chance(character):
        """
        Calculate a character's chance to dodge
        
        Args:
            character (BaseCharacter): The character
            
        Returns:
            float: Dodge chance (0.0 to 1.0)
        """
        dodge_chance = DODGE_CHANCE_BASE + (character.speed * DODGE_CHANCE_PER_SPEED)
        # Cap dodge chance at 50%
        return min(0.5, dodge_chance)
    
    @staticmethod
    def calculate_magic_resistance(character):
        """
        Calculate a character's magic resistance
        
        Args:
            character (BaseCharacter): The character
            
        Returns:
            float: Magic resistance (0.0 to 1.0)
        """
        resistance = MAGIC_RESISTANCE_BASE + (character.defense * MAGIC_RESISTANCE_PER_DEFENSE)
        # Cap resistance at 75%
        return min(0.75, resistance)
    
    @staticmethod
    def calculate_xp_gain(character, enemy):
        """
        Calculate XP gained from defeating an enemy
        
        Args:
            character (BaseCharacter): The player character
            enemy (Enemy): The defeated enemy
            
        Returns:
            int: XP amount
        """
        base_xp = enemy.get_xp_value()
        
        # Apply level difference modifier
        level_diff = enemy.level - character.level
        if level_diff > 0:
            # Bonus XP for defeating higher level enemies
            xp_multiplier = 1.0 + (0.1 * level_diff)
        else:
            # Reduced XP for defeating lower level enemies
            xp_multiplier = max(0.5, 1.0 + (0.05 * level_diff))
        
        # Calculate final XP
        return max(1, int(base_xp * xp_multiplier))
