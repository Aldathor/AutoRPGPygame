"""
Enemy Spawner - Generates enemies of varying difficulty for party battles
"""
import random
from entities.enemies.enemy_types import Goblin, Orc, Troll, Skeleton, Dragon
from game.config import (
    ENEMY_SPAWN_BASE_TIME, ENEMY_TYPES, MAX_ENEMY_COUNT, 
    ENEMY_TARGETING_PRIORITIES
)

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
        
        # Track current battle difficulty
        self.current_difficulty = 1.0
        self.boss_battle_counter = 0  # Count battles until boss appears
        
        # Flag to prevent spawning during combat
        self.initial_spawn_done = False
    
    def update(self, delta_time):
        """
        Update the spawner
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # We no longer spawn enemies continuously during combat
        # This method is kept for compatibility but doesn't do anything
        pass
    
    def reset_for_new_battle(self):
        """Reset spawner state for a new battle"""
        self.initial_spawn_done = False
    
    def spawn_enemy(self):
        """
        Spawn a new enemy based on party strength
        
        Returns:
            Enemy: The spawned enemy
        """
        # Calculate average party level
        party_levels = [char.level for char in self.game_state.party if char and char.is_alive()]
        if not party_levels:
            return None
            
        avg_party_level = sum(party_levels) / len(party_levels)
        max_party_level = max(party_levels)
        
        # Calculate appropriate enemy level based on party level and difficulty
        level_range = max(1, int(avg_party_level * 0.2))  # Allow some variation in enemy level
        base_level = max(1, int(avg_party_level * self.current_difficulty))
        enemy_level = max(1, random.randint(base_level - level_range, base_level + level_range))
        
        # Cap enemy level relative to max party level to avoid extreme difficulty
        enemy_level = min(enemy_level, max_party_level + 2)
        
        # Determine enemy type based on party level and chance
        enemy_type = self._select_enemy_type(avg_party_level)
        
        # Create the enemy
        enemy_class = self.enemy_classes.get(enemy_type)
        if not enemy_class:
            print(f"Unknown enemy type: {enemy_type}")
            return None
        
        enemy = enemy_class(enemy_level)
        
        # Assign targeting priority based on enemy type
        enemy.targeting_priority = ENEMY_TARGETING_PRIORITIES.get(enemy_type, "random")
        
        # Add to game state if below max enemies
        if len(self.game_state.enemies) < MAX_ENEMY_COUNT:
            self.game_state.enemies.append(enemy)
            print(f"Spawned {enemy.name} (Level {enemy.level}) with targeting: {enemy.targeting_priority}")
            return enemy
        
        return None
    
    def spawn_enemy_group(self, count=None):
        """
        Spawn a group of enemies
        
        Args:
            count (int, optional): Number of enemies to spawn, if None will determine based on party
            
        Returns:
            list: Spawned enemies
        """
        # Determine number of enemies to spawn based on party size if not specified
        if count is None:
            living_party_count = sum(1 for char in self.game_state.party if char and char.is_alive())
            
            # Spawn 1-3 enemies based on party size
            if living_party_count <= 1:
                count = random.randint(1, 2)  # 1-2 enemies for single character
            elif living_party_count == 2:
                count = random.randint(2, 3)  # 2-3 enemies for two characters
            else:
                count = MAX_ENEMY_COUNT  # Full enemy group for full party
        
        # Cap at maximum enemies
        count = min(count, MAX_ENEMY_COUNT)
        
        # Clear existing enemies
        self.game_state.enemies = []
        
        # Spawn the enemies
        spawned_enemies = []
        for _ in range(count):
            enemy = self.spawn_enemy()
            if enemy:
                spawned_enemies.append(enemy)
        
        # Mark that initial spawn is done
        self.initial_spawn_done = True
        
        return spawned_enemies
    
    def _select_enemy_type(self, party_level):
        """
        Select an enemy type based on party level
        
        Args:
            party_level (float): Average party level
            
        Returns:
            str: The selected enemy type
        """
        # Calculate probabilities based on party level
        probabilities = self._calculate_enemy_probabilities(party_level)
        
        # Roll for enemy type
        roll = random.random()
        cumulative_prob = 0
        
        for enemy_type, prob in probabilities.items():
            cumulative_prob += prob
            if roll <= cumulative_prob:
                return enemy_type
        
        # Fallback to goblin
        return "goblin"
    
    def _calculate_enemy_probabilities(self, party_level):
        """
        Calculate spawn probabilities based on party level
        
        Args:
            party_level (float): Average party level
            
        Returns:
            dict: Enemy types and their spawn probabilities
        """
        probabilities = {}
        
        # Base probabilities for level 1
        if party_level <= 3:
            probabilities = {
                "goblin": 0.7,
                "orc": 0.25,
                "skeleton": 0.05,
                "troll": 0.0,
                "dragon": 0.0
            }
        # Mid-level probabilities
        elif party_level <= 7:
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
        
        # Adjust probabilities for boss battle
        if self.boss_battle_counter >= 5:  # Every 5 battles, increase dragon chance
            # Increase dragon probability for boss battle
            for enemy_type in probabilities:
                if enemy_type == "dragon":
                    probabilities[enemy_type] = 0.4  # 40% chance for dragon
                else:
                    # Reduce other probabilities proportionally
                    probabilities[enemy_type] *= 0.6
                    
        return probabilities
    
    def spawn_boss(self):
        """
        Spawn a boss enemy
        
        Returns:
            Enemy: The spawned boss
        """
        # Calculate average party level
        party_levels = [char.level for char in self.game_state.party if char and char.is_alive()]
        if not party_levels:
            return None
            
        avg_party_level = sum(party_levels) / len(party_levels)
        
        # Boss is always a dragon with level higher than party
        boss_level = int(avg_party_level) + 2
        boss = Dragon(boss_level)
        
        # Set boss targeting priority
        boss.targeting_priority = "magical"  # Target highest magic character
        
        # Clear existing enemies and add boss
        self.game_state.enemies = [boss]
        print(f"Spawned Boss: {boss.name} (Level {boss.level})")
        
        # Reset boss battle counter
        self.boss_battle_counter = 0
        
        # Mark that initial spawn is done
        self.initial_spawn_done = True
        
        return boss
    
    def check_for_boss_battle(self):
        """
        Check if it's time for a boss battle
        
        Returns:
            bool: True if it's a boss battle, False otherwise
        """
        # Increment boss battle counter
        self.boss_battle_counter += 1
        
        # Every 5 battles, spawn a boss
        if self.boss_battle_counter >= 5:
            return True
            
        return False
    
    def increase_difficulty(self, amount=0.05):
        """
        Increase the difficulty level
        
        Args:
            amount (float, optional): Amount to increase difficulty
        """
        self.current_difficulty += amount
        print(f"Difficulty increased to {self.current_difficulty:.2f}")