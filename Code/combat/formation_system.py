"""
Combat Formations - Manages party positioning and formations
"""
import math
import pygame
from combat.combat_state import CombatState
from game.config import MAX_PARTY_SIZE

class FormationType:
    """Formation types available to the party"""
    LINE = "line"           # Characters in a horizontal line
    TRIANGLE = "triangle"   # Triangle formation (tank forward, others back)
    COLUMN = "column"       # Characters in a vertical column
    SPREAD = "spread"       # Characters spread out
    CIRCLE = "circle"       # Characters in a circle
    FLANK = "flank"         # Two characters flank one in the center
    WEDGE = "wedge"         # Inverted V formation (charge formation)
    DIAGONAL = "diagonal"   # Diagonal line

class FormationSystem:
    """
    Manages party formations and positioning
    """
    def __init__(self, battle_manager):
        """
        Initialize the formation system
        
        Args:
            battle_manager: Reference to the battle manager
        """
        self.battle_manager = battle_manager
        self.movement_controller = getattr(battle_manager, 'movement_controller', None)
        
        # Formation parameters
        self.current_formation = FormationType.LINE
        self.formation_center = pygame.Vector2(0, 0)
        self.formation_spacing = 120
        self.formation_rotation = 0  # Degrees
        self.formation_scale = 1.0
        
        # Formation descriptions
        self.formation_descriptions = {
            FormationType.LINE: "Characters form a horizontal line, good for wide coverage",
            FormationType.TRIANGLE: "Tank at front with support characters behind, good for defense",
            FormationType.COLUMN: "Characters in a vertical column, good for narrow passages",
            FormationType.SPREAD: "Characters spread out to avoid AoE attacks",
            FormationType.CIRCLE: "Characters form a circle, good for 360° defense",
            FormationType.FLANK: "Two characters flank one in the center, good for pincer attacks",
            FormationType.WEDGE: "Characters form an inverted V, good for charges",
            FormationType.DIAGONAL: "Characters form a diagonal line, good for approach"
        }
        
        # Battle state tracking
        self.currently_moving = False
        self.move_targets = {}  # Character -> target position
        self.move_complete_callbacks = {}  # Character -> callback
    
    def get_formation_positions(self, formation_type=None, center=None, 
                               rotation=None, spacing=None, scale=None):
        """
        Calculate positions for a given formation
        
        Args:
            formation_type (str, optional): Formation type or None for current
            center (pygame.Vector2, optional): Center position or None for current
            rotation (float, optional): Rotation in degrees or None for current
            spacing (float, optional): Spacing between characters or None for current
            scale (float, optional): Formation scale or None for current
            
        Returns:
            list: List of positions for each party member
        """
        # Use current values if not specified
        if formation_type is None:
            formation_type = self.current_formation
        if center is None:
            center = self.formation_center
        if rotation is None:
            rotation = self.formation_rotation
        if spacing is None:
            spacing = self.formation_spacing
        if scale is None:
            scale = self.formation_scale
        
        # Get party members
        party = self.battle_manager.game_state.party
        active_members = [char for char in party if char and char.is_alive()]
        member_count = len(active_members)
        
        # Position offsets based on formation type
        positions = []
        
        if formation_type == FormationType.LINE:
            # Horizontal line
            for i in range(member_count):
                offset_x = (i - (member_count - 1) / 2) * spacing
                positions.append(pygame.Vector2(offset_x, 0))
        
        elif formation_type == FormationType.TRIANGLE:
            if member_count == 1:
                positions.append(pygame.Vector2(0, 0))
            elif member_count == 2:
                positions.append(pygame.Vector2(0, -spacing/2))  # Front
                positions.append(pygame.Vector2(0, spacing/2))   # Back
            else:
                # Front position
                positions.append(pygame.Vector2(0, -spacing/2))
                
                # Back positions
                back_count = member_count - 1
                for i in range(back_count):
                    offset_x = (i - (back_count - 1) / 2) * spacing
                    positions.append(pygame.Vector2(offset_x, spacing/2))
        
        elif formation_type == FormationType.COLUMN:
            # Vertical column
            for i in range(member_count):
                offset_y = (i - (member_count - 1) / 2) * spacing
                positions.append(pygame.Vector2(0, offset_y))
        
        elif formation_type == FormationType.SPREAD:
            # Spread in a wider pattern
            if member_count == 1:
                positions.append(pygame.Vector2(0, 0))
            elif member_count == 2:
                positions.append(pygame.Vector2(-spacing/2, -spacing/2))
                positions.append(pygame.Vector2(spacing/2, spacing/2))
            elif member_count == 3:
                positions.append(pygame.Vector2(-spacing, 0))
                positions.append(pygame.Vector2(0, 0))
                positions.append(pygame.Vector2(spacing, 0))
            else:
                # Form a square or rectangle
                for i in range(member_count):
                    row = i // 2
                    col = i % 2
                    offset_x = (col - 0.5) * spacing * 1.5
                    offset_y = (row - ((member_count-1) // 2) / 2) * spacing
                    positions.append(pygame.Vector2(offset_x, offset_y))
        
        elif formation_type == FormationType.CIRCLE:
            # Circle formation
            radius = spacing / 2
            for i in range(member_count):
                angle = 2 * math.pi * i / member_count
                offset_x = math.cos(angle) * radius
                offset_y = math.sin(angle) * radius
                positions.append(pygame.Vector2(offset_x, offset_y))
        
        elif formation_type == FormationType.FLANK:
            # Flanking formation
            if member_count == 1:
                positions.append(pygame.Vector2(0, 0))
            elif member_count == 2:
                positions.append(pygame.Vector2(-spacing/2, 0))
                positions.append(pygame.Vector2(spacing/2, 0))
            else:
                # Center position
                positions.append(pygame.Vector2(0, 0))
                
                # Flank positions
                flank_count = member_count - 1
                flank_spacing = spacing * 1.2  # Wider spacing for flanks
                for i in range(flank_count):
                    side = 1 if i % 2 == 0 else -1
                    offset_x = side * flank_spacing
                    offset_y = -spacing/3 if i < flank_count/2 else spacing/3
                    positions.append(pygame.Vector2(offset_x, offset_y))
        
        elif formation_type == FormationType.WEDGE:
            # Inverted V formation (charge formation)
            if member_count == 1:
                positions.append(pygame.Vector2(0, 0))
            elif member_count == 2:
                positions.append(pygame.Vector2(-spacing/3, -spacing/3))
                positions.append(pygame.Vector2(spacing/3, -spacing/3))
            else:
                # Point of the wedge
                positions.append(pygame.Vector2(0, -spacing/2))
                
                # Wings of the wedge
                wing_count = member_count - 1
                for i in range(wing_count):
                    side = 1 if i % 2 == 0 else -1
                    offset_x = side * spacing * (i//2 + 1) / 2
                    offset_y = spacing * (i//2 + 1) / 3
                    positions.append(pygame.Vector2(offset_x, offset_y))
        
        elif formation_type == FormationType.DIAGONAL:
            # Diagonal line
            for i in range(member_count):
                offset_x = (i - (member_count - 1) / 2) * spacing / 2
                offset_y = (i - (member_count - 1) / 2) * spacing / 2
                positions.append(pygame.Vector2(offset_x, offset_y))
        
        else:
            # Default to line formation
            for i in range(member_count):
                offset_x = (i - (member_count - 1) / 2) * spacing
                positions.append(pygame.Vector2(offset_x, 0))
        
        # Apply rotation, scale, and center offset
        rotation_rad = math.radians(rotation)
        result = []
        
        for pos in positions:
            # Apply scale
            scaled_pos = pygame.Vector2(pos.x * scale, pos.y * scale)
            
            # Apply rotation
            rotated_x = scaled_pos.x * math.cos(rotation_rad) - scaled_pos.y * math.sin(rotation_rad)
            rotated_y = scaled_pos.x * math.sin(rotation_rad) + scaled_pos.y * math.cos(rotation_rad)
            
            # Add center offset
            final_pos = pygame.Vector2(center.x + rotated_x, center.y + rotated_y)
            result.append(final_pos)
        
        return result
    
    def apply_formation(self, formation_type=None, center=None, 
                       rotation=None, spacing=None, scale=None):
        """
        Move party members to their formation positions
        
        Args:
            formation_type (str, optional): Formation type or None for current
            center (pygame.Vector2, optional): Center position or None for current
            rotation (float, optional): Rotation in degrees or None for current
            spacing (float, optional): Spacing between characters or None for current
            scale (float, optional): Formation scale or None for current
            
        Returns:
            bool: True if formation change started
        """
        if self.currently_moving:
            return False
            
        # Check if movement controller exists
        if not self.movement_controller:
            return False
        
        # Update formation parameters
        if formation_type is not None:
            self.current_formation = formation_type
        if center is not None:
            self.formation_center = center
        if rotation is not None:
            self.formation_rotation = rotation
        if spacing is not None:
            self.formation_spacing = spacing
        if scale is not None:
            self.formation_scale = scale
        
        # Get party members
        party = self.battle_manager.game_state.party
        active_members = [char for char in party if char and char.is_alive()]
        
        # Calculate formation positions
        positions = self.get_formation_positions()
        
        # Check if we have enough positions
        if len(positions) < len(active_members):
            return False
        
        # Begin movement for each party member
        self.currently_moving = True
        self.move_targets = {}
        self.move_complete_callbacks = {}
        
        for i, char in enumerate(active_members):
            if i >= len(positions):
                break
                
            target_pos = positions[i]
            
            # Check if character is already at position
            current_pos = (char.position.x, char.position.y)
            distance = math.hypot(current_pos[0] - target_pos.x, current_pos[1] - target_pos.y)
            
            if distance < 10:  # Already at position
                continue
                
            # Start movement
            if hasattr(self.battle_manager, 'initiate_movement'):
                # Store target position
                self.move_targets[char] = target_pos
                
                # Create completion callback
                callback = lambda c=char: self._on_formation_move_complete(c)
                self.move_complete_callbacks[char] = callback
                
                # Start movement
                self.battle_manager.initiate_movement(char, (target_pos.x, target_pos.y), callback)
        
        return True
    
    def _on_formation_move_complete(self, character):
        """
        Handle completion of formation movement
        
        Args:
            character: The character that completed movement
        """
        # Remove from tracking
        if character in self.move_targets:
            del self.move_targets[character]
        
        if character in self.move_complete_callbacks:
            del self.move_complete_callbacks[character]
        
        # Check if all movement is complete
        if not self.move_targets:
            self.currently_moving = False
    
    def rotate_formation(self, angle_change):
        """
        Rotate the current formation
        
        Args:
            angle_change (float): Change in rotation angle in degrees
            
        Returns:
            bool: True if rotation started
        """
        new_rotation = self.formation_rotation + angle_change
        return self.apply_formation(rotation=new_rotation)
    
    def face_target(self, target):
        """
        Rotate formation to face a target
        
        Args:
            target: The target to face
            
        Returns:
            bool: True if rotation started
        """
        if not hasattr(target, 'position'):
            return False
            
        # Calculate direction to target
        direction = pygame.Vector2(target.position) - self.formation_center
        
        # Calculate angle in degrees
        angle = math.degrees(math.atan2(direction.y, direction.x))
        
        # Rotate to face target
        return self.apply_formation(rotation=angle)
    
    def adjust_spacing(self, spacing_change):
        """
        Adjust spacing between party members
        
        Args:
            spacing_change (float): Change in spacing
            
        Returns:
            bool: True if spacing change started
        """
        new_spacing = max(50, min(200, self.formation_spacing + spacing_change))
        return self.apply_formation(spacing=new_spacing)
    
    def move_formation(self, target_center):
        """
        Move the entire formation to a new center position
        
        Args:
            target_center (pygame.Vector2): New center position
            
        Returns:
            bool: True if formation move started
        """
        return self.apply_formation(center=target_center)
    
    def get_formation_description(self, formation_type=None):
        """
        Get description of a formation
        
        Args:
            formation_type (str, optional): Formation type or None for current
            
        Returns:
            str: Formation description
        """
        if formation_type is None:
            formation_type = self.current_formation
            
        return self.formation_descriptions.get(
            formation_type, "No description available.")
    
    def update(self, delta_time):
        """
        Update formation system
        
        Args:
            delta_time (float): Time since last update
        """
        # Nothing to update in the base implementation
        pass
    
    def render(self, screen):
        """
        Render formation visualizations (for debugging)
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        # Only render in debug mode
        if not getattr(self.movement_controller, 'debug_render', False):
            return
            
        # Render formation center
        center = (int(self.formation_center.x), int(self.formation_center.y))
        pygame.draw.circle(screen, (0, 255, 255), center, 5, 2)
        
        # Render formation positions
        positions = self.get_formation_positions()
        for pos in positions:
            pos_tuple = (int(pos.x), int(pos.y))
            pygame.draw.circle(screen, (0, 255, 255), pos_tuple, 10, 1)
            
        # Render name of current formation
        font = pygame.font.SysFont("Arial", 16)
        text = font.render(f"Formation: {self.current_formation}", True, (0, 255, 255))
        screen.blit(text, (10, 50))
