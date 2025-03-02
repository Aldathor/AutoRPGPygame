"""
Enemy Spawner - Generates enemies of varying difficulty
"""
import random
from entities.enemies.enemy_types import Goblin, Orc, Troll, Skeleton, Dragon
from game.config import ENEMY_SPAWN_BASE_TIME, ENEMY_TYPES

class EnemySpawner:
    """
    Handles spawning of enemies with appropriate difficulty
    """
    def __init__(self, game_state):
        """
        Initialize the enemy spawner
        
        Args:
            game_state (GameState): Reference to the game state
        """
        self.game_state = game_state
        self.spawn_timer = 0
        self.spawn_interval = ENEMY_SPAWN_BASE_TIME
        self.enemy_classes = {
            "goblin": Goblin,
            "orc": Orc,
            "troll": Troll,
            "skeleton": Skeleton,
            "dragon": Dragon
        }
    
    def update(self, delta_time):
        """
        Update the spawner
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Only spawn if in battle and there are no enemies
        if not self.game_state.enemies:
            self.spawn_timer += delta_time
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0
                self.spawn_enemy()
    
    def spawn_enemy(self):
        """
        Spawn a new enemy based on player level
        
        Returns:
            Enemy: The spawned enemy
        """
        player = self.game_state.player_character
        if not player:
            return None
        
        # Calculate appropriate enemy level based on player level
        player_level = player.level
        level_range = max(1, int(player_level * 0.2))  # Allow some variation in enemy level
        enemy_level = max(1, random.randint(player_level - level_range, player_level + level_range))
        
        # Determine enemy type based on player level and chance
        enemy_type = self._select_enemy_type(player_level)
        
        # Create the enemy
        enemy_class = self.enemy_classes.get(enemy_type)
        if not enemy_class:
            print(f"Unknown enemy type: {enemy_type}")
            return None
        
        enemy = enemy_class(enemy_level)
        
        # Add to game state
        self.game_state.enemies.append(enemy)
        print(f"Spawned {enemy.name} (Level {enemy.level})")
        
        return enemy
    
    def _select_enemy_type(self, player_level):
        """
        Select an enemy type based on player level
        
        Args:
            player_level (int): Player's current level
            
        Returns:
            str: The selected enemy type
        """
        # Calculate probabilities based on player level
        probabilities = self._calculate_enemy_probabilities(player_level)
        
        # Roll for enemy type
        roll = random.random()
        cumulative_prob = 0
        
        for enemy_type, prob in probabilities.items():
            cumulative_prob += prob
            if roll <= cumulative_prob:
                return enemy_type
        
        # Fallback to goblin
        return "goblin"
    
    def _calculate_enemy_probabilities(self, player_level):
        """
        Calculate spawn probabilities based on player level
        
        Args:
            player_level (int): Player's current level
            
        Returns:
            dict: Enemy types and their spawn probabilities
        """
        probabilities = {}
        
        # Base probabilities for level 1
        if player_level <= 3:
            probabilities = {
                "goblin": 0.7,
                "orc": 0.25,
                "skeleton": 0.05,
                "troll": 0.0,
                "dragon": 0.0
            }
        # Mid-level probabilities
        elif player_level <= 7:
            probabilities = {
                "goblin": 0.4,
                "orc": 0.3,
                "skeleton": 0.2,
                "troll": 0.1,
                "dragon": 0.0
            }
        # High-level probabilities
        else:
            probabilities = {
                "goblin": 0.2,
                "orc": 0.3,
                "skeleton": 0.2,
                "troll": 0.2,
                "dragon": 0.1
            }
        
        return probabilities
    
    def spawn_boss(self):
        """
        Spawn a boss enemy
        
        Returns:
            Enemy: The spawned boss
        """
        player = self.game_state.player_character
        if not player:
            return None
        
        # Boss is always a dragon with level higher than player
        boss_level = player.level + 2
        boss = Dragon(boss_level)
        
        # Add to game state
        self.game_state.enemies.append(boss)
        print(f"Spawned Boss: {boss.name} (Level {boss.level})")
        
        return boss
