"""
Tactical UI Controller - User interface for spatial combat controls
"""
import pygame
import math
from combat.combat_state import CombatState
from combat.formation_system import FormationType
from combat.area_effect_system import AoEShape

class TacticalUIController:
    """
    Manages user interface for tactical combat controls
    """
    def __init__(self, battle_manager):
        """
        Initialize tactical UI controller
        
        Args:
            battle_manager: Reference to the battle manager
        """
        self.battle_manager = battle_manager
        
        # UI state
        self.active = False
        self.current_mode = "movement"  # movement, formation, ability, target
        self.selected_ability = None
        self.ability_target_position = None
        self.show_grid = False
        self.show_paths = True
        self.show_ranges = True
        
        # Initialize fonts
        self.fonts = {
            "small": pygame.font.SysFont("Arial", 14),
            "medium": pygame.font.SysFont("Arial", 18),
            "large": pygame.font.SysFont("Arial", 24)
        }
        
        # Button definitions (x, y, width, height, text, action)
        self.buttons = []
        
        # Current UI mode controls
        self.mode_controls = {}
        
        # Dragging state
        self.dragging = False
        self.drag_start = None
        self.drag_entity = None
        
        # Ability placement state
        self.placing_ability = False
        self.ability_preview = None
        
        # Formation editor state
        self.editing_formation = False
        self.formation_preview = None
        
        # Action history for undo
        self.action_history = []
        
        # Initialize UI elements
        self._initialize_ui()
    
    def _initialize_ui(self):
        """Initialize UI elements"""
        # Bottom panel buttons
        button_height = 30
        button_width = 120
        panel_height = 40
        spacing = 10
        
        # Calculate positions at the bottom of the screen
        if hasattr(self.battle_manager, 'screen_width'):
            screen_width = self.battle_manager.screen_width
            screen_height = self.battle_manager.screen_height
        else:
            # Default screen size if not available
            screen_width = 1024
            screen_height = 768
            
        # Bottom panel
        panel_y = screen_height - panel_height
        
        # Button positions
        button_y = panel_y + (panel_height - button_height) // 2
        
        # Define the buttons
        self.buttons = [
            # Mode buttons (bottom panel)
            {
                "rect": pygame.Rect(spacing, button_y, button_width, button_height),
                "text": "Movement",
                "action": lambda: self._set_mode("movement"),
                "tooltip": "Movement mode - Click on the map to move selected character"
            },
            {
                "rect": pygame.Rect(spacing * 2 + button_width, button_y, button_width, button_height),
                "text": "Formation",
                "action": lambda: self._set_mode("formation"),
                "tooltip": "Formation mode - Arrange party in formations"
            },
            {
                "rect": pygame.Rect(spacing * 3 + button_width * 2, button_y, button_width, button_height),
                "text": "Abilities",
                "action": lambda: self._set_mode("ability"),
                "tooltip": "Ability mode - Use special abilities and area attacks"
            },
            {
                "rect": pygame.Rect(spacing * 4 + button_width * 3, button_y, button_width, button_height),
                "text": "End Turn",
                "action": self._end_turn,
                "tooltip": "End the current character's turn"
            },
            # Visualization toggle (top-right)
            {
                "rect": pygame.Rect(screen_width - button_width - spacing, spacing, button_width, button_height),
                "text": "Show Grid",
                "action": self._toggle_grid,
                "tooltip": "Toggle grid display"
            }
        ]
        
        # Mode-specific controls
        self.mode_controls = {
            "movement": self._create_movement_controls(),
            "formation": self._create_formation_controls(),
            "ability": self._create_ability_controls()
        }
    
    def _create_movement_controls(self):
        """Create movement mode controls"""
        # Control panel on the right side
        panel_width = 200
        button_height = 30
        button_width = 180
        spacing = 10
        
        # Calculate positions
        if hasattr(self.battle_manager, 'screen_width'):
            screen_width = self.battle_manager.screen_width
            screen_height = self.battle_manager.screen_height
        else:
            screen_width = 1024
            screen_height = 768
            
        panel_x = screen_width - panel_width - spacing
        panel_y = 50
        
        controls = [
            # Movement controls
            {
                "rect": pygame.Rect(panel_x, panel_y, button_width, button_height),
                "text": "Find Cover",
                "action": self._find_cover,
                "tooltip": "Move to nearest available cover"
            },
            {
                "rect": pygame.Rect(panel_x, panel_y + button_height + spacing, button_width, button_height),
                "text": "Move to Flank",
                "action": self._move_to_flank,
                "tooltip": "Move to flanking position around target"
            },
            {
                "rect": pygame.Rect(panel_x, panel_y + (button_height + spacing) * 2, button_width, button_height),
                "text": "Take Cover",
                "action": self._take_cover,
                "tooltip": "Take cover at current position (if available)"
            },
            {
                "rect": pygame.Rect(panel_x, panel_y + (button_height + spacing) * 3, button_width, button_height),
                "text": "Break Cover",
                "action": self._break_cover,
                "tooltip": "Break cover and return to normal stance"
            }
        ]
        
        return controls
    
    def _create_formation_controls(self):
        """Create formation mode controls"""
        # Control panel on the right side
        panel_width = 200
        button_height = 30
        button_width = 180
        spacing = 10
        
        # Calculate positions
        if hasattr(self.battle_manager, 'screen_width'):
            screen_width = self.battle_manager.screen_width
            screen_height = self.battle_manager.screen_height
        else:
            screen_width = 1024
            screen_height = 768
            
        panel_x = screen_width - panel_width - spacing
        panel_y = 50
        
        controls = []
        
        # Formation buttons
        formations = [
            (FormationType.LINE, "Line"),
            (FormationType.TRIANGLE, "Triangle"),
            (FormationType.COLUMN, "Column"),
            (FormationType.SPREAD, "Spread"),
            (FormationType.CIRCLE, "Circle"),
            (FormationType.FLANK, "Flank"),
            (FormationType.WEDGE, "Wedge")
        ]
        
        for i, (formation_type, name) in enumerate(formations):
            controls.append({
                "rect": pygame.Rect(panel_x, panel_y + (button_height + spacing) * i, button_width, button_height),
                "text": name,
                "action": lambda f=formation_type: self._set_formation(f),
                "tooltip": f"Change to {name} formation"
            })
        
        # Add rotation controls
        controls.append({
            "rect": pygame.Rect(panel_x, panel_y + (button_height + spacing) * len(formations), button_width, button_height),
            "text": "Rotate Left",
            "action": lambda: self._rotate_formation(-45),
            "tooltip": "Rotate formation counter-clockwise"
        })
        
        controls.append({
            "rect": pygame.Rect(panel_x, panel_y + (button_height + spacing) * (len(formations) + 1), button_width, button_height),
            "text": "Rotate Right",
            "action": lambda: self._rotate_formation(45),
            "tooltip": "Rotate formation clockwise"
        })
        
        return controls
    
    def _create_ability_controls(self):
        """Create ability mode controls"""
        # Control panel on the right side
        panel_width = 200
        button_height = 30
        button_width = 180
        spacing = 10
        
        # Calculate positions
        if hasattr(self.battle_manager, 'screen_width'):
            screen_width = self.battle_manager.screen_width
            screen_height = self.battle_manager.screen_height
        else:
            screen_width = 1024
            screen_height = 768
            
        panel_x = screen_width - panel_width - spacing
        panel_y = 50
        
        controls = []
        
        # Ability buttons - would be populated based on active character
        # Here are some sample abilities
        abilities = [
            ("fireball", "Fireball", "Fire damage in an area"),
            ("ice_storm", "Ice Storm", "Ice damage and slow in an area"),
            ("lightning_bolt", "Lightning Bolt", "Lightning damage in a line"),
            ("heal_circle", "Healing Circle", "Heal allies in an area"),
            ("shockwave", "Shockwave", "Knockback and stun in an area")
        ]
        
        for i, (ability_id, name, desc) in enumerate(abilities):
            controls.append({
                "rect": pygame.Rect(panel_x, panel_y + (button_height + spacing) * i, button_width, button_height),
                "text": name,
                "action": lambda a=ability_id: self._select_ability(a),
                "tooltip": desc,
                "ability_id": ability_id
            })
        
        return controls
    
    def activate(self):
        """Activate the tactical UI"""
        self.active = True
        
        # Set default mode
        self._set_mode("movement")
    
    def deactivate(self):
        """Deactivate the tactical UI"""
        self.active = False
        self.selected_ability = None
        self.placing_ability = False
        self.editing_formation = False
    
    def toggle(self):
        """Toggle tactical UI activation"""
        if self.active:
            self.deactivate()
        else:
            self.activate()
            
        return self.active
    
    def _set_mode(self, mode):
        """
        Set the current UI mode
        
        Args:
            mode (str): New mode
        """
        if mode not in ["movement", "formation", "ability", "target"]:
            return
            
        self.current_mode = mode
        self.selected_ability = None
        self.placing_ability = False
        self.editing_formation = False
        
        # Cancel any ongoing actions
        if mode == "movement":
            pass  # Additional movement mode setup
        elif mode == "formation":
            # Enable formation preview
            self.editing_formation = True
            if hasattr(self.battle_manager, 'formation_system'):
                formation_system = self.battle_manager.formation_system
                self.formation_preview = formation_system.current_formation
        elif mode == "ability":
            pass  # Additional ability mode setup
    
    def _select_ability(self, ability_id):
        """
        Select an ability to use
        
        Args:
            ability_id (str): ID of the ability
        """
        self.selected_ability = ability_id
        self.placing_ability = True
        
        # Create preview effect
        if hasattr(self.battle_manager, 'aoe_manager'):
            aoe_manager = self.battle_manager.aoe_manager
            
            # Get active character
            character = self._get_active_character()
            
            if character:
                # Create effect but don't activate yet
                self.ability_preview = aoe_manager.create_effect(
                    ability_id, 
                    (character.position.x, character.position.y),
                    (1, 0),  # Default direction
                    character
                )
    
    def _toggle_grid(self):
        """Toggle grid display"""
        self.show_grid = not self.show_grid
        
        # Toggle grid in movement controller
        if hasattr(self.battle_manager, 'movement_controller'):
            self.battle_manager.movement_controller.debug_render = self.show_grid
    
    def _end_turn(self):
        """End the current character's turn"""
        # Reset character cooldowns or perform other end-of-turn actions
        character = self._get_active_character()
        if character:
            # Example: Reset attack cooldown
            character.attack_cooldown = 0
            
            # Move to next character
            if hasattr(self.battle_manager.game_state, 'select_next_active_character'):
                self.battle_manager.game_state.select_next_active_character()
    
    def _find_cover(self):
        """Find and move to nearest cover"""
        character = self._get_active_character()
        if not character or not hasattr(self.battle_manager, 'cover_system'):
            return
            
        # Find nearest cover
        cover_pos = self.battle_manager.cover_system.find_nearest_cover(character)
        
        if cover_pos:
            # Move to cover
            if hasattr(self.battle_manager, 'initiate_movement'):
                self.battle_manager.initiate_movement(
                    character, cover_pos, 
                    lambda char: self.battle_manager.cover_system.take_cover(char))
                
                # Log the action
                if hasattr(self.battle_manager, '_log_message'):
                    self.battle_manager._log_message(f"{character.name} moves to nearest cover")
        else:
            # No cover found
            if hasattr(self.battle_manager, '_log_message'):
                self.battle_manager._log_message(f"No cover found for {character.name}")
    
    def _move_to_flank(self):
        """Move to flanking position around current target"""
        character = self._get_active_character()
        if not character or not hasattr(self.battle_manager.game_state, 'enemies'):
            return
            
        # Find a valid target
        enemies = [e for e in self.battle_manager.game_state.enemies if e.is_alive()]
        if not enemies:
            return
            
        # Get nearest enemy as target
        target = min(enemies, key=lambda e: 
                    math.hypot(e.position.x - character.position.x, 
                              e.position.y - character.position.y))
        
        # Calculate flanking position
        # Find if any allies are attacking this target
        allies = [c for c in self.battle_manager.game_state.party 
                 if c and c != character and c.is_alive()]
        
        flank_positions = []
        
        # Generate positions around the target
        radius = character.attack_range * 0.8  # Slightly inside attack range
        
        # Find existing ally positions to avoid overlapping
        ally_positions = []
        for ally in allies:
            if hasattr(ally, 'current_target') and ally.current_target == target:
                ally_positions.append((ally.position.x, ally.position.y))
        
        # Generate potential flank positions
        num_positions = 8
        for i in range(num_positions):
            angle = 2 * math.pi * i / num_positions
            x = target.position.x + math.cos(angle) * radius
            y = target.position.y + math.sin(angle) * radius
            flank_positions.append((x, y))
        
        # Find best flanking position that's not near an ally
        best_pos = None
        best_score = float('-inf')
        
        for pos in flank_positions:
            # Check if position is valid
            if hasattr(self.battle_manager, 'movement_controller'):
                if not self.battle_manager.movement_controller.combat_grid.is_position_free(pos):
                    continue
            
            # Calculate flanking score
            # Higher score for positions opposite to allies
            score = 0
            
            # Add score for each ally based on flanking angle
            for ally_pos in ally_positions:
                # Vector from target to ally
                ally_vector = (ally_pos[0] - target.position.x, ally_pos[1] - target.position.y)
                # Vector from target to potential position
                pos_vector = (pos[0] - target.position.x, pos[1] - target.position.y)
                
                # Calculate dot product
                dot = ally_vector[0] * pos_vector[0] + ally_vector[1] * pos_vector[1]
                
                # Normalize by vector lengths
                ally_length = math.sqrt(ally_vector[0]**2 + ally_vector[1]**2)
                pos_length = math.sqrt(pos_vector[0]**2 + pos_vector[1]**2)
                
                if ally_length > 0 and pos_length > 0:
                    dot_normalized = dot / (ally_length * pos_length)
                    
                    # Convert to angle
                    angle = math.acos(max(-1.0, min(1.0, dot_normalized)))
                    
                    # Higher score for positions closer to 180 degrees (opposite)
                    score += math.pi - abs(math.pi - angle)
            
            # If no allies, prefer positions based on current position
            if not ally_positions:
                # Vector from target to character
                char_vector = (character.position.x - target.position.x, 
                             character.position.y - target.position.y)
                # Vector from target to potential position
                pos_vector = (pos[0] - target.position.x, pos[1] - target.position.y)
                
                # Calculate dot product
                dot = char_vector[0] * pos_vector[0] + char_vector[1] * pos_vector[1]
                
                # Normalize by vector lengths
                char_length = math.sqrt(char_vector[0]**2 + char_vector[1]**2)
                pos_length = math.sqrt(pos_vector[0]**2 + pos_vector[1]**2)
                
                if char_length > 0 and pos_length > 0:
                    dot_normalized = dot / (char_length * pos_length)
                    
                    # Convert to angle
                    angle = math.acos(max(-1.0, min(1.0, dot_normalized)))
                    
                    # Prefer positions with some angle from current position (not too far)
                    score += -abs(math.pi/2 - angle)
            
            # Update best position
            if score > best_score:
                best_score = score
                best_pos = pos
        
        # If found a valid position, move there
        if best_pos:
            # Set target
            character.current_target = target
            
            # Move to flanking position
            if hasattr(self.battle_manager, 'initiate_movement'):
                self.battle_manager.initiate_movement(
                    character, best_pos, 
                    lambda char: self._apply_flanking_bonus(char, target))
                
                # Log the action
                if hasattr(self.battle_manager, '_log_message'):
                    self.battle_manager._log_message(f"{character.name} moves to flank {target.name}")
        else:
            # No valid flanking position
            if hasattr(self.battle_manager, '_log_message'):
                self.battle_manager._log_message(f"No valid flanking position for {character.name}")
    
    def _apply_flanking_bonus(self, character, target):
        """
        Apply flanking bonus after movement
        
        Args:
            character: Character that moved
            target: Target being flanked
        """
        # Apply flanking bonus if available
        if not hasattr(self.battle_manager, 'tactical_ai'):
            return
            
        # Use modifier manager if available
        if hasattr(self.battle_manager, 'modifier_manager'):
            from combat.combat_modifiers import (
                CombatModifier, CombatModifierType, CombatModifierSource
            )
            
            # Create flanking modifier
            hit_modifier = CombatModifier(
                CombatModifierType.HIT_CHANCE, 
                0.2,  # +20% hit chance
                CombatModifierSource.FLANKING,
                10.0,  # 10 second duration
                "Flanking: +20% hit chance"
            )
            
            # Add modifier
            self.battle_manager.modifier_manager.add_modifier(character, hit_modifier)
            
            # Log the effect
            if hasattr(self.battle_manager, '_log_message'):
                self.battle_manager._log_message(f"{character.name} gains flanking bonus against {target.name}")
    
    def _take_cover(self):
        """Take cover at current position"""
        character = self._get_active_character()
        if not character or not hasattr(self.battle_manager, 'cover_system'):
            return
            
        # Try to take cover
        if self.battle_manager.cover_system.take_cover(character):
            # Log the action
            if hasattr(self.battle_manager, '_log_message'):
                self.battle_manager._log_message(f"{character.name} takes cover")
        else:
            # No cover available
            if hasattr(self.battle_manager, '_log_message'):
                self.battle_manager._log_message(f"No cover available for {character.name}")
    
    def _break_cover(self):
        """Break cover and return to normal stance"""
        character = self._get_active_character()
        if not character or not hasattr(self.battle_manager, 'cover_system'):
            return
            
        # Try to break cover
        if self.battle_manager.cover_system.break_cover(character):
            # Log the action
            if hasattr(self.battle_manager, '_log_message'):
                self.battle_manager._log_message(f"{character.name} breaks cover")
        else:
            # Not in cover
            if hasattr(self.battle_manager, '_log_message'):
                self.battle_manager._log_message(f"{character.name} is not in cover")
    
    def _set_formation(self, formation_type):
        """
        Set party formation
        
        Args:
            formation_type (str): Type of formation
        """
        if not hasattr(self.battle_manager, 'formation_system'):
            return
            
        # Apply formation
        formation_system = self.battle_manager.formation_system
        
        if formation_system.apply_formation(formation_type):
            # Update preview
            self.formation_preview = formation_type
            
            # Log the action
            if hasattr(self.battle_manager, '_log_message'):
                self.battle_manager._log_message(f"Party formation changed to {formation_type}")
                
            # Apply formation bonuses to party members
            if hasattr(self.battle_manager, 'modifier_manager'):
                # Apply formation bonuses to all party members
                for character in self.battle_manager.game_state.party:
                    if character and character.is_alive():
                        self.battle_manager.modifier_manager.apply_formation_bonus(
                            character, formation_type)
    
    def _rotate_formation(self, angle):
        """
        Rotate party formation
        
        Args:
            angle (float): Rotation angle in degrees
        """
        if not hasattr(self.battle_manager, 'formation_system'):
            return
            
        # Rotate formation
        formation_system = self.battle_manager.formation_system
        
        if formation_system.rotate_formation(angle):
            # Log the action
            if hasattr(self.battle_manager, '_log_message'):
                self.battle_manager._log_message(f"Party formation rotated by {angle} degrees")
    
    def _get_active_character(self):
        """
        Get the currently active character
        
        Returns:
            Character: Active character or None
        """
        if not hasattr(self.battle_manager, 'game_state'):
            return None
            
        game_state = self.battle_manager.game_state
        
        if not hasattr(game_state, 'active_character_index'):
            return None
            
        # Get active character from party
        idx = game_state.active_character_index
        
        if idx < 0 or idx >= len(game_state.party):
            return None
            
        return game_state.party[idx]
    
    def handle_mouse_event(self, event):
        """
        Handle mouse events
        
        Args:
            event (pygame.event.Event): Mouse event
            
        Returns:
            bool: True if event was handled
        """
        if not self.active:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Click
            position = event.pos
            
            # Check if clicking on a button
            for button in self.buttons:
                if button["rect"].collidepoint(position):
                    if "action" in button:
                        button["action"]()
                    return True
            
            # Check mode-specific controls
            if self.current_mode in self.mode_controls:
                for control in self.mode_controls[self.current_mode]:
                    if control["rect"].collidepoint(position):
                        if "action" in control:
                            control["action"]()
                        return True
            
            # Handle mode-specific click functionality
            if self.current_mode == "movement":
                return self._handle_movement_click(position)
            elif self.current_mode == "formation":
                return self._handle_formation_click(position)
            elif self.current_mode == "ability":
                return self._handle_ability_click(position)
        
        elif event.type == pygame.MOUSEMOTION:
            # Mouse movement
            position = event.pos
            
            # Check hover for tooltips
            for button in self.buttons:
                if button["rect"].collidepoint(position):
                    if "tooltip" in button:
                        self._show_tooltip(button["tooltip"], position)
                    return True
            
            # Check mode-specific controls
            if self.current_mode in self.mode_controls:
                for control in self.mode_controls[self.current_mode]:
                    if control["rect"].collidepoint(position):
                        if "tooltip" in control:
                            self._show_tooltip(control["tooltip"], position)
                        return True
            
            # Handle mode-specific movement functionality
            if self.current_mode == "movement" and self.dragging:
                return self._handle_movement_drag(position)
            elif self.current_mode == "ability" and self.placing_ability:
                return self._handle_ability_movement(position)
            elif self.current_mode == "formation" and self.editing_formation:
                return self._handle_formation_movement(position)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            # Release
            position = event.pos
            
            # Handle mode-specific release functionality
            if self.current_mode == "movement" and self.dragging:
                return self._handle_movement_release(position)
            elif self.current_mode == "ability" and self.placing_ability:
                return self._handle_ability_release(position)
            elif self.current_mode == "formation" and self.editing_formation:
                return self._handle_formation_release(position)
        
        return False
    
    def _handle_movement_click(self, position):
        """
        Handle click in movement mode
        
        Args:
            position (tuple): Mouse position
            
        Returns:
            bool: True if handled
        """
        # Get active character
        character = self._get_active_character()
        if not character:
            return False
            
        # Check if clicking on a character (for dragging)
        if self._is_position_over_character(position, character):
            self.dragging = True
            self.drag_start = position
            self.drag_entity = character
            return True
        
        # Otherwise, move character to clicked position
        if hasattr(self.battle_manager, 'initiate_movement'):
            if self.battle_manager.initiate_movement(character, position):
                return True
        
        return False
    
    def _handle_movement_drag(self, position):
        """
        Handle drag in movement mode
        
        Args:
            position (tuple): Mouse position
            
        Returns:
            bool: True if handled
        """
        # Nothing to do when dragging in movement mode
        return True
    
    def _handle_movement_release(self, position):
        """
        Handle release in movement mode
        
        Args:
            position (tuple): Mouse position
            
        Returns:
            bool: True if handled
        """
        if not self.drag_entity:
            self.dragging = False
            return False
            
        # Move entity to release position
        if hasattr(self.battle_manager, 'initiate_movement'):
            if self.battle_manager.initiate_movement(self.drag_entity, position):
                self.dragging = False
                self.drag_entity = None
                return True
        
        self.dragging = False
        self.drag_entity = None
        return False
    
    def _handle_formation_click(self, position):
        """
        Handle click in formation mode
        
        Args:
            position (tuple): Mouse position
            
        Returns:
            bool: True if handled
        """
        # Check if clicking in battle area (not on UI)
        if self._is_position_in_battle_area(position):
            # Move formation center
            if hasattr(self.battle_manager, 'formation_system'):
                formation_system = self.battle_manager.formation_system
                
                # Update formation center and apply
                formation_system.formation_center = pygame.Vector2(position)
                formation_system.apply_formation()
                
                return True
        
        return False
    
    def _handle_formation_movement(self, position):
        """
        Handle movement in formation mode
        
        Args:
            position (tuple): Mouse position
            
        Returns:
            bool: True if handled
        """
        # Preview formation at mouse position
        if self._is_position_in_battle_area(position) and hasattr(self.battle_manager, 'formation_system'):
            # Update preview position
            self.battle_manager.formation_system.formation_center = pygame.Vector2(position)
            
            return True
        
        return False
    
    def _handle_formation_release(self, position):
        """
        Handle release in formation mode
        
        Args:
            position (tuple): Mouse position
            
        Returns:
            bool: True if handled
        """
        # Commit formation change on release
        if self._is_position_in_battle_area(position) and hasattr(self.battle_manager, 'formation_system'):
            formation_system = self.battle_manager.formation_system
            
            # Apply formation at release position
            formation_system.formation_center = pygame.Vector2(position)
            formation_system.apply_formation()
            
            return True
        
        return False
    
    def _handle_ability_click(self, position):
        """
        Handle click in ability mode
        
        Args:
            position (tuple): Mouse position
            
        Returns:
            bool: True if handled
        """
        # If placing ability, start targeting
        if self.selected_ability and not self.placing_ability:
            self.placing_ability = True
            self.ability_target_position = position
            
            # Update preview position
            if self.ability_preview:
                self.ability_preview.set_position(position)
                
            return True
            
        return False
    
    def _handle_ability_movement(self, position):
        """
        Handle movement in ability mode
        
        Args:
            position (tuple): Mouse position
            
        Returns:
            bool: True if handled
        """
        # Update ability preview position
        if self.placing_ability and self.ability_preview:
            self.ability_target_position = position
            
            # Get active character for direction vector
            character = self._get_active_character()
            
            if character:
                # Calculate direction vector from character to target
                char_pos = (character.position.x, character.position.y)
                direction = (position[0] - char_pos[0], position[1] - char_pos[1])
                
                # Update preview
                self.ability_preview.set_position(position, direction)
                
            return True
            
        return False
    
    def _handle_ability_release(self, position):
        """
        Handle release in ability mode
        
        Args:
            position (tuple): Mouse position
            
        Returns:
            bool: True if handled
        """
        # Activate ability on release
        if self.placing_ability and self.selected_ability:
            character = self._get_active_character()
            
            if character and hasattr(self.battle_manager, 'aoe_manager'):
                # Calculate direction vector from character to target
                char_pos = (character.position.x, character.position.y)
                direction = (position[0] - char_pos[0], position[1] - char_pos[1])
                
                # Create and activate effect
                effect = self.battle_manager.aoe_manager.create_effect(
                    self.selected_ability, position, direction, character)
                
                if effect:
                    self.battle_manager.aoe_manager.activate_effect(effect)
                    
                    # Log the action
                    if hasattr(self.battle_manager, '_log_message'):
                        self.battle_manager._log_message(
                            f"{character.name} uses {effect.name}")
                    
                    # Reset ability selection
                    self.selected_ability = None
                    self.placing_ability = False
                    self.ability_preview = None
                    
                    return True
        
        # Reset if canceled
        self.placing_ability = False
        self.ability_preview = None
        return False
    
    def _show_tooltip(self, text, position):
        """
        Show tooltip at position
        
        Args:
            text (str): Tooltip text
            position (tuple): Mouse position
        """
        if hasattr(self.battle_manager, 'ui_manager'):
            ui_manager = self.battle_manager.ui_manager
            
            if hasattr(ui_manager, 'set_tooltip'):
                ui_manager.set_tooltip(text)
    
    def _is_position_over_character(self, position, character):
        """
        Check if position is over a character
        
        Args:
            position (tuple): Position to check
            character: Character to check
            
        Returns:
            bool: True if position is over character
        """
        if not hasattr(character, 'position') or not hasattr(character, 'sprite'):
            return False
            
        # Create a rectangle around the character sprite
        char_rect = pygame.Rect(
            character.position.x - character.sprite.get_width() // 2,
            character.position.y - character.sprite.get_height() // 2,
            character.sprite.get_width(),
            character.sprite.get_height()
        )
        
        return char_rect.collidepoint(position)
    
    def _is_position_in_battle_area(self, position):
        """
        Check if position is in the main battle area (not UI panels)
        
        Args:
            position (tuple): Position to check
            
        Returns:
            bool: True if in battle area
        """
        # Simple check - not over any UI buttons
        for button in self.buttons:
            if button["rect"].collidepoint(position):
                return False
                
        # Check mode-specific controls
        if self.current_mode in self.mode_controls:
            for control in self.mode_controls[self.current_mode]:
                if control["rect"].collidepoint(position):
                    return False
        
        return True
    
    def update(self, delta_time):
        """
        Update the tactical UI
        
        Args:
            delta_time (float): Time since last update
        """
        if not self.active:
            return
            
        # Update ability preview if active
        if self.placing_ability and self.ability_preview:
            # Update preview position based on mouse
            mouse_pos = pygame.mouse.get_pos()
            self._handle_ability_movement(mouse_pos)
    
    def render(self, screen):
        """
        Render the tactical UI
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        if not self.active:
            return
            
        # Render mode panels and buttons
        self._render_ui_panels(screen)
        
        # Render mode-specific elements
        if self.current_mode == "movement":
            self._render_movement_ui(screen)
        elif self.current_mode == "formation":
            self._render_formation_ui(screen)
        elif self.current_mode == "ability":
            self._render_ability_ui(screen)
        
        # Render active character indicator
        self._render_active_character_indicator(screen)
        
        # Render ability preview if placing an ability
        if self.placing_ability and self.ability_preview:
            self.ability_preview.render(screen)
    
    def _render_ui_panels(self, screen):
        """
        Render UI panels and buttons
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Bottom panel background
        if hasattr(self.battle_manager, 'screen_width'):
            screen_width = self.battle_manager.screen_width
            screen_height = self.battle_manager.screen_height
        else:
            screen_width = 1024
            screen_height = 768
            
        # Draw bottom panel
        panel_height = 40
        panel_rect = pygame.Rect(0, screen_height - panel_height, screen_width, panel_height)
        
        # Semi-transparent panel
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((30, 30, 40, 200))  # Dark blue with alpha
        screen.blit(panel_surface, panel_rect)
        
        # Right panel if in a mode with controls
        if self.current_mode in self.mode_controls and self.mode_controls[self.current_mode]:
            panel_width = 210
            right_panel_rect = pygame.Rect(
                screen_width - panel_width, 40, 
                panel_width, screen_height - 40 - panel_height)
            
            # Semi-transparent panel
            right_panel_surface = pygame.Surface((right_panel_rect.width, right_panel_rect.height), pygame.SRCALPHA)
            right_panel_surface.fill((30, 30, 40, 180))  # Dark blue with alpha
            screen.blit(right_panel_surface, right_panel_rect)
            
            # Panel title
            title_text = self.current_mode.capitalize()
            title_surface = self.fonts["medium"].render(title_text, True, (255, 255, 255))
            screen.blit(title_surface, (right_panel_rect.x + 10, right_panel_rect.y + 10))
        
        # Draw all buttons
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons:
            # Check if button is for current mode
            highlight = False
            
            if "text" in button:
                # Highlight current mode button
                if button["text"].lower() == self.current_mode:
                    highlight = True
                    
            # Check for hover
            hover = button["rect"].collidepoint(mouse_pos)
            
            # Button color based on state
            if highlight:
                color = (0, 150, 200)
            elif hover:
                color = (100, 100, 150)
            else:
                color = (60, 60, 80)
            
            # Draw button
            pygame.draw.rect(screen, color, button["rect"], 0, 5)
            pygame.draw.rect(screen, (200, 200, 220), button["rect"], 1, 5)
            
            # Draw button text
            if "text" in button:
                text_surface = self.fonts["small"].render(button["text"], True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=button["rect"].center)
                screen.blit(text_surface, text_rect)
        
        # Draw mode-specific controls
        if self.current_mode in self.mode_controls:
            for control in self.mode_controls[self.current_mode]:
                # Check for hover
                hover = control["rect"].collidepoint(mouse_pos)
                
                # Check if control is selected (for abilities)
                selected = False
                if "ability_id" in control and control["ability_id"] == self.selected_ability:
                    selected = True
                
                # Button color based on state
                if selected:
                    color = (0, 200, 100)
                elif hover:
                    color = (100, 100, 150)
                else:
                    color = (60, 60, 80)
                
                # Draw control
                pygame.draw.rect(screen, color, control["rect"], 0, 5)
                pygame.draw.rect(screen, (200, 200, 220), control["rect"], 1, 5)
                
                # Draw control text
                if "text" in control:
                    text_surface = self.fonts["small"].render(control["text"], True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=control["rect"].center)
                    screen.blit(text_surface, text_rect)
    
    def _render_movement_ui(self, screen):
        """
        Render movement mode UI
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Get active character
        character = self._get_active_character()
        if not character:
            return
            
        # Show movement range if debug is on
        if self.show_ranges and hasattr(character, 'movement_speed'):
            # Calculate movement range
            move_range = character.movement_speed * 3  # Movement speed * 3 seconds
            
            # Draw circle for movement range
            range_surface = pygame.Surface((move_range * 2, move_range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (0, 255, 0, 50), (move_range, move_range), move_range)
            screen.blit(range_surface, (character.position.x - move_range, character.position.y - move_range))
            
            # Draw circle for attack range
            attack_range = getattr(character, 'attack_range', 100)
            range_surface = pygame.Surface((attack_range * 2, attack_range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (255, 0, 0, 50), (attack_range, attack_range), attack_range)
            screen.blit(range_surface, (character.position.x - attack_range, character.position.y - attack_range))
    
    def _render_formation_ui(self, screen):
        """
        Render formation mode UI
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Draw current formation preview
        if hasattr(self.battle_manager, 'formation_system'):
            # Get formation positions
            formation_system = self.battle_manager.formation_system
            positions = formation_system.get_formation_positions()
            
            # Draw lines connecting positions
            if len(positions) > 1:
                pygame.draw.lines(screen, (0, 200, 0), True, 
                                [(p.x, p.y) for p in positions], 2)
            
            # Draw position markers
            for pos in positions:
                pygame.draw.circle(screen, (0, 200, 0), (int(pos.x), int(pos.y)), 10, 1)
            
            # Draw formation center
            pygame.draw.circle(screen, (0, 200, 0), 
                             (int(formation_system.formation_center.x), 
                              int(formation_system.formation_center.y)), 
                             5)
            
            # Draw current formation name
            formation_name = formation_system.current_formation
            text_surface = self.fonts["medium"].render(f"Formation: {formation_name}", True, (0, 200, 0))
            
            if hasattr(self.battle_manager, 'screen_width'):
                screen_width = self.battle_manager.screen_width
                screen_height = self.battle_manager.screen_height
            else:
                screen_width = 1024
                screen_height = 768
                
            text_rect = text_surface.get_rect(center=(screen_width // 2, 70))
            screen.blit(text_surface, text_rect)
            
            # Draw formation description
            description = formation_system.get_formation_description()
            if description:
                desc_surface = self.fonts["small"].render(description, True, (0, 200, 0))
                desc_rect = desc_surface.get_rect(center=(screen_width // 2, 90))
                screen.blit(desc_surface, desc_rect)
    
    def _render_ability_ui(self, screen):
        """
        Render ability mode UI
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Draw ability targeting info
        if self.selected_ability:
            # Get ability description
            ability_name = self.selected_ability.capitalize()
            
            # Draw targeting instructions
            text = f"Click to place {ability_name}"
            text_surface = self.fonts["medium"].render(text, True, (255, 255, 0))
            
            if hasattr(self.battle_manager, 'screen_width'):
                screen_width = self.battle_manager.screen_width
            else:
                screen_width = 1024
                
            text_rect = text_surface.get_rect(center=(screen_width // 2, 70))
            screen.blit(text_surface, text_rect)
    
    def _render_active_character_indicator(self, screen):
        """
        Render indicator for active character
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Get active character
        character = self._get_active_character()
        if not character:
            return
            
        # Draw arrow above character
        arrow_points = [
            (character.position.x, character.position.y - 50),
            (character.position.x - 10, character.position.y - 40),
            (character.position.x + 10, character.position.y - 40)
        ]
        
        pygame.draw.polygon(screen, (255, 255, 0), arrow_points)
        
        # Draw character name
        text_surface = self.fonts["small"].render(f"Active: {character.name}", True, (255, 255, 0))
        text_rect = text_surface.get_rect(center=(character.position.x, character.position.y - 60))
        screen.blit(text_surface, text_rect)