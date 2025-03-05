"""
Real-time Battle Manager - Handles real-time combat flow and character interactions
"""
import time
import pygame
from combat.movement_controller import MovementController
from combat.movement_controller import MovementController
from combat.tactical_ai import TacticalAI
from combat.formation_system import FormationSystem, FormationType
from combat.cover_system import CoverSystem, CoverType
from combat.area_effect_system import AoEManager
from combat.tactical_ui import TacticalUIController
from combat.combat_modifiers import ModifierManager
from combat.combat_state import CombatState
from game.events import (
    trigger_event, EVENT_COMBAT_MOVE_START, EVENT_COMBAT_MOVE_END,
    EVENT_COMBAT_STATE_CHANGE
)

from combat.combat_calculator import CombatCalculator

class BattleSystemsIntegration:
    """
    Integration class for all spatial combat systems in RealtimeBattleManager
    """
    
    def init_systems(battle_manager, screen_width, screen_height):
        """
        Initialize all spatial combat systems
        
        Args:
            battle_manager: The battle manager instance
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        # Set screen dimensions
        battle_manager.screen_width = screen_width
        battle_manager.screen_height = screen_height
        
        # Initialize systems in order of dependency
        # 1. Movement controller and combat grid
        from combat.movement_controller import MovementController
        battle_manager.movement_controller = MovementController(screen_width, screen_height)
        
        # 2. Modifier manager (before tactical systems that use modifiers)
        from combat.combat_modifiers import ModifierManager
        battle_manager.modifier_manager = ModifierManager()
        
        # 3. Tactical AI
        from combat.tactical_ai import TacticalAI
        battle_manager.tactical_ai = TacticalAI(battle_manager)
        
        # 4. Formation system
        from combat.formation_system import FormationSystem, FormationType
        battle_manager.formation_system = FormationSystem(battle_manager)
        
        # 5. Cover system
        from combat.cover_system import CoverSystem
        battle_manager.cover_system = CoverSystem(battle_manager)
        battle_manager.cover_system.generate_random_cover(5)  # Add some random cover
        
        # 6. Area effect system
        from combat.area_effect_system import AoEManager
        battle_manager.aoe_manager = AoEManager(battle_manager)
        
        # 7. Tactical UI controller (depends on all other systems)
        from combat.tactical_ui import TacticalUIController
        battle_manager.tactical_ui = TacticalUIController(battle_manager)
        
        # Initialize positions after all systems are ready
        battle_manager._initialize_spatial_combat()
        
        # Log initialization
        if hasattr(battle_manager, '_log_message'):
            battle_manager._log_message("Tactical combat systems initialized")
    
    def _initialize_spatial_combat(battle_manager):
        """Initialize spatial positioning for all entities"""
        # Register entities with movement controller
        if not hasattr(battle_manager, 'movement_controller'):
            return
            
        # Position party members on the left side
        party_center_x = battle_manager.screen_width // 4
        party_center_y = battle_manager.screen_height // 2
        
        # Set initial formation center
        if hasattr(battle_manager, 'formation_system'):
            battle_manager.formation_system.formation_center = pygame.Vector2(party_center_x, party_center_y)
            
            # Apply initial formation
            from combat.formation_system import FormationType
            battle_manager.formation_system.apply_formation(FormationType.TRIANGLE)
        else:
            # Fallback if no formation system
            character_spacing = 150
            
            for i, character in enumerate(battle_manager.game_state.party):
                if character and character.is_alive():
                    # Calculate vertical position
                    char_y = party_center_y + (i - 1) * character_spacing
                    
                    # Register with movement controller
                    battle_manager.movement_controller.register_entity(character, 
                                                                    (party_center_x, char_y))
        
        # Position enemies on the right side
        enemy_center_x = (battle_manager.screen_width * 3) // 4
        enemy_center_y = battle_manager.screen_height // 2
        enemy_spacing = 120
        
        for i, enemy in enumerate(battle_manager.game_state.enemies):
            if enemy.is_alive():
                # Calculate position based on number of enemies
                if len(battle_manager.game_state.enemies) <= 3:
                    enemy_y = enemy_center_y + (i - (len(battle_manager.game_state.enemies) - 1) / 2) * enemy_spacing
                    enemy_x = enemy_center_x
                else:
                    # Grid layout for more than 3 enemies
                    col = i % 2
                    row = i // 2
                    enemy_x = enemy_center_x + (col - 0.5) * enemy_spacing
                    enemy_y = enemy_center_y + (row - len(battle_manager.game_state.enemies) // 4) * enemy_spacing
                
                # Register with movement controller
                battle_manager.movement_controller.register_entity(enemy, (enemy_x, enemy_y))
    
    def start_battle(battle_manager):
        """Start the battle with all spatial systems"""
        # Initialize event queue
        battle_manager.event_queue.clear()
        
        # Activate tactical UI
        if hasattr(battle_manager, 'tactical_ui'):
            battle_manager.tactical_ui.activate()
        
        # Schedule initial AI update
        battle_manager.event_queue.schedule(0.1, 10, battle_manager._update_enemy_ai)
        
        # Log battle start
        if hasattr(battle_manager, '_log_message'):
            battle_manager._log_message("Tactical battle started!")
    
    def update_all_systems(battle_manager, delta_time):
        """
        Update all spatial combat systems
        
        Args:
            battle_manager: The battle manager instance
            delta_time (float): Time since last update
        """
        # Update core movement system
        if hasattr(battle_manager, 'movement_controller'):
            battle_manager.movement_controller.update(delta_time)
        
        # Update modifier manager
        if hasattr(battle_manager, 'modifier_manager'):
            battle_manager.modifier_manager.update(delta_time)
        
        # Update tactical AI
        if hasattr(battle_manager, 'tactical_ai'):
            battle_manager.tactical_ai.update(delta_time)
        
        # Update formation system
        if hasattr(battle_manager, 'formation_system'):
            battle_manager.formation_system.update(delta_time)
        
        # Update cover system
        if hasattr(battle_manager, 'cover_system'):
            battle_manager.cover_system.update(delta_time)
        
        # Update area effect system
        if hasattr(battle_manager, 'aoe_manager'):
            battle_manager.aoe_manager.update(delta_time)
        
        # Update tactical UI (last, depends on all others)
        if hasattr(battle_manager, 'tactical_ui'):
            battle_manager.tactical_ui.update(delta_time)
    
    def render_all_systems(battle_manager, screen):
        """
        Render all spatial combat systems
        
        Args:
            battle_manager: The battle manager instance
            screen (pygame.Surface): The screen to render to
        """
        # Only render if debug mode is on or tactical UI is active
        debug_mode = False
        if hasattr(battle_manager, 'movement_controller'):
            debug_mode = battle_manager.movement_controller.debug_render
        
        tactical_ui_active = False
        if hasattr(battle_manager, 'tactical_ui'):
            tactical_ui_active = battle_manager.tactical_ui.active
        
        if debug_mode or tactical_ui_active:
            # Render in order of layering (background to foreground)
            
            # 1. Movement system (if debug mode)
            if debug_mode and hasattr(battle_manager, 'movement_controller'):
                battle_manager.movement_controller.render(screen)
            
            # 2. Formation system (if debug mode)
            if debug_mode and hasattr(battle_manager, 'formation_system'):
                battle_manager.formation_system.render(screen)
            
            # 3. Cover system (if debug mode)
            if debug_mode and hasattr(battle_manager, 'cover_system'):
                battle_manager.cover_system.render(screen)
            
            # 4. Area effect system (always show effects)
            if hasattr(battle_manager, 'aoe_manager'):
                battle_manager.aoe_manager.render(screen)
            
            # 5. Tactical UI (always render if active)
            if tactical_ui_active and hasattr(battle_manager, 'tactical_ui'):
                battle_manager.tactical_ui.render(screen)
    
    def handle_mouse_event(battle_manager, event):
        """
        Handle mouse events for spatial combat systems
        
        Args:
            battle_manager: The battle manager instance
            event (pygame.event.Event): The mouse event
            
        Returns:
            bool: True if event was handled
        """
        # Forward to tactical UI if active
        if hasattr(battle_manager, 'tactical_ui') and battle_manager.tactical_ui.active:
            return battle_manager.tactical_ui.handle_mouse_event(event)
            
        return False
    
    def handle_key_event(battle_manager, key):
        """
        Handle key events for spatial combat systems
        
        Args:
            battle_manager: The battle manager instance
            key (int): The key code from pygame.K_*
            
        Returns:
            bool: True if event was handled
        """
        # Toggle tactical UI with T key
        if key == pygame.K_t:
            if hasattr(battle_manager, 'tactical_ui'):
                active = battle_manager.tactical_ui.toggle()
                
                # Log toggle
                if hasattr(battle_manager, '_log_message'):
                    if active:
                        battle_manager._log_message("Tactical UI activated")
                    else:
                        battle_manager._log_message("Tactical UI deactivated")
                        
                return True
                
        # Toggle debug visualization with F1 key
        elif key == pygame.K_F1:
            if hasattr(battle_manager, 'movement_controller'):
                debug_mode = battle_manager.movement_controller.toggle_debug_render()
                
                # Sync all systems
                if hasattr(battle_manager, 'cover_system'):
                    battle_manager.cover_system.debug_render = debug_mode
                    
                if hasattr(battle_manager, 'formation_system'):
                    battle_manager.formation_system.debug_render = debug_mode
                
                # Log toggle
                if hasattr(battle_manager, '_log_message'):
                    if debug_mode:
                        battle_manager._log_message("Debug visualization enabled")
                    else:
                        battle_manager._log_message("Debug visualization disabled")
                        
                return True
                
        # If tactical UI is active, let it handle key events first
        if hasattr(battle_manager, 'tactical_ui') and battle_manager.tactical_ui.active:
            # Tactical UI key handling could be added here
            pass
            
        return False
    
    def position_entity(battle_manager, entity, position):
        """
        Position an entity at a specific location
        
        Args:
            battle_manager: The battle manager instance
            entity: The entity to position
            position (tuple): The (x, y) position
            
        Returns:
            bool: True if successful
        """
        if hasattr(battle_manager, 'movement_controller'):
            return battle_manager.movement_controller.register_entity(entity, position)
            
        return False
    
    def clean_up(battle_manager):
        """Clean up all spatial combat systems"""
        # Clear active effects
        if hasattr(battle_manager, 'aoe_manager'):
            battle_manager.aoe_manager.clear_effects()
        
        # Deactivate tactical UI
        if hasattr(battle_manager, 'tactical_ui'):
            battle_manager.tactical_ui.deactivate()
        
        # Clear modifiers
        if hasattr(battle_manager, 'modifier_manager'):
            for character in battle_manager.game_state.party:
                if character:
                    battle_manager.modifier_manager.clear_modifiers(character)
            
            for enemy in battle_manager.game_state.enemies:
                battle_manager.modifier_manager.clear_modifiers(enemy)

class RealtimeBattleManager:
    """
    Manages real-time battles between party members and enemies
    """
    def __init__(self, game_state):
        """
        Initialize the real-time battle manager
        
        Args:
            game_state (GameState): Reference to the game state
        """
        self.game_state = game_state
        self.combat_log = getattr(game_state, 'combat_log', None)
        if not self.combat_log:
            from ui.combat_log import CombatLog
            self.combat_log = CombatLog()
        
        self.event_queue = CombatEventQueue()
        self.animations = []
        self.battle_time = 0
        self.paused = False
        
        # Combat encounter tracking
        self.combat_encounter_count = 0
        
        # Target selection handling
        self.target_selection_active = False
        self.selecting_character = None
        
        # AI update frequency
        self.ai_update_interval = 0.5  # seconds
        self.last_ai_update = 0
    
    # Add integration methods to RealtimeBattleManager
    def add_integration_methods(battle_manager):
        """
        Add spatial combat integration methods to a battle manager instance
        
        Args:
            battle_manager: The battle manager instance to modify
        """
        # Add initialization method
        battle_manager.initialize_spatial_combat_systems = lambda width, height: BattleSystemsIntegration.init_systems(battle_manager, width, height)
        
        # Add internal initialization
        battle_manager._initialize_spatial_combat = lambda: BattleSystemsIntegration._initialize_spatial_combat(battle_manager)
        
        # Add start battle method (using original but adding spatial systems)
        original_start_battle = battle_manager.start_battle
        battle_manager.start_battle = lambda: (original_start_battle(), BattleSystemsIntegration.start_battle(battle_manager))
        
        # Add update method
        battle_manager._update_spatial_combat_systems = lambda delta_time: BattleSystemsIntegration.update_all_systems(battle_manager, delta_time)
        
        # Add render method
        battle_manager._render_spatial_combat_systems = lambda screen: BattleSystemsIntegration.render_all_systems(battle_manager, screen)
        
        # Add event handling methods
        battle_manager.handle_mouse_event = lambda event: BattleSystemsIntegration.handle_mouse_event(battle_manager, event)
        battle_manager.handle_key_event = lambda key: BattleSystemsIntegration.handle_key_event(battle_manager, key)
        
        # Add positioning method
        battle_manager.position_entity = lambda entity, position: BattleSystemsIntegration.position_entity(battle_manager, entity, position)
        
        # Add cleanup method
        battle_manager.clean_up_spatial_systems = lambda: BattleSystemsIntegration.clean_up(battle_manager)

    def start_battle(self):
        """Initialize a new battle"""
        self.event_queue.clear()
        self.battle_time = 0
        self.animations = []
        
        # Schedule initial AI update
        self.event_queue.schedule(0.1, 10, self._update_enemy_ai)
        
        # Log battle start
        self._log_message("Battle started!")
    
    def update(self, delta_time):
        """
        Update the real-time battle system
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        if self.paused:
            return
            
        # Update battle time
        self.battle_time += delta_time
        
        # Process events from the queue
        self.event_queue.update(delta_time)
        
        # Update all combat entities
        for character in self.game_state.party:
            if character:
                character.update(delta_time)
        
        for enemy in self.game_state.enemies:
            enemy.update(delta_time)
        
        # Update animations
        self.animations = [anim for anim in self.animations if anim.update()]
        
        # AI updates at fixed intervals
        self.last_ai_update += delta_time
        if self.last_ai_update >= self.ai_update_interval:
            self._update_enemy_ai()
            self.last_ai_update = 0
        
        # Check battle state (victory/defeat)
        self._check_battle_state()
    
    def _check_battle_state(self):
        """Check for battle end conditions"""
        # Check for party defeat
        if not self._is_party_alive():
            self.game_state.defeat_count += 1
            self.game_state.change_state("game_over")
            return
            
        # Check for enemy defeat
        if not self.game_state.enemies or all(not enemy.is_alive() for enemy in self.game_state.enemies):
            self.game_state.victory_count += 1
            self.game_state.change_state("victory")
            return
    
    def _is_party_alive(self):
        """Check if any party member is alive"""
        return any(char and char.is_alive() for char in self.game_state.party)
    
    def _update_enemy_ai(self):
        """Update AI decisions for all enemies"""
        # Process each enemy's AI
        for enemy in self.game_state.enemies:
            if enemy.is_alive() and enemy.combat_state == CombatState.IDLE:
                # Select target from party
                target = self._select_target_for_enemy(enemy)
                
                if target:
                    # Check if in range
                    if not enemy.is_in_range(target):
                        # Move towards target if not in range
                        enemy.move_towards_target(target)
                    else:
                        # Attack if in range and ready
                        if enemy.can_attack():
                            attack_success = enemy.attack_target(target)
                            if attack_success:
                                # Schedule completion of attack (end of wind-up)
                                self.event_queue.schedule(
                                    enemy.attack_phase.wind_up_time,
                                    5,
                                    self._process_enemy_attack,
                                    enemy,
                                    target
                                )
        
        # Schedule next AI update
        self.event_queue.schedule(self.ai_update_interval, 10, self._update_enemy_ai)
    
    def initialize_movement_controller(self, screen_width, screen_height):
        """
        Initialize the movement controller for spatial combat
        
        Args:
            screen_width (int): Width of the screen in pixels
            screen_height (int): Height of the screen in pixels
        """
        self.movement_controller = MovementController(screen_width, screen_height)
        
        # Initialize combat grid with entities
        self._initialize_combat_positions()

    def initialize_spatial_combat_systems(self, screen_width, screen_height):
        """
        Initialize all spatial combat systems
        
        Args:
            screen_width (int): Width of the screen in pixels
            screen_height (int): Height of the screen in pixels
        """
        # Initialize movement controller
        self.movement_controller = MovementController(screen_width, screen_height)
        
        # Initialize tactical AI
        self.tactical_ai = TacticalAI(self)
        
        # Initialize formation system
        self.formation_system = FormationSystem(self)
        
        # Initialize cover system
        self.cover_system = CoverSystem(self)
        
        # Generate random cover objects
        self.cover_system.generate_random_cover(5)
        
        # Initialize combat grid with entities
        self._initialize_combat_positions()
        
        # Set initial formation
        party_center_x = screen_width // 4
        party_center_y = screen_height // 2
        self.formation_system.formation_center = pygame.Vector2(party_center_x, party_center_y)
        self.formation_system.apply_formation(FormationType.TRIANGLE)

    def initialize_spatial_combat_systems(self, screen_width, screen_height):
        """
        Initialize all spatial combat systems
        
        Args:
            screen_width (int): Width of the screen in pixels
            screen_height (int): Height of the screen in pixels
        """
        # Initialize movement controller
        self.movement_controller = MovementController(screen_width, screen_height)
        
        # Initialize tactical AI
        self.tactical_ai = TacticalAI(self)
        
        # Initialize formation system
        self.formation_system = FormationSystem(self)
        
        # Initialize cover system
        self.cover_system = CoverSystem(self)
        
        # Generate random cover objects
        self.cover_system.generate_random_cover(5)
        
        # Initialize combat grid with entities
        self._initialize_combat_positions()
        
        # Set initial formation
        party_center_x = screen_width // 4
        party_center_y = screen_height // 2
        self.formation_system.formation_center = pygame.Vector2(party_center_x, party_center_y)
        self.formation_system.apply_formation(FormationType.TRIANGLE)

    def initiate_movement(self, entity, target_position, completion_callback=None):
        """
        Initiate movement for an entity
        
        Args:
            entity (BaseCharacter): Entity to move
            target_position (tuple): (x, y) target position
            completion_callback (function, optional): Function to call when movement completes
            
        Returns:
            bool: True if movement was initiated
        """
        # Check if entity can move
        if not entity.is_alive() or entity.combat_state != CombatState.IDLE:
            return False
        
        # Start movement
        movement_started = self.movement_controller.start_movement(
            entity, target_position, entity.movement_speed)
        
        if not movement_started:
            return False
        
        # Update entity state
        entity.combat_state = CombatState.MOVING
        entity.state_start_time = time.time()
        
        # Schedule completion check
        self.event_queue.schedule(
            0.1, 10, self._check_movement_completion, entity, completion_callback
        )
        
        # Trigger movement start event
        trigger_event(EVENT_COMBAT_MOVE_START, entity, target_position)
        
        return True

    def move_entity_towards_target(self, entity, target_entity, preferred_distance=None, 
                                completion_callback=None):
        """
        Move an entity towards a target entity
        
        Args:
            entity (BaseCharacter): Entity to move
            target_entity (BaseCharacter): Target to move towards
            preferred_distance (float, optional): Preferred distance to maintain
            completion_callback (function, optional): Function to call when movement completes
            
        Returns:
            bool: True if movement was initiated
        """
        # Check if entity can move
        if not entity.is_alive() or entity.combat_state != CombatState.IDLE:
            return False
        
        # Start movement
        movement_started = self.movement_controller.move_towards_entity(
            entity, target_entity, preferred_distance, entity.movement_speed)
        
        if not movement_started:
            return False
        
        # Update entity state
        entity.combat_state = CombatState.MOVING
        entity.state_start_time = time.time()
        
        # Schedule completion check
        self.event_queue.schedule(
            0.1, 10, self._check_movement_completion, entity, completion_callback
        )
        
        # Trigger movement start event
        trigger_event(EVENT_COMBAT_MOVE_START, entity, target_entity)
        
        return True

    def _check_movement_completion(self, entity, completion_callback=None):
        """
        Check if entity's movement is complete and handle completion
        
        Args:
            entity (BaseCharacter): Entity to check
            completion_callback (function, optional): Function to call when movement completes
        """
        if not entity.is_alive():
            self.movement_controller.stop_movement(entity)
            return
        
        # Check if movement is complete
        if self.movement_controller.is_entity_at_target(entity):
            # Movement complete
            self.movement_controller.stop_movement(entity)
            
            # Update entity state
            old_state = entity.combat_state
            entity.combat_state = CombatState.IDLE
            entity.state_start_time = time.time()
            
            # Trigger movement end event
            trigger_event(EVENT_COMBAT_MOVE_END, entity)
            
            # Trigger state change event
            trigger_event(EVENT_COMBAT_STATE_CHANGE, entity, old_state, CombatState.IDLE)
            
            # Call completion callback if provided
            if completion_callback:
                completion_callback(entity)
        else:
            # Movement still in progress, check again later
            self.event_queue.schedule(
                0.1, 10, self._check_movement_completion, entity, completion_callback
            )

    def _update_spatial_combat_systems(self, delta_time):
        """Update all spatial combat systems"""
        # Update movement controller
        if hasattr(self, 'movement_controller'):
            self.movement_controller.update(delta_time)
        
        # Update tactical AI
        if hasattr(self, 'tactical_ai'):
            self.tactical_ai.update(delta_time)
        
        # Update formation system
        if hasattr(self, 'formation_system'):
            self.formation_system.update(delta_time)
        
        # Update cover system
        if hasattr(self, 'cover_system'):
            self.cover_system.update(delta_time)

    def _render_spatial_combat_systems(self, screen):
        """Render spatial combat debug visualizations"""
        # Only render if debug mode is on
        if not hasattr(self, 'movement_controller') or not self.movement_controller.debug_render:
            return
        
        # Render movement system
        self.movement_controller.render(screen)
        
        # Render formation system
        if hasattr(self, 'formation_system'):
            self.formation_system.render(screen)
        
        # Render cover system
        if hasattr(self, 'cover_system'):
            self.cover_system.render(screen)

    def _update_movement_system(self, delta_time):
        """Update the movement controller"""
        if hasattr(self, 'movement_controller'):
            self.movement_controller.update(delta_time)

    def _render_movement_system(self, screen):
        """Render movement debug visualization"""
        if hasattr(self, 'movement_controller') and self.movement_controller.debug_render:
            self.movement_controller.render(screen)

    def _process_enemy_attack(self, enemy, target):
        """
        Process an enemy's attack when wind-up completes
        
        Args:
            enemy (Enemy): The attacking enemy
            target (BaseCharacter): The target character
        """
        # Make sure enemy and target are still valid
        if not enemy.is_alive() or enemy.combat_state != CombatState.WIND_UP:
            return
            
        if not target.is_alive():
            # Target died before attack completed, find new target
            new_target = self._select_target_for_enemy(enemy)
            if new_target:
                target = new_target
            else:
                # No valid targets, cancel attack
                enemy.combat_state = CombatState.RECOVERY
                enemy.state_start_time = time.time()
                return
        
        # Complete the attack
        result = enemy.complete_attack(target)
        
        # Log the attack
        self._log_attack(enemy, target, result)
        
        # Add attack animation
        if hasattr(self.game_state, 'animation_helper'):
            animation_type = enemy.get_animation_type()
            self.game_state.animation_helper.add_attack_animation(enemy, target, animation_type)
        
        # Check if character died
        if not target.is_alive():
            self._log_message(f"{target.name} has been defeated!")
            
            # Check if all party members are dead
            if not self._is_party_alive():
                self._log_message("The party has been defeated!")
        
        # Schedule transition to idle after recovery
        self.event_queue.schedule(
            enemy.attack_phase.recovery_time,
            5,
            self._complete_recovery,
            enemy
        )
    
    def _complete_recovery(self, character):
        """
        Complete recovery phase and return to idle
        
        Args:
            character (BaseCharacter): The character completing recovery
        """
        if character.is_alive() and character.combat_state == CombatState.RECOVERY:
            character.combat_state = CombatState.IDLE
            character.state_start_time = time.time()
    
    def _select_target_for_enemy(self, enemy):
        """
        Select a target for an enemy to attack
        
        Args:
            enemy (Enemy): The enemy selecting a target
            
        Returns:
            BaseCharacter: The selected target
        """
        # Basic targeting strategy based on enemy type
        living_party = [char for char in self.game_state.party if char and char.is_alive()]
        
        if not living_party:
            return None
            
        # Different enemy types might have different targeting strategies
        if hasattr(enemy, 'targeting_priority'):
            if enemy.targeting_priority == "weakest":
                # Target character with lowest HP percentage
                return min(living_party, key=lambda char: char.current_hp / char.max_hp)
            elif enemy.targeting_priority == "strongest":
                # Target character with highest attack
                return max(living_party, key=lambda char: char.attack)
            elif enemy.targeting_priority == "magical":
                # Target character with highest magic
                return max(living_party, key=lambda char: char.magic)
            elif enemy.targeting_priority == "random":
                # Random targeting
                import random
                return random.choice(living_party)
        
        # Default: random target
        import random
        return random.choice(living_party)
    
    def initiate_player_attack(self, character, target):
        """
        Initiate an attack by a player character
        
        Args:
            character (BaseCharacter): The attacking character
            target (BaseCharacter): The target
            
        Returns:
            bool: True if attack was initiated
        """
        if not character.can_attack() or not target.is_alive():
            return False
        
        # Start attack sequence
        attack_started = character.attack_target(target)
        if not attack_started:
            return False
        
        # Schedule completion of attack (end of wind-up)
        self.event_queue.schedule(
            character.attack_phase.wind_up_time,
            5,
            self._process_player_attack,
            character,
            target
        )
        
        return True
    
    def _process_player_attack(self, character, target):
        """
        Process a player's attack when wind-up completes
        
        Args:
            character (BaseCharacter): The attacking character
            target (BaseCharacter): The target
        """
        # Make sure character and target are still valid
        if not character.is_alive() or character.combat_state != CombatState.WIND_UP:
            return
            
        if not target.is_alive():
            # Target died before attack completed, cancel attack
            character.combat_state = CombatState.RECOVERY
            character.state_start_time = time.time()
            return
        
        # Complete the attack
        result = character.complete_attack(target)
        
        # Log the attack
        self._log_attack(character, target, result)
        
        # Add attack animation
        if hasattr(self.game_state, 'animation_helper'):
            animation_type = character.get_animation_type()
            self.game_state.animation_helper.add_attack_animation(character, target, animation_type)
        
        # Check if enemy died
        if not target.is_alive():
            self._handle_enemy_defeat(target, character)
        
        # Schedule transition to idle after recovery
        self.event_queue.schedule(
            character.attack_phase.recovery_time,
            5,
            self._complete_recovery,
            character
        )
    
    def initiate_target_selection(self, character):
        """
        Start the target selection process for a player character
        
        Args:
            character (BaseCharacter): Character selecting a target
            
        Returns:
            bool: True if selection was initiated
        """
        if not character.can_attack():
            return False
        
        # Get living enemies as potential targets
        potential_targets = [enemy for enemy in self.game_state.enemies if enemy.is_alive()]
        if not potential_targets:
            return False
        
        # Set target selection state
        self.target_selection_active = True
        self.selecting_character = character
        self.game_state.selecting_target = True
        self.game_state.potential_targets = potential_targets
        
        return True
    
    def select_target(self, target_index):
        """
        Complete target selection and initiate attack
        
        Args:
            target_index (int): Index of selected target
            
        Returns:
            bool: True if attack was initiated
        """
        if not self.target_selection_active:
            return False
            
        if 0 <= target_index < len(self.game_state.potential_targets):
            target = self.game_state.potential_targets[target_index]
            character = self.selecting_character
            
            # Check if target is in range
            if not character.is_in_range(target):
                # Begin moving towards target if not in range
                character.move_towards_target(target)
                
                # Schedule attack when character gets in range
                self.event_queue.schedule(
                    0.1, 5, self._check_attack_range, character, target
                )
            else:
                # Initiate attack if in range
                result = self.initiate_player_attack(character, target)
                
                # Reset target selection state
                self.target_selection_active = False
                self.selecting_character = None
                self.game_state.selecting_target = False
                self.game_state.potential_targets = []
                
                return result
        
        # Reset target selection state if attack wasn't initiated
        self.cancel_target_selection()
        return False
    
    def _check_attack_range(self, character, target):
        """
        Check if character is in range to attack target, and attack if possible
        
        Args:
            character (BaseCharacter): The character moving to attack
            target (BaseCharacter): The target
            
        Returns:
            bool: True if attack was initiated
        """
        if not character.is_alive() or not target.is_alive():
            # Reset target selection if either character is not alive
            self.cancel_target_selection()
            return False
            
        # Check if in range
        if character.is_in_range(target):
            # Stop movement
            character.is_moving = False
            
            # Initiate attack if ready
            if character.can_attack():
                result = self.initiate_player_attack(character, target)
                
                # Reset target selection
                self.cancel_target_selection()
                return result
        else:
            # Not in range yet, keep moving and check again
            character.move_towards_target(target)
            self.event_queue.schedule(
                0.1, 5, self._check_attack_range, character, target
            )
        
        return False
    
    def cancel_target_selection(self):
        """Cancel the current target selection"""
        self.target_selection_active = False
        self.selecting_character = None
        self.game_state.selecting_target = False
        self.game_state.potential_targets = []
    
    def _handle_enemy_defeat(self, enemy, character):
        """
        Handle effects of defeating an enemy
        
        Args:
            enemy (Enemy): The defeated enemy
            character (BaseCharacter): Character that defeated the enemy
        """
        # Award XP to all living party members
        # The character that dealt the killing blow gets a bonus
        xp_gained = enemy.get_xp_value()
        
        # Calculate shared XP (70% of total, divided among all living party members)
        living_party_count = sum(1 for char in self.game_state.party if char and char.is_alive())
        shared_xp = int(xp_gained * 0.7 / living_party_count) if living_party_count > 0 else 0
        
        # Killer gets bonus XP (30% of total)
        killer_bonus = int(xp_gained * 0.3)
        
        # Award XP to all living party members
        for char in self.game_state.party:
            if char and char.is_alive():
                # Award shared XP
                char_xp = shared_xp
                
                # Add bonus for the killer
                if char == character:
                    char_xp += killer_bonus
                
                # Apply XP gain
                leveled_up = char.gain_xp(char_xp)
                
                # Log results
                self._log_message(f"{char.name} gained {char_xp} XP")
                if leveled_up:
                    self._log_message(f"{char.name} leveled up to level {char.level}!")
        
        # Log the defeat
        self._log_message(f"{enemy.name} has been defeated!")
    
    def _log_attack(self, attacker, target, result):
        """
        Log an attack to the combat log
        
        Args:
            attacker (BaseCharacter): The attacking character
            target (BaseCharacter): The target character
            result (dict): Attack result
        """
        # Use the combat log component's method
        if hasattr(self.combat_log, 'log_attack'):
            self.combat_log.log_attack(attacker, target, result)
        else:
            # Fallback if log_attack method is not available
            hit_status = "hit" if result.get("hit", False) else "missed"
            damage = result.get("damage", 0)
            self._log_message(f"{attacker.name} {hit_status} {target.name} for {damage} damage")
    
    def _log_message(self, message):
        """
        Add a message to the combat log
        
        Args:
            message (str): The message to log
        """
        # Use the combat log component's method
        if self.combat_log:
            self.combat_log.add_entry(message)
        else:
            # Fallback if combat log is not available
            print(f"[COMBAT] {message}")
    
    def toggle_pause(self):
        """
        Toggle the battle pause state
        
        Returns:
            bool: New pause state
        """
        self.paused = not self.paused
        return self.paused
    
    def render_animations(self, screen):
        """
        Render battle effects and indicators
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Render animations
        for animation in self.animations:
            animation.render(screen)
        
        # Render range indicators for target selection
        if self.target_selection_active and self.selecting_character:
            char = self.selecting_character
            char_center = (char.position[0] + char.sprite.get_width() // 2, 
                         char.position[1] + char.sprite.get_height() // 2)
            
            # Draw attack range circle
            pygame.draw.circle(
                screen,
                (255, 255, 0),  # Yellow
                char_center,
                char.attack_range,
                1  # Line width
            )
    
    def get_recent_log(self, count=10):
        """
        Get the most recent log messages
        
        Args:
            count (int): Number of messages to return
            
        Returns:
            list: Recent combat log messages
        """
        if hasattr(self.combat_log, 'get_recent_entries'):
            return self.combat_log.get_recent_entries(count)
        return []