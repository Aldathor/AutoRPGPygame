"""
Unit tests for AI behavior
"""
import unittest
from unittest.mock import MagicMock, patch
from entities.player_classes.warrior import Warrior
from entities.enemies.enemy_types import Goblin, Dragon
from combat.enemy_spawner import EnemySpawner
from game.game_state import GameState

class TestEnemyAI(unittest.TestCase):
    """Test cases for enemy AI behavior"""
    
    def setUp(self):
        """Set up test objects"""
        self.warrior = Warrior("TestWarrior", level=5)
        self.goblin = Goblin(level=3)
        self.dragon = Dragon(level=7)
        
        # Reset cooldowns
        self.warrior.attack_cooldown = 0
        self.goblin.attack_cooldown = 0
        self.dragon.attack_cooldown = 0
        
        # Ensure characters are alive
        self.warrior.current_hp = self.warrior.max_hp
        self.goblin.current_hp = self.goblin.max_hp
        self.dragon.current_hp = self.dragon.max_hp
    
    def test_goblin_attack_behavior(self):
        """Test goblin attack behavior"""
        # Goblins have a chance for double attack
        attack_result = self.goblin.attack_target(self.warrior)
        
        # Verify attack result structure
        self.assertIn("damage", attack_result)
        self.assertIn("hit", attack_result)
        self.assertIn("double_attack", attack_result)
        
        # After attack, cooldown should be set
        self.assertGreater(self.goblin.attack_cooldown, 0)
    
    def test_dragon_breath_weapon(self):
        """Test dragon breath weapon"""
        # Force breath weapon by setting breath timer to 0 and mocking random
        self.dragon.breath_timer = 0
        
        with patch('random.random', return_value=0.1):  # Return value < 0.3 to trigger breath
            attack_result = self.dragon.attack_target(self.warrior)
            
            # Verify breath weapon was used
            self.assertIn("breath_weapon", attack_result)
            self.assertTrue(attack_result["breath_weapon"])
            
            # Breath cooldown should be set
            self.assertGreater(self.dragon.breath_timer, 0)
    
    def test_dragon_regular_attack(self):
        """Test dragon regular attack when breath not available"""
        # Set breath on cooldown
        self.dragon.breath_timer = self.dragon.breath_cooldown
        
        attack_result = self.dragon.attack_target(self.warrior)
        
        # Verify regular attack was used
        self.assertIn("breath_weapon", attack_result)
        self.assertFalse(attack_result["breath_weapon"])
    
    def test_enemy_targets_player(self):
        """Test that enemy targets player properly"""
        # Both should be able to attack
        self.assertTrue(self.goblin.can_attack())
        self.assertTrue(self.warrior.is_alive())
        
        # Goblin should target player
        result = self.goblin.attack_target(self.warrior)
        
        # Attack should hit and damage player
        self.assertTrue(result["hit"])
        self.assertGreater(result["damage"], 0)
        self.assertLess(self.warrior.current_hp, self.warrior.max_hp)

class TestEnemySpawner(unittest.TestCase):
    """Test cases for enemy spawner"""
    
    def setUp(self):
        """Set up test objects"""
        self.game_state = GameState()
        self.game_state.player_character = Warrior("TestWarrior", level=5)
        self.spawner = EnemySpawner(self.game_state)
    
    def test_enemy_spawn(self):
        """Test basic enemy spawning"""
        # Initially no enemies
        self.assertEqual(len(self.game_state.enemies), 0)
        
        # Spawn an enemy
        enemy = self.spawner.spawn_enemy()
        
        # Should have created an enemy
        self.assertIsNotNone(enemy)
        
        # Enemy should be added to game state
        self.assertEqual(len(self.game_state.enemies), 1)
        self.assertEqual(self.game_state.enemies[0], enemy)
        
        # Enemy level should be appropriate for player level
        self.assertGreaterEqual(enemy.level, 1)
        self.assertLessEqual(enemy.level, self.game_state.player_character.level + 3)
    
    def test_enemy_type_selection(self):
        """Test enemy type selection based on player level"""
        # Test for low level player (expected mostly goblins)
        self.game_state.player_character.level = 1
        type_counts = self._count_enemy_types(100)
        self.assertGreater(type_counts.get("goblin", 0), 50)  # Over 50% should be goblins
        
        # Test for high level player (should have more variety)
        self.game_state.player_character.level = 10
        type_counts = self._count_enemy_types(100)
        self.assertLess(type_counts.get("goblin", 0), 50)  # Less than 50% should be goblins
        self.assertGreater(type_counts.get("dragon", 0), 1)  # Should have some dragons
    
    def test_boss_spawn(self):
        """Test boss enemy spawning"""
        # Spawn a boss
        boss = self.spawner.spawn_boss()
        
        # Should be a dragon
        self.assertEqual(boss.enemy_type, "dragon")
        
        # Boss level should be higher than player
        self.assertGreater(boss.level, self.game_state.player_character.level)
        
        # Boss should be added to game state
        self.assertIn(boss, self.game_state.enemies)
    
    def _count_enemy_types(self, count):
        """
        Helper to count spawned enemy types
        
        Args:
            count (int): Number of enemies to spawn
            
        Returns:
            dict: Count of each enemy type
        """
        # Clear existing enemies
        self.game_state.enemies = []
        
        # Mock spawn_enemy to not add to game state
        original_spawn = self.spawner.spawn_enemy
        
        def spawn_without_adding():
            self.game_state.enemies = []
            return original_spawn()
        
        self.spawner.spawn_enemy = spawn_without_adding
        
        # Spawn enemies and count types
        type_counts = {}
        for _ in range(count):
            enemy = self.spawner.spawn_enemy()
            enemy_type = enemy.enemy_type
            type_counts[enemy_type] = type_counts.get(enemy_type, 0) + 1
        
        return type_counts

if __name__ == '__main__':
    unittest.main()
