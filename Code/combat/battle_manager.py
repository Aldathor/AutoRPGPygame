"""
Battle Manager - Controls combat flow and calculations
"""
from game.config import BATTLE_TIMER_INTERVAL
from ui.combat_log import CombatLog

class BattleManager:
    """
    Manages battles between characters and enemies
    """
    def __init__(self, game_state):
        """
        Initialize the battle manager
        
        Args:
            game_state (GameState): Reference to the game state
        """
        self.game_state = game_state
        self.combat_log = CombatLog()
        self.last_action_time = 0
    
    def update(self, delta_time):
        """
        Update the battle system
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update all combat entities
        if self.game_state.player_character:
            self.game_state.player_character.update(delta_time)
        
        for enemy in self.game_state.enemies:
            if enemy.is_alive():
                enemy.update(delta_time)
        
        # Remove dead enemies
        self.game_state.enemies = [enemy for enemy in self.game_state.enemies if enemy.is_alive()]
        
        # Process battle actions based on timer
        self.last_action_time += delta_time
        if self.last_action_time >= BATTLE_TIMER_INTERVAL:
            self.last_action_time = 0
            self._process_battle_actions()
    
    def _process_battle_actions(self):
        """Process one round of battle actions"""
        player = self.game_state.player_character
        
        # Skip if player is dead or no enemies
        if not player or not player.is_alive() or not self.game_state.enemies:
            return
        
        # Process player action
        if player.can_attack():
            # Select first living enemy
            target = next((enemy for enemy in self.game_state.enemies if enemy.is_alive()), None)
            if target:
                result = player.attack_target(target)
                self._log_attack(player, target, result)
                
                # Check if enemy died
                if not target.is_alive():
                    self._handle_enemy_defeat(target)
        
        # Process enemy actions
        for enemy in self.game_state.enemies:
            if enemy.is_alive() and enemy.can_attack():
                result = enemy.attack_target(player)
                self._log_attack(enemy, player, result)
                
                # Check if player died
                if not player.is_alive():
                    self._log_message(f"{player.name} has been defeated!")
                    break
    
    def _handle_enemy_defeat(self, enemy):
        """
        Handle effects of defeating an enemy
        
        Args:
            enemy (Enemy): The defeated enemy
        """
        player = self.game_state.player_character
        
        # Award XP
        xp_gained = enemy.get_xp_value()
        leveled_up = player.gain_xp(xp_gained)
        
        # Log results
        self._log_message(f"{enemy.name} has been defeated! +{xp_gained} XP")
        if leveled_up:
            self._log_message(f"{player.name} leveled up to level {player.level}!")
    
    def _log_attack(self, attacker, target, result):
        """
        Log an attack to the combat log
        
        Args:
            attacker (BaseCharacter): The attacking character
            target (BaseCharacter): The target character
            result (dict): Attack result
        """
        # Use the combat log component's method
        self.combat_log.log_attack(attacker, target, result)
    
    def _log_message(self, message):
        """
        Add a message to the combat log
        
        Args:
            message (str): The message to log
        """
        # Use the combat log component's method
        self.combat_log.add_entry(message)
    
    def get_recent_log(self, count=10):
        """
        Get the most recent log messages
        
        Args:
            count (int): Number of messages to return
            
        Returns:
            list: Recent combat log messages
        """
        return self.combat_log.get_recent_entries(count)
