"""
Main game controller with party system support
"""
import pygame
import random
from game.game_state import GameState
from game.config import (
    STATE_MENU, STATE_CHARACTER_SELECT, STATE_PARTY_SELECT, STATE_BATTLE, 
    STATE_GAME_OVER, STATE_VICTORY, MAX_PARTY_SIZE
)
from game.events import (
    register_event_handler, EVENT_CONTINUE_TO_NEXT_BATTLE,
    EVENT_COMBAT_ATTACK_START, EVENT_COMBAT_ATTACK_HIT,
    EVENT_COMBAT_ENTITY_DEFEATED, EVENT_TARGET_SELECTION_START
)
from entities.player_classes.warrior import Warrior
from entities.player_classes.archer import Archer
from entities.player_classes.mage import Mage
from combat.realtime_battle_manager import RealtimeBattleManager
from combat.combat_state import CombatState, CombatEventQueue
from combat.enemy_spawner import EnemySpawner
from ui.ui_manager import UIManager
from data.data_manager import DataManager
from ui.character_creation_dialog import CharacterCreationDialog
from ui.animation_helper import AnimationHelper

class GameController:
    """
    Main controller for the game, coordinates between different systems
    """
    def __init__(self, screen):
        """
        Initialize the game controller with real-time battle support
        
        Args:
            screen (pygame.Surface): The main game screen
        """
        # Initialize debug flag first
        self.debug = True
        
        self.screen = screen
        self.game_state = GameState()
        
        # Use RealtimeBattleManager instead of BattleManager
        self.battle_manager = RealtimeBattleManager(self.game_state)
        
        self.enemy_spawner = EnemySpawner(self.game_state)
        self.ui_manager = UIManager(self.game_state)
        self.data_manager = DataManager()
        from ui.animation_helper import AnimationHelper
        self.animation_helper = AnimationHelper(screen.get_width(), screen.get_height())
        self.game_state.animation_helper = self.animation_helper

        # Character creation UI
        self.character_creation_dialog = CharacterCreationDialog()
        self.character_creation_dialog.callback = self._on_character_created
        
        # Character name input
        self.character_name = ""
        self.typing_character_name = False
        self.current_character_class = None
        
        # Target selection state
        self.selecting_target = False
        self.available_targets = []
        
        # Combat and rest counter
        self.combat_encounter_count = 0
        self.rests_taken = 0

        # Add this to the game state so UI can access it
        self.game_state.rests_taken = 0

        # Attach battle manager to game state for UI access
        self.game_state.battle_manager = self.battle_manager
        
        # Load character roster on startup
        self._load_character_roster()
        
        # Register event handlers
        register_event_handler(EVENT_CONTINUE_TO_NEXT_BATTLE, self._continue_to_next_battle)
        register_event_handler(EVENT_COMBAT_ENTITY_DEFEATED, self._on_entity_defeated)
        register_event_handler(EVENT_COMBAT_ATTACK_HIT, self._on_attack_hit)
        register_event_handler(EVENT_TARGET_SELECTION_START, self._on_target_selection_start)
        
        # Debug flag
        self.debug = True
    
    def update(self, delta_time):
        """
        Update the game state and all systems with real-time combat support
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update game state first
        self.game_state.update(delta_time)
        
        # Update battle-specific systems if in battle state
        if self.game_state.current_state == STATE_BATTLE and not self.game_state.battle_paused:
            # Update real-time battle manager
            self.battle_manager.update(delta_time)
            
            # Update enemy spawner
            self.enemy_spawner.update(delta_time)
            
            # Update animation helper
            self.animation_helper.update(delta_time)
            
            # Update character positions and states
            self._update_combat_entities(delta_time)

        # Always update UI
        self.ui_manager.update(delta_time)
        
        # Update character creation dialog if active
        if self.character_creation_dialog.active:
            self.character_creation_dialog.update(delta_time)
    
    def _update_combat_entities(self, delta_time):
        """
        Update all combat entities (characters and enemies) for real-time combat
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update party members
        for character in self.game_state.party:
            if character and character.is_alive():
                character.update(delta_time)
        
        # Update enemies
        for enemy in self.game_state.enemies:
            if enemy.is_alive():
                enemy.update(delta_time)

    def render(self):
        """Render the current game state"""
        # Let the UI manager handle all rendering
        self.ui_manager.render(self.screen)
        
        # If typing character name, render input box
        if self.typing_character_name:
            self._render_name_input()
        
        # If character creation dialog is active, render it
        if self.character_creation_dialog.active:
            self.character_creation_dialog.render(self.screen)
    
    def handle_key_event(self, key):
        """
        Handle keyboard input
        
        Args:
            key (int): The key code from pygame.K_*
            
        Returns:
            bool: True if the key was handled, False otherwise
        """
        # Handle character name input if active
        if self.typing_character_name:
            if key == pygame.K_RETURN:
                self._create_character()
                self.typing_character_name = False
                return True
            elif key == pygame.K_ESCAPE:
                self.typing_character_name = False
                self.character_name = ""
                return True
            elif key == pygame.K_BACKSPACE:
                self.character_name = self.character_name[:-1]
                return True
            # Don't process other inputs while typing
            return True
        
        # Handle character creation dialog if active
        if self.character_creation_dialog.active:
            handled = self.character_creation_dialog.handle_key_event(key)
            return handled
        
        # Global controls for all states
        if key == pygame.K_s and self.game_state.current_state in [STATE_BATTLE, STATE_VICTORY]:
            self._save_game()
            return True
        elif key == pygame.K_l and self.game_state.current_state == STATE_MENU:
            self._load_game()
            return True
        elif key == pygame.K_SPACE and self.game_state.current_state in [STATE_BATTLE, STATE_VICTORY]:
            # Global pause/resume (works in battle and victory states)
            paused = self.game_state.toggle_battle_pause()
            if paused:
                self.animation_helper.pause_animations()
            else:
                self.animation_helper.resume_animations()
            print(f"Game {'paused' if paused else 'resumed'}")
            return True
        
        # State-specific controls
        if self.game_state.current_state == STATE_MENU:
            if key == pygame.K_n:
                # Go to character selection (for new game)
                self.game_state.change_state(STATE_CHARACTER_SELECT)
                return True
            elif key == pygame.K_c:
                # Go to party selection (character management)
                self.game_state.change_state(STATE_PARTY_SELECT)
                return True
        
        elif self.game_state.current_state == STATE_CHARACTER_SELECT:
            if key == pygame.K_1:
                self._select_character_class("warrior")
                return True
            elif key == pygame.K_2:
                self._select_character_class("archer")
                return True
            elif key == pygame.K_3:
                self._select_character_class("mage")
                return True
            elif key == pygame.K_ESCAPE:
                self.game_state.change_state(STATE_MENU)
                return True
        
        elif self.game_state.current_state == STATE_PARTY_SELECT:
            if key == pygame.K_ESCAPE:
                self.game_state.change_state(STATE_MENU)
                return True
            elif key == pygame.K_c:
                # Start character creation
                self._start_character_creation()
                return True
            elif key == pygame.K_b:
                # Start battle if party has at least one character
                if any(self.game_state.party):
                    self._start_battle()
                    return True
            elif key >= pygame.K_1 and key <= pygame.K_9:
                # Select roster slot or party slot
                index = key - pygame.K_1
                if index < len(self.game_state.character_roster):
                    self._select_roster_character(index)
                    return True
            elif key == pygame.K_UP:
                # Scroll roster up
                if hasattr(self.ui_manager, 'party_selection_ui'):
                    self.ui_manager.party_selection_ui.roster_scroll_offset = max(
                        0, self.ui_manager.party_selection_ui.roster_scroll_offset - 1
                    )
                    return True
            elif key == pygame.K_DOWN:
                # Scroll roster down
                if hasattr(self.ui_manager, 'party_selection_ui'):
                    max_offset = max(0, len(self.game_state.character_roster) - 
                                  self.ui_manager.party_selection_ui.max_visible_roster)
                    self.ui_manager.party_selection_ui.roster_scroll_offset = min(
                        max_offset, self.ui_manager.party_selection_ui.roster_scroll_offset + 1
                    )
                    return True
        
        elif self.game_state.current_state == STATE_BATTLE:
            if self.selecting_target:
                # Target selection mode
                if key >= pygame.K_1 and key <= pygame.K_9:
                    target_index = key - pygame.K_1
                    if target_index < len(self.available_targets):
                        self._select_target(self.available_targets[target_index])
                        self.selecting_target = False
                        return True
                elif key == pygame.K_ESCAPE:
                    # Cancel target selection
                    self.selecting_target = False
                    return True
            else:
                # Regular battle controls
                if key == pygame.K_TAB:
                    # Cycle through active party members
                    self.game_state.select_next_active_character()
                    return True
                elif key >= pygame.K_1 and key <= pygame.K_3:
                    # Select party member
                    member_index = key - pygame.K_1
                    if member_index < MAX_PARTY_SIZE and self.game_state.party[member_index]:
                        self.game_state.active_character_index = member_index
                        return True
                elif key == pygame.K_a:
                    # Manual attack command
                    active_char_idx = self.game_state.active_character_index
                    if (0 <= active_char_idx < len(self.game_state.party) and 
                        self.game_state.party[active_char_idx] and 
                        self.game_state.party[active_char_idx].is_alive() and
                        self.game_state.party[active_char_idx].can_attack()):
                        # Start target selection
                        self._start_target_selection()
                        return True
        
        elif self.game_state.current_state == STATE_GAME_OVER:
            if key == pygame.K_RETURN:
                self.game_state.change_state(STATE_MENU)
                return True
        
        elif self.game_state.current_state == STATE_VICTORY:
            if key == pygame.K_RETURN:
                # Manual option to continue is still available
                self._continue_to_next_battle()
                return True
        
        # Key was not handled
        return False
    
    def handle_text_input(self, text):
        """
        Handle text input (for character name)
        
        Args:
            text (str): The text input
        """
        if self.typing_character_name:
            # Limit name length
            if len(self.character_name) < 20:
                self.character_name += text
                if self.debug:
                    print(f"Character name input: {self.character_name}")
        
        # Forward to character creation dialog if active
        if self.character_creation_dialog.active:
            self.character_creation_dialog.handle_text_input(text)
    
    def handle_mouse_event(self, event):
        """
        Handle mouse input
        
        Args:
            event (pygame.event.Event): The mouse event
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        # Handle character creation dialog if active
        if self.character_creation_dialog.active:
            handled = self.character_creation_dialog.handle_mouse_event(event)
            if handled:
                return True
        
        # Handle mouse events based on current state
        if self.game_state.current_state == STATE_PARTY_SELECT:
            # Handle party selection UI mouse events
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                handled = self._handle_party_select_mouse(mouse_pos)
                if handled:
                    return True
                
        elif self.game_state.current_state == STATE_BATTLE:
            # Handle battle UI mouse events
            if event.type == pygame.MOUSEBUTTONDOWN and self.selecting_target:
                mouse_pos = pygame.mouse.get_pos()
                handled = self._handle_battle_target_selection(mouse_pos)
                if handled:
                    return True
        
        # Event was not handled
        return False
    
    def _handle_party_select_mouse(self, mouse_pos):
        """
        Handle mouse clicks in party selection screen
        
        Args:
            mouse_pos (tuple): Mouse x,y position
            
        Returns:
            bool: True if handled, False otherwise
        """
        # Get screen dimensions
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Party section
        party_section_width = screen_width // 2
        party_section_height = 200
        party_section_x = (screen_width - party_section_width) // 2
        party_section_y = 100
        
        # Party slots
        slot_width = 150
        slot_height = 120
        slots_x = party_section_x + (party_section_width - (slot_width * MAX_PARTY_SIZE) - 
                                (10 * (MAX_PARTY_SIZE - 1))) // 2
        slots_y = party_section_y + 50
        
        # Character roster section
        roster_section_width = screen_width * 3 // 4
        roster_section_height = 350
        roster_section_x = (screen_width - roster_section_width) // 2
        roster_section_y = party_section_y + party_section_height + 30
        
        # Create New Character button
        create_btn_width = 200
        create_btn_height = 30
        create_btn_x = roster_section_x + 20
        create_btn_y = roster_section_y + roster_section_height - 40
        create_btn_rect = pygame.Rect(create_btn_x, create_btn_y, create_btn_width, create_btn_height)
        
        # Start Battle button
        start_btn_width = 200
        start_btn_height = 30
        start_btn_x = roster_section_x + roster_section_width - start_btn_width - 20
        start_btn_y = roster_section_y + roster_section_height - 40
        start_btn_rect = pygame.Rect(start_btn_x, start_btn_y, start_btn_width, start_btn_height)
        
        # Debug button locations
        if pygame.key.get_pressed()[pygame.K_F3] and self.debug:  # F3 key for debug
            print(f"Mouse position: {mouse_pos}")
            print(f"Create button: {create_btn_rect}")
            print(f"Start button: {start_btn_rect}")
        
        # Check if "Create New Character" button was clicked
        if create_btn_rect.collidepoint(mouse_pos):
            if self.debug:
                print("Create New Character button clicked")
            self._start_character_creation()
            return True
        
        # Check if "Start Battle" button was clicked (if party has at least one character)
        if any(self.game_state.party) and start_btn_rect.collidepoint(mouse_pos):
            if self.debug:
                print("Start Battle button clicked")
            self._start_battle()
            return True
        
        # Check for party slot clicks
        for i in range(MAX_PARTY_SIZE):
            slot_x = slots_x + i * (slot_width + 10)
            slot_rect = pygame.Rect(slot_x, slots_y, slot_width, slot_height)
            
            if slot_rect.collidepoint(mouse_pos):
                # Handle party slot click
                if i < len(self.game_state.party):
                    # Toggle character in/out of this slot
                    if self.game_state.party[i]:
                        removed_char = self.game_state.remove_character_from_party(i)
                        if self.debug:
                            print(f"Removed {removed_char.name if removed_char else 'character'} from party slot {i+1}")
                        return True
        
        # Check roster item clicks
        item_height = 40
        visible_area_height = roster_section_height - 50  # Accounting for title/padding
        max_visible_items = min(
            8,  # Maximum number of roster entries visible at once
            visible_area_height // item_height
        )
        
        list_width = roster_section_width - 40  # Padding on both sides
        list_start_x = roster_section_x + 20
        list_start_y = roster_section_y + 50
        
        # Get roster offset from UI if available
        roster_offset = 0
        if hasattr(self.ui_manager, 'party_selection_ui'):
            roster_offset = getattr(self.ui_manager.party_selection_ui, 'roster_scroll_offset', 0)
        
        # Check visible roster items
        for i in range(max_visible_items):
            roster_idx = i + roster_offset
            if roster_idx < len(self.game_state.character_roster):
                # Item area
                item_rect = pygame.Rect(
                    list_start_x, 
                    list_start_y + i * item_height, 
                    list_width, 
                    item_height - 5
                )
                
                if item_rect.collidepoint(mouse_pos):
                    if self.debug:
                        print(f"Clicked character roster item {roster_idx+1}")
                    self._select_roster_character(roster_idx)
                    return True
                
                # Add to party button
                character = self.game_state.character_roster[roster_idx]
                if not any(char is character for char in self.game_state.party if char):
                    add_btn_width = 90
                    add_btn_height = item_height - 15
                    add_btn_x = item_rect.right - add_btn_width - 10
                    add_btn_y = item_rect.top + 5
                    add_btn_rect = pygame.Rect(add_btn_x, add_btn_y, add_btn_width, add_btn_height)
                    
                    if add_btn_rect.collidepoint(mouse_pos):
                        if self.debug:
                            print(f"Clicked Add button for roster item {roster_idx+1}")
                        self._select_roster_character(roster_idx)
                        return True
        
        # Check for scroll up/down areas
        scroll_up_rect = pygame.Rect(
            roster_section_x, 
            roster_section_y + 35, 
            roster_section_width, 
            15
        )
        
        scroll_down_rect = pygame.Rect(
            roster_section_x, 
            roster_section_y + roster_section_height - 45, 
            roster_section_width, 
            15
        )
        
        if scroll_up_rect.collidepoint(mouse_pos) and hasattr(self.ui_manager, 'party_selection_ui'):
            # Scroll up
            self.ui_manager.party_selection_ui.roster_scroll_offset = max(
                0, self.ui_manager.party_selection_ui.roster_scroll_offset - 1
            )
            return True
            
        if scroll_down_rect.collidepoint(mouse_pos) and hasattr(self.ui_manager, 'party_selection_ui'):
            # Scroll down
            max_offset = max(0, len(self.game_state.character_roster) - max_visible_items)
            self.ui_manager.party_selection_ui.roster_scroll_offset = min(
                max_offset, self.ui_manager.party_selection_ui.roster_scroll_offset + 1
            )
            return True
        
        return False
    
    def _handle_battle_target_selection(self, mouse_pos):
        """
        Handle mouse clicks for target selection in battle
        
        Args:
            mouse_pos (tuple): Mouse x,y position
            
        Returns:
            bool: True if handled, False otherwise
        """
        # Check if we clicked on an enemy
        for i, enemy in enumerate(self.available_targets):
            if enemy.is_alive():
                # Get enemy position (this is simplified - you'd need to match your rendering logic)
                enemy_x = (self.screen.get_width() * 3) // 4
                enemy_y = self.screen.get_height() // 2
                enemy_spacing = 80
                
                if len(self.available_targets) <= 3:
                    offset_x = (i - (len(self.available_targets) - 1) / 2) * enemy_spacing
                    enemy_pos_x = enemy_x + offset_x
                    enemy_pos_y = enemy_y
                else:
                    # Grid layout for more than 3 enemies
                    col = i % 2
                    row = i // 2
                    enemy_pos_x = enemy_x + (col - 0.5) * enemy_spacing
                    enemy_pos_y = enemy_y + (row - len(self.available_targets) // 4) * enemy_spacing
                
                # Simple hit testing with a rectangle around the enemy
                enemy_rect = pygame.Rect(
                    enemy_pos_x - enemy.sprite.get_width() // 2 - 5,
                    enemy_pos_y - enemy.sprite.get_height() // 2 - 5,
                    enemy.sprite.get_width() + 10,
                    enemy.sprite.get_height() + 10
                )
                
                if enemy_rect.collidepoint(mouse_pos):
                    self._select_target(enemy)
                    return True
        
        return False
    
    def _select_character_class(self, character_type):
        """
        Select a character class and prompt for name
        
        Args:
            character_type (str): Type of character ("warrior", "archer", "mage")
        """
        self.current_character_class = character_type
        self.typing_character_name = True
        self.character_name = ""
        
        if self.debug:
            print(f"Selected character class: {character_type}, enter name...")
    
    def _start_character_creation(self):
        """Start the character creation process"""
        self.character_creation_dialog.show(self._on_character_created)
        if self.debug:
            print("Starting character creation dialog")
    
    def _on_character_created(self, result):
        """
        Handle character creation result
        
        Args:
            result (dict): Character creation result with name and class
        """
        if not result:
            if self.debug:
                print("Character creation cancelled")
            return
            
        name = result.get("name")
        character_class = result.get("class")
        
        if not name or not character_class:
            if self.debug:
                print("Invalid character creation result")
            return
            
        # Create character based on class
        if character_class == "warrior":
            character = Warrior(name)
        elif character_class == "archer":
            character = Archer(name)
        elif character_class == "mage":
            character = Mage(name)
        else:
            print(f"Unknown character type: {character_class}")
            return
        
        # Add to roster
        self.game_state.add_character_to_roster(character)
        
        # Save the character roster
        self.data_manager.save_character_roster(self.game_state.character_roster)
        
        if self.debug:
            print(f"Created character: {name} ({character_class})")
    
    def _create_character(self):
        """Create a new character with the entered name and selected class"""
        if not self.character_name or not self.current_character_class:
            return
            
        # Create character based on class
        if self.current_character_class == "warrior":
            character = Warrior(self.character_name)
        elif self.current_character_class == "archer":
            character = Archer(self.character_name)
        elif self.current_character_class == "mage":
            character = Mage(self.character_name)
        else:
            print(f"Unknown character type: {self.current_character_class}")
            return
        
        # Add to roster
        self.game_state.add_character_to_roster(character)
        
        # Save the character roster
        self.data_manager.save_character_roster(self.game_state.character_roster)
        
        if self.debug:
            print(f"Created character: {self.character_name} ({self.current_character_class})")
        
        # Clear creation state
        self.current_character_class = None
        self.character_name = ""
        
        # Go to party selection screen
        self.game_state.change_state(STATE_PARTY_SELECT)
    
    def _select_roster_character(self, index):
        """
        Select a character from the roster to add to party
        
        Args:
            index (int): Character index in roster
        """
        if 0 <= index < len(self.game_state.character_roster):
            character = self.game_state.character_roster[index]
            
            # Check if character is already in party
            if character in self.game_state.party:
                print(f"{character.name} is already in the party")
                return
                
            # Add to first available party slot
            for i in range(MAX_PARTY_SIZE):
                if self.game_state.party[i] is None:
                    self.game_state.party[i] = character
                    print(f"Added {character.name} to party slot {i}")
                    return
                    
            print("Party is full")
    
    def _start_battle(self):
        """Start a battle with the current party using real-time battle system"""
        # Ensure we have at least one character
        if not any(self.game_state.party):
            print("Need at least one character in party to start battle")
            return
            
        # Reset game state for a new battle
        self.game_state.enemies = []
        self.game_state.battle_timer = 0
        self.game_state.battle_round = 0
        self.game_state.battle_paused = False
        
        # Reset enemy spawner
        self.enemy_spawner.reset_for_new_battle()
        
        # Set active character to first living character
        for i, char in enumerate(self.game_state.party):
            if char and char.is_alive():
                self.game_state.active_character_index = i
                break
        
        # Start the battle
        self.game_state.change_state(STATE_BATTLE)
        
        # Initialize combat positions
        self._initialize_combat_positions()
        
        # Spawn initial enemies
        num_enemies = self._determine_enemy_count()
        self.enemy_spawner.spawn_enemy_group(num_enemies)
        
        # Start the real-time battle manager
        self.battle_manager.start_battle()
        
        if self.debug:
            print(f"Started real-time battle with {num_enemies} enemies")

    def _initialize_combat_positions(self):
        """
        Initialize positions for all entities in combat
        """
        # Position party members on the left side
        party_center_x = self.screen.get_width() // 4
        party_center_y = self.screen.get_height() // 2
        character_spacing = 150
        
        for i, character in enumerate(self.game_state.party):
            if character:
                # Calculate vertical position
                char_y = party_center_y + (i - 1) * character_spacing
                
                # Set position (ensure character has a position attribute)
                character.position = pygame.Vector2(party_center_x, char_y)
        
        # Enemy positions will be set by the enemy spawner

    def _determine_enemy_count(self):
        """
        Determine how many enemies to spawn based on party size and strength
        
        Returns:
            int: Number of enemies to spawn
        """
        # Count living party members
        living_party_members = sum(1 for char in self.game_state.party if char and char.is_alive())
        
        # Base enemy count on party size
        if living_party_members == 1:
            # 1-2 enemies for a single character
            return random.randint(1, 2)
        elif living_party_members == 2:
            # 2-3 enemies for two characters
            return random.randint(2, 3)
        else:
            # Max enemies for three characters
            return 3
    
    def _start_target_selection(self):
        """Start the target selection process using real-time battle manager"""
        # Get active character
        active_char_idx = self.game_state.active_character_index
        if not (0 <= active_char_idx < len(self.game_state.party) and 
                self.game_state.party[active_char_idx] and 
                self.game_state.party[active_char_idx].is_alive()):
            return
        
        # Use the real-time battle manager to initiate target selection
        character = self.game_state.party[active_char_idx]
        target_selection_initiated = self.battle_manager.initiate_target_selection(character)
        
        if target_selection_initiated:
            self.selecting_target = True
            self.available_targets = self.game_state.potential_targets
            
            if self.debug:
                print(f"Started real-time target selection with {len(self.available_targets)} enemies")
    
    def _select_target(self, target):
        """
        Select a target for the active character to attack using real-time battle system
        
        Args:
            target (BaseCharacter): The selected target
        """
        if not self.selecting_target:
            return
        
        # Use the real-time battle manager to select target
        target_index = self.available_targets.index(target) if target in self.available_targets else -1
        
        if target_index >= 0:
            self.battle_manager.select_target(target_index)
            
            # Reset target selection state (battle manager also handles this)
            self.selecting_target = False
            self.available_targets = []
            
            if self.debug:
                print(f"Selected target: {target.name}")
    
    def _on_entity_defeated(self, entity, defeater=None):
        """
        Handle entity defeated event
        
        Args:
            entity (BaseCharacter): The defeated entity
            defeater (BaseCharacter, optional): The entity that defeated it
        """
        if entity in self.game_state.enemies:
            if self.debug:
                print(f"Enemy defeated: {entity.name}")

    def _on_attack_hit(self, attacker, target, result):
        """
        Handle attack hit event
        
        Args:
            attacker (BaseCharacter): The attacking entity
            target (BaseCharacter): The target entity
            result (dict): Attack result data
        """
        # Could add special effects or other logic here
        pass

    def _on_target_selection_start(self, character):
        """
        Handle target selection start event
        
        Args:
            character (BaseCharacter): The character selecting a target
        """
        # Update UI state or other game elements here
        pass    

    def _take_rest(self):
        """
        Take a rest to restore party's health and revive fallen characters
        """
        # Create fire pit animation
        from ui.rest_animation import FirePitAnimation
        fire_pit = FirePitAnimation(self.screen.get_width(), self.screen.get_height())
        
        # Set up animation variables
        animation_duration = 5.0  # seconds
        animation_timer = 0
        clock = pygame.time.Clock()
        
        # Show animation
        while animation_timer < animation_duration:
            delta_time = clock.tick(60) / 1000.0  # delta time in seconds
            animation_timer += delta_time
            
            # Update animation
            fire_pit.update(delta_time)
            
            # Render animation
            self.screen.fill((0, 0, 0))  # Clear screen
            fire_pit.render(self.screen)
            
            # Render rest information
            font = pygame.font.SysFont("Arial", 24)
            rest_text = font.render(f"Resting by the campfire... ({self.rests_taken + 1})", True, (255, 255, 255))
            rest_rect = rest_text.get_rect(center=(self.screen.get_width() // 2, 50))
            self.screen.blit(rest_text, rest_rect)
            
            # Render party recovery info
            y_offset = 100
            for character in self.game_state.party:
                if character:
                    # Gradual healing animation
                    heal_percentage = min(1.0, animation_timer / animation_duration)
                    if not character.is_alive():
                        status = "Reviving..."
                        new_hp = int(character.max_hp * heal_percentage)
                    else:
                        old_hp = character.current_hp
                        new_hp = old_hp + int((character.max_hp - old_hp) * heal_percentage)
                        status = "Recovering..."
                    
                    # Update character HP for animation effect
                    character.current_hp = new_hp
                    if heal_percentage > 0.5:  # Halfway through, revive any dead characters
                        character.alive = True
                    
                    char_text = font.render(f"{character.name}: {status} ({character.current_hp}/{character.max_hp} HP)", True, (255, 255, 255))
                    char_rect = char_text.get_rect(center=(self.screen.get_width() // 2, y_offset))
                    self.screen.blit(char_text, char_rect)
                    y_offset += 30
            
            # Render a progress bar
            bar_width = 400
            bar_height = 20
            bar_x = (self.screen.get_width() - bar_width) // 2
            bar_y = self.screen.get_height() - 100
            
            # Background
            pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            # Progress
            progress_width = int(bar_width * (animation_timer / animation_duration))
            pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, progress_width, bar_height))
            # Border
            pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Render continue message
            if animation_timer > animation_duration * 0.8:  # Near the end
                continue_text = font.render("Press any key to continue...", True, (255, 255, 255))
                continue_rect = continue_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 50))
                self.screen.blit(continue_text, continue_rect)
            
            pygame.display.flip()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN and animation_timer > animation_duration * 0.8:
                    # Allow skipping near the end
                    animation_timer = animation_duration
                elif event.type == pygame.MOUSEBUTTONDOWN and animation_timer > animation_duration * 0.8:
                    # Allow skipping near the end
                    animation_timer = animation_duration
        
        # Heal all party members to full and revive fallen characters
        for character in self.game_state.party:
            if character:
                old_hp = character.current_hp
                character.current_hp = character.max_hp
                character.alive = True  # Revive
                heal_amount = character.current_hp - old_hp
                
                if self.debug and heal_amount > 0:
                    print(f"{character.name} rested and recovered {heal_amount} HP")
        
        self.rests_taken += 1
        self.game_state.rests_taken = self.rests_taken  # Update in game state for UI
        
        if self.debug:
            print(f"Party has taken a rest ({self.rests_taken} rests so far)")
        
        # Add a message to the combat log
        if hasattr(self.battle_manager, 'combat_log'):
            self.battle_manager._log_message("The party takes a rest and recovers full health!")
            self.battle_manager._log_message("All fallen characters have been revived!")
            
        # Continue to next battle after the rest
        # Reset battle state but keep the party
        self.game_state.enemies = []
        self.game_state.battle_timer = 0
        self.game_state.battle_round = 0
        
        # Ensure active character is a living one
        self._select_next_living_character()
        
        # Reset enemy spawner
        self.enemy_spawner.reset_for_new_battle()
        
        # Change to battle state
        self.game_state.change_state(STATE_BATTLE)
        
        # Spawn new enemies
        num_enemies = self._determine_enemy_count()
        self.enemy_spawner.spawn_enemy_group(num_enemies)
        
        if self.debug:
            print(f"Starting new battle after rest with {num_enemies} enemies")

    def _continue_to_next_battle(self):
        """Continue to the next battle after a victory"""
        if self.game_state.battle_paused:
            # Don't auto-continue if paused
            return
        
        # Increment combat encounter counter
        self.combat_encounter_count += 1
        
        # Check if it's time for a rest
        if self.combat_encounter_count >= 3:
            self._take_rest()
            self.combat_encounter_count = 0  # Reset counter
            return
        
        # Reset battle state but keep the party
        self.game_state.enemies = []
        self.game_state.battle_timer = 0
        self.game_state.battle_round = 0
        
        # Ensure active character is a living one
        self._select_next_living_character()
        
        # Reset enemy spawner
        self.enemy_spawner.reset_for_new_battle()
        
        # Change to battle state
        self.game_state.change_state(STATE_BATTLE)
        
        # Spawn new enemies
        num_enemies = self._determine_enemy_count()
        self.enemy_spawner.spawn_enemy_group(num_enemies)
        
        if self.debug:
            print(f"Continuing to next battle ({self.combat_encounter_count}/3 until rest) with {num_enemies} enemies")
    
    def _select_next_living_character(self):
        """Select the next living character as active"""
        for i, char in enumerate(self.game_state.party):
            if char and char.is_alive():
                self.game_state.active_character_index = i
                return
    
    def _save_game(self):
        """Save the current game state"""
        if any(self.game_state.party):
            success = self.data_manager.save_game(self.game_state)
            print(f"Game {'saved successfully' if success else 'save failed'}")
        else:
            print("No characters to save")
        
        # Also save the character roster
        success = self.data_manager.save_character_roster(self.game_state.character_roster)
        if self.debug:
            print(f"Character roster {'saved successfully' if success else 'save failed'}")
    
    def _load_game(self):
        """Load a saved game"""
        result = self.data_manager.load_game()
        if result:
            # Update game state with loaded data
            self.game_state.party = result.get("party", [None, None, None])
            self.game_state.victory_count = result.get("victory_count", 0)
            self.game_state.defeat_count = result.get("defeat_count", 0)
            
            # Select first living character
            self._select_next_living_character()
            
            # Start a new battle with the loaded party
            self.game_state.enemies = []
            self.game_state.battle_timer = 0
            self.game_state.battle_round = 0
            self.game_state.battle_paused = False
            self.game_state.change_state(STATE_BATTLE)
            
            # Spawn initial enemies
            num_enemies = self._determine_enemy_count()
            for _ in range(num_enemies):
                self.enemy_spawner.spawn_enemy()
            
            if self.debug:
                print(f"Game loaded successfully with {len([c for c in self.game_state.party if c])} characters")
        else:
            print("Failed to load game")
    
    def _load_character_roster(self):
        """Load the character roster"""
        roster = self.data_manager.load_character_roster()
        self.game_state.character_roster = roster
        if self.debug:
            print(f"Loaded {len(roster)} characters into roster")
    
    def _render_name_input(self):
        """Render the character name input box"""
        # Create an overlay with transparency
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Input box
        box_width = 400
        box_height = 150
        box_x = (self.screen.get_width() - box_width) // 2
        box_y = (self.screen.get_height() - box_height) // 2
        
        # Draw input box
        pygame.draw.rect(self.screen, (50, 50, 70), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, (200, 200, 200), (box_x, box_y, box_width, box_height), 2)
        
        # Title
        font = pygame.font.SysFont("Arial", 24)
        title_text = font.render("Enter Character Name", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(box_x + box_width // 2, box_y + 30))
        self.screen.blit(title_text, title_rect)
        
        # Input field
        input_box_width = 350
        input_box_height = 40
        input_box_x = box_x + (box_width - input_box_width) // 2
        input_box_y = box_y + 60
        
        pygame.draw.rect(self.screen, (30, 30, 40), (input_box_x, input_box_y, input_box_width, input_box_height))
        pygame.draw.rect(self.screen, (150, 150, 150), (input_box_x, input_box_y, input_box_width, input_box_height), 1)
        
        # Render current name with blinking cursor
        cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 0
        display_text = self.character_name + ("|" if cursor_visible else "")
        
        text_surface = font.render(display_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(midleft=(input_box_x + 10, input_box_y + input_box_height // 2))
        
        # Limit text rendering to input box width
        self.screen.blit(text_surface, text_rect, 
                      (0, 0, min(input_box_width - 20, text_surface.get_width()), text_surface.get_height()))
        
        # Instructions
        instructions = font.render("Press ENTER to confirm, ESC to cancel", True, (200, 200, 200))
        instructions_rect = instructions.get_rect(center=(box_x + box_width // 2, box_y + 120))
        self.screen.blit(instructions, instructions_rect)