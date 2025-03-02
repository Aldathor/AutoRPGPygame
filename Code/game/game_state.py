"""
Game state management
"""
from game.config import STATE_MENU, STATE_CHARACTER_SELECT, STATE_BATTLE, STATE_GAME_OVER, STATE_VICTORY

class GameState:
    """
    Manages the current state of the game and transitions between states.
    Implements a state machine pattern.
    """
    def __init__(self):
        """Initialize the game state"""
        self.current_state = STATE_MENU
        self.player_character = None
        self.enemies = []
        self.battle_paused = False
        self.battle_timer = 0
        self.battle_round = 0
        self.victory_count = 0
        self.defeat_count = 0
        
        # Timer for auto-continuing after victory
        self.victory_display_timer = 0
        self.victory_display_duration = 2.0  # Show victory screen for 2 seconds
        
        # State handlers - maps state names to their update/render methods
        self.state_handlers = {
            STATE_MENU: self._handle_menu_state,
            STATE_CHARACTER_SELECT: self._handle_character_select_state,
            STATE_BATTLE: self._handle_battle_state,
            STATE_GAME_OVER: self._handle_game_over_state,
            STATE_VICTORY: self._handle_victory_state
        }
        
        # State rendering handlers
        self.state_renderers = {
            STATE_MENU: self._render_menu_state,
            STATE_CHARACTER_SELECT: self._render_character_select_state,
            STATE_BATTLE: self._render_battle_state,
            STATE_GAME_OVER: self._render_game_over_state,
            STATE_VICTORY: self._render_victory_state
        }
    
    def change_state(self, new_state):
        """
        Change to a new game state
        
        Args:
            new_state (str): The state to change to
        """
        if new_state in self.state_handlers:
            self.current_state = new_state
            
            # Reset victory timer when changing to victory state
            if new_state == STATE_VICTORY:
                self.victory_display_timer = 0
                
            print(f"Game state changed to: {new_state}")
        else:
            print(f"Invalid state: {new_state}")
    
    def update(self, delta_time):
        """
        Update the current game state
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Get the handler for the current state and call it
        handler = self.state_handlers.get(self.current_state)
        if handler:
            handler(delta_time)
    
    def render(self, screen):
        """
        Render the current game state
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        # Get the renderer for the current state and call it
        renderer = self.state_renderers.get(self.current_state)
        if renderer:
            renderer(screen)
    
    def _handle_menu_state(self, delta_time):
        """Handle updates for the menu state"""
        pass  # Menu state doesn't need updates
    
    def _handle_character_select_state(self, delta_time):
        """Handle updates for the character select state"""
        pass  # Character select doesn't need time-based updates
    
    def _handle_battle_state(self, delta_time):
        """
        Handle updates for the battle state
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        if not self.battle_paused:
            self.battle_timer += delta_time
            
            # Check for battle end conditions
            if not self.player_character or self.player_character.current_hp <= 0:
                self.defeat_count += 1
                self.change_state(STATE_GAME_OVER)
            elif not self.enemies or all(enemy.current_hp <= 0 for enemy in self.enemies):
                self.victory_count += 1
                self.change_state(STATE_VICTORY)
    
    def _handle_game_over_state(self, delta_time):
        """Handle updates for the game over state"""
        pass  # Game over state doesn't need time-based updates
    
    def _handle_victory_state(self, delta_time):
        """
        Handle updates for the victory state, including auto-continuing
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update victory display timer if not paused
        if not self.battle_paused:
            self.victory_display_timer += delta_time
            
            # Auto-continue to next battle after timer expires
            if self.victory_display_timer >= self.victory_display_duration:
                # Signal the game controller to start next battle
                # This will be handled by the callback we'll set up
                from game.events import trigger_event, EVENT_CONTINUE_TO_NEXT_BATTLE
                trigger_event(EVENT_CONTINUE_TO_NEXT_BATTLE)
    
    def _render_menu_state(self, screen):
        """Render the menu state"""
        # Menu rendering will be implemented in UI manager
        pass
    
    def _render_character_select_state(self, screen):
        """Render the character select state"""
        # Character select rendering will be implemented in UI manager
        pass
    
    def _render_battle_state(self, screen):
        """Render the battle state"""
        # Battle rendering will be implemented in UI manager
        pass
    
    def _render_game_over_state(self, screen):
        """Render the game over state"""
        # Game over rendering will be implemented in UI manager
        pass
    
    def _render_victory_state(self, screen):
        """Render the victory state"""
        # Victory rendering will be implemented in UI manager
        pass
    
    def toggle_battle_pause(self):
        """Toggle the battle pause state"""
        self.battle_paused = not self.battle_paused
        return self.battle_paused