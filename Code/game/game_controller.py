"""
Main game controller
"""
import pygame
from game.game_state import GameState
from game.config import (
    STATE_MENU, STATE_CHARACTER_SELECT, STATE_BATTLE, 
    STATE_GAME_OVER, STATE_VICTORY
)
from game.events import register_event_handler, EVENT_CONTINUE_TO_NEXT_BATTLE
from entities.player_classes.warrior import Warrior
from entities.player_classes.archer import Archer
from entities.player_classes.mage import Mage
from combat.battle_manager import BattleManager
from combat.enemy_spawner import EnemySpawner
from ui.ui_manager import UIManager
from data.data_manager import DataManager

class GameController:
    """
    Main controller for the game, coordinates between different systems
    """
    def __init__(self, screen):
        """
        Initialize the game controller
        
        Args:
            screen (pygame.Surface): The main game screen
        """
        self.screen = screen
        self.game_state = GameState()
        self.battle_manager = BattleManager(self.game_state)
        self.enemy_spawner = EnemySpawner(self.game_state)
        self.ui_manager = UIManager(self.game_state)
        self.data_manager = DataManager()
        
        # Attach battle manager to game state for UI access
        self.game_state.battle_manager = self.battle_manager
        
        # Register event handlers
        register_event_handler(EVENT_CONTINUE_TO_NEXT_BATTLE, self._continue_to_next_battle)
    
    def update(self, delta_time):
        """
        Update the game state and all systems
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update game state first
        self.game_state.update(delta_time)
        
        # Update battle-specific systems if in battle state
        if self.game_state.current_state == STATE_BATTLE and not self.game_state.battle_paused:
            self.battle_manager.update(delta_time)
            self.enemy_spawner.update(delta_time)
        
        # Always update UI
        self.ui_manager.update(delta_time)
    
    def render(self):
        """Render the current game state"""
        # Let the UI manager handle all rendering
        self.ui_manager.render(self.screen)
    
    def handle_key_event(self, key):
        """
        Handle keyboard input
        
        Args:
            key (int): The key code from pygame.K_*
        """
        # Global controls for all states
        if key == pygame.K_s:
            self._save_game()
        elif key == pygame.K_l:
            self._load_game()
        elif key == pygame.K_SPACE:
            # Global pause/resume (works in any state)
            paused = self.game_state.toggle_battle_pause()
            print(f"Game {'paused' if paused else 'resumed'}")
        
        # State-specific controls
        if self.game_state.current_state == STATE_MENU:
            if key == pygame.K_RETURN:
                self.game_state.change_state(STATE_CHARACTER_SELECT)
        
        elif self.game_state.current_state == STATE_CHARACTER_SELECT:
            if key == pygame.K_1:
                self._select_character("warrior")
            elif key == pygame.K_2:
                self._select_character("archer")
            elif key == pygame.K_3:
                self._select_character("mage")
        
        elif self.game_state.current_state == STATE_GAME_OVER:
            if key == pygame.K_RETURN:
                self.game_state.change_state(STATE_MENU)
        
        elif self.game_state.current_state == STATE_VICTORY:
            if key == pygame.K_RETURN:
                # Manual option to continue is still available
                self._continue_to_next_battle()
    
    def _select_character(self, character_type):
        """
        Create and select a character based on type
        
        Args:
            character_type (str): Type of character to create ("warrior", "archer", "mage")
        """
        if character_type == "warrior":
            self.game_state.player_character = Warrior()
        elif character_type == "archer":
            self.game_state.player_character = Archer()
        elif character_type == "mage":
            self.game_state.player_character = Mage()
        else:
            print(f"Unknown character type: {character_type}")
            return
        
        print(f"Selected character: {character_type}")
        
        # Reset game state for a new battle
        self.game_state.enemies = []
        self.game_state.battle_timer = 0
        self.game_state.battle_round = 0
        self.game_state.battle_paused = False
        
        # Start the battle
        self.game_state.change_state(STATE_BATTLE)
        
        # Spawn initial enemies
        self.enemy_spawner.spawn_enemy()
    
    def _continue_to_next_battle(self):
        """Continue to the next battle after a victory"""
        if self.game_state.battle_paused:
            # Don't auto-continue if paused
            return
            
        # Reset battle state but keep the player character
        self.game_state.enemies = []
        self.game_state.battle_timer = 0
        self.game_state.battle_round = 0
        
        # Change to battle state
        self.game_state.change_state(STATE_BATTLE)
        
        # Spawn new enemies
        self.enemy_spawner.spawn_enemy()
        
        print("Continuing to next battle")
    
    def _save_game(self):
        """Save the current game state"""
        if self.game_state.player_character:
            self.data_manager.save_game(self.game_state)
            print("Game saved")
        else:
            print("No character to save")
    
    def _load_game(self):
        """Load a saved game"""
        result = self.data_manager.load_game()
        if result:
            # Update game state with loaded data
            self.game_state.player_character = result.get("player_character")
            self.game_state.victory_count = result.get("victory_count", 0)
            self.game_state.defeat_count = result.get("defeat_count", 0)
            
            # Start a new battle with the loaded character
            self.game_state.enemies = []
            self.game_state.battle_timer = 0
            self.game_state.battle_round = 0
            self.game_state.battle_paused = False
            self.game_state.change_state(STATE_BATTLE)
            
            # Spawn initial enemies
            self.enemy_spawner.spawn_enemy()
            
            print("Game loaded")
        else:
            print("Failed to load game")