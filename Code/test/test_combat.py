"""
Unit tests for combat system
"""
import unittest
from entities.player_classes.warrior import Warrior
from entities.player_classes.archer import Archer
from entities.player_classes.mage import Mage
from entities.enemies.enemy_types import Goblin, Orc, Dragon
from combat.combat_calculator import CombatCalculator

class TestCombatCalculations(unittest.TestCase):
    """Test cases for combat calculations"""
    
    def setUp(self):
        """Set up test characters"""
        self.warrior = Warrior("TestWarrior", level=5)
        self.archer = Archer("TestArcher", level=5)
        self.mage = Mage("TestMage", level=5)
        self.goblin = Goblin(level=3)
        self.orc = Orc(level=5)
        self.dragon = Dragon(level=8)
        
        # Ensure predictable HP values for damage tests
        self.warrior.current_hp = self.warrior.max_hp
        self.archer.current_hp = self.archer.max_hp
        self.mage.current_hp = self.mage.max_hp
        self.goblin.current_hp = self.goblin.max_hp
        self.orc.current_hp = self.orc.max_hp
        self.dragon.current_hp = self.dragon.max_hp
    
    def test_physical_damage_calculation(self):
        """Test physical damage calculation"""
        # Test with fixed damage amount for consistent testing
        result = CombatCalculator.calculate_physical_damage(self.warrior, self.goblin, 50)
        
        # Verify result structure
        self.assertIn("damage", result)
        self.assertIn("hit", result)
        self.assertIn("dodged", result)
        self.assertIn("critical", result)
        
        # Damage should be positive (unless dodged, which we handle separately)
        if result["hit"]:
            self.assertGreater(result["damage"], 0)
    
    def test_magical_damage_calculation(self):
        """Test magical damage calculation"""
        # Test with fixed damage amount for consistent testing
        result = CombatCalculator.calculate_magical_damage(self.mage, self.orc, 50)
        
        # Verify result structure
        self.assertIn("damage", result)
        self.assertIn("hit", result)
        self.assertIn("magical", result)
        
        # Damage should be positive
        self.assertGreater(result["damage"], 0)
    
    def test_dodge_chance_calculation(self):
        """Test dodge chance calculation"""
        # Archer should have higher dodge chance than warrior
        archer_dodge = CombatCalculator.calculate_dodge_chance(self.archer)
        warrior_dodge = CombatCalculator.calculate_dodge_chance(self.warrior)
        
        self.assertGreater(archer_dodge, warrior_dodge)
        
        # Dodge chance should be between 0 and 0.5 (50%)
        self.assertGreaterEqual(archer_dodge, 0.0)
        self.assertLessEqual(archer_dodge, 0.5)
    
    def test_magic_resistance_calculation(self):
        """Test magic resistance calculation"""
        # Warrior should have higher magic resistance due to higher defense
        warrior_resist = CombatCalculator.calculate_magic_resistance(self.warrior)
        mage_resist = CombatCalculator.calculate_magic_resistance(self.mage)
        
        self.assertGreater(warrior_resist, mage_resist)
        
        # Resistance should be between 0 and 0.75 (75%)
        self.assertGreaterEqual(warrior_resist, 0.0)
        self.assertLessEqual(warrior_resist, 0.75)
    
    def test_xp_gain_calculation(self):
        """Test XP gain calculation"""
        # Higher level enemy should give more XP
        xp_from_goblin = CombatCalculator.calculate_xp_gain(self.warrior, self.goblin)
        xp_from_dragon = CombatCalculator.calculate_xp_gain(self.warrior, self.dragon)
        
        self.assertGreater(xp_from_dragon, xp_from_goblin)
        
        # XP should be positive
        self.assertGreater(xp_from_goblin, 0)
        self.assertGreater(xp_from_dragon, 0)

class TestCharacterCombat(unittest.TestCase):
    """Test cases for character combat abilities"""
    
    def setUp(self):
        """Set up test characters"""
        self.warrior = Warrior("TestWarrior", level=5)
        self.archer = Archer("TestArcher", level=5)
        self.mage = Mage("TestMage", level=5)
        self.goblin = Goblin(level=3)
        
        # Reset cooldowns
        self.warrior.attack_cooldown = 0
        self.archer.attack_cooldown = 0
        self.mage.attack_cooldown = 0
        self.goblin.attack_cooldown = 0
        
        # Ensure full HP
        self.goblin.current_hp = self.goblin.max_hp
    
    def test_warrior_attack(self):
        """Test warrior attack ability"""
        # Warrior should be able to attack
        self.assertTrue(self.warrior.can_attack())
        
        # Perform attack
        result = self.warrior.attack_target(self.goblin)
        
        # Verify attack result
        self.assertIn("damage", result)
        self.assertIn("hit", result)
        self.assertIn("critical", result)
        
        # Attack should set cooldown
        self.assertGreater(self.warrior.attack_cooldown, 0)
        
        # Should not be able to attack while on cooldown
        self.assertFalse(self.warrior.can_attack())
    
    def test_archer_attack(self):
        """Test archer attack ability"""
        # Archer should be able to attack
        self.assertTrue(self.archer.can_attack())
        
        # Perform attack
        result = self.archer.attack_target(self.goblin)
        
        # Verify attack result
        self.assertIn("damage", result)
        self.assertIn("hit", result)
        self.assertIn("multi_hit", result)
        
        # If multi-hit occurred, should have more than 1 hit
        if result["multi_hit"]:
            self.assertGreater(result["hits"], 1)
        
        # Attack should set cooldown
        self.assertGreater(self.archer.attack_cooldown, 0)
    
    def test_mage_attack(self):
        """Test mage attack ability"""
        # Mage should be able to attack
        self.assertTrue(self.mage.can_attack())
        
        # Perform attack
        result = self.mage.attack_target(self.goblin)
        
        # Verify attack result
        self.assertIn("damage", result)
        self.assertIn("hit", result)
        self.assertIn("spell", result)
        
        # Should have a valid spell type
        self.assertIn(result["spell"], ["fireball", "ice_shard", "lightning"])
        
        # Attack should set cooldown
        self.assertGreater(self.mage.attack_cooldown, 0)
    
    def test_taking_damage(self):
        """Test taking damage"""
        initial_hp = self.warrior.current_hp
        
        # Apply damage to warrior
        damage_result = self.warrior.take_damage(20)
        
        # Verify damage was applied
        self.assertLess(self.warrior.current_hp, initial_hp)
        
        # Verify result structure
        self.assertIn("damage", damage_result)
        self.assertIn("hit", damage_result)
        
        # Damage taken should match result
        self.assertEqual(initial_hp - self.warrior.current_hp, damage_result["damage"])
    
    def test_death_on_damage(self):
        """Test character death when HP reaches 0"""
        # Set HP low
        self.goblin.current_hp = 1
        
        # Verify alive before attack
        self.assertTrue(self.goblin.is_alive())
        
        # Apply fatal damage
        self.goblin.take_damage(50)
        
        # Verify character is dead
        self.assertFalse(self.goblin.is_alive())
        self.assertEqual(self.goblin.current_hp, 0)

if __name__ == '__main__':
    unittest.main()
