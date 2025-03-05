"""
Cover System - Provides cover mechanics for spatial combat
"""
import pygame
import math
import random
from combat.combat_grid import CellType
from combat.combat_state import CombatState

class CoverType:
    """Types of cover provided by the environment"""
    NONE = "none"            # No cover
    HALF = "half"            # Half cover (+2 AC, Dex save advantage)
    THREE_QUARTERS = "3/4"   # Three-quarters cover (+5 AC, Dex save advantage)
    FULL = "full"            # Full cover (can't be targeted directly)

class CoverSystem:
    """
    Manages cover mechanics for combat
    """
    def __init__(self, battle_manager):
        """
        Initialize the cover system
        
        Args:
            battle_manager: Reference to the battle manager
        """
        self.battle_manager = battle_manager
        self.movement_controller = getattr(battle_manager, 'movement_controller', None)
        
        # Cover status tracking
        self.entity_cover = {}  # Entity -> (cover_type, cover_direction, source_cell)
        
        # Cover modifiers
        self.cover_modifiers = {
            CoverType.NONE: {
                'damage_reduction': 0.0,      # No damage reduction
                'hit_penalty': 0,            # No hit penalty
                'evasion_bonus': 0.0,        # No evasion bonus
            },
            CoverType.HALF: {
                'damage_reduction': 0.25,    # 25% damage reduction
                'hit_penalty': 2,            # -2 to hit (AC +2)
                'evasion_bonus': 0.1,        # +10% chance to evade
            },
            CoverType.THREE_QUARTERS: {
                'damage_reduction': 0.5,     # 50% damage reduction
                'hit_penalty': 5,            # -5 to hit (AC +5)
                'evasion_bonus': 0.2,        # +20% chance to evade
            },
            CoverType.FULL: {
                'damage_reduction': 1.0,     # 100% damage reduction
                'hit_penalty': 1000,         # Can't be hit
                'evasion_bonus': 1.0,        # 100% chance to evade
            }
        }
        
        # Environment objects that provide cover
        self.cover_objects = []  # (x, y, width, height, cover_type)
    
    def add_cover_object(self, x, y, width, height, cover_type=CoverType.HALF):
        """
        Add a cover object to the environment
        
        Args:
            x (int): X position
            y (int): Y position
            width (int): Width of cover object
            height (int): Height of cover object
            cover_type (str): Type of cover provided
            
        Returns:
            int: ID of the cover object
        """
        # Add cover object
        self.cover_objects.append((x, y, width, height, cover_type))
        
        # Add cover cells to grid if available
        if self.movement_controller:
            grid = self.movement_controller.combat_grid
            
            # Calculate grid cells covered by this object
            top_left = grid.get_cell_coords((x, y))
            bottom_right = grid.get_cell_coords((x + width, y + height))
            
            # Set cells to obstacles or cover
            for row in range(top_left[0], bottom_right[0] + 1):
                for col in range(top_left[1], bottom_right[1] + 1):
                    if cover_type == CoverType.FULL:
                        grid.set_cell_type((row, col), CellType.OBSTACLE)
                    else:
                        grid.set_cell_type((row, col), CellType.COVER)
        
        return len(self.cover_objects) - 1
    
    def remove_cover_object(self, cover_id):
        """
        Remove a cover object
        
        Args:
            cover_id (int): ID of the cover object
            
        Returns:
            bool: True if removed
        """
        if 0 <= cover_id < len(self.cover_objects):
            # Get cover object
            cover = self.cover_objects[cover_id]
            
            # Remove cover cells from grid if available
            if self.movement_controller:
                grid = self.movement_controller.combat_grid
                
                # Calculate grid cells covered by this object
                top_left = grid.get_cell_coords((cover[0], cover[1]))
                bottom_right = grid.get_cell_coords((cover[0] + cover[2], cover[1] + cover[3]))
                
                # Reset cells to empty
                for row in range(top_left[0], bottom_right[0] + 1):
                    for col in range(top_left[1], bottom_right[1] + 1):
                        grid.set_cell_type((row, col), CellType.EMPTY)
            
            # Remove cover object
            self.cover_objects.pop(cover_id)
            return True
            
        return False
    
    def generate_random_cover(self, count=5, min_size=40, max_size=120):
        """
        Generate random cover objects in the environment
        
        Args:
            count (int): Number of cover objects to generate
            min_size (int): Minimum size of cover objects
            max_size (int): Maximum size of cover objects
            
        Returns:
            int: Number of cover objects created
        """
        if not self.movement_controller:
            return 0
            
        grid = self.movement_controller.combat_grid
        screen_width = grid.width
        screen_height = grid.height
        
        # Create cover objects
        cover_count = 0
        for _ in range(count):
            # Random size
            width = random.randint(min_size, max_size)
            height = random.randint(min_size, max_size)
            
            # Random position (avoiding edges)
            x = random.randint(50, screen_width - width - 50)
            y = random.randint(50, screen_height - height - 50)
            
            # Random cover type (weighted towards half cover)
            cover_type_roll = random.random()
            if cover_type_roll < 0.7:
                cover_type = CoverType.HALF
            elif cover_type_roll < 0.9:
                cover_type = CoverType.THREE_QUARTERS
            else:
                cover_type = CoverType.FULL
            
            # Add cover object
            self.add_cover_object(x, y, width, height, cover_type)
            cover_count += 1
        
        return cover_count
    
    def update_entity_cover_status(self, entity, target=None):
        """
        Update an entity's cover status
        
        Args:
            entity: The entity to update
            target: Target to check cover against or None for general cover
            
        Returns:
            str: Cover type (CoverType constant)
        """
        if not entity or not hasattr(entity, 'position'):
            return CoverType.NONE
            
        # If no target, check general cover
        if not target or not hasattr(target, 'position'):
            # Check if entity is in a cover cell
            if self.movement_controller:
                grid = self.movement_controller.combat_grid
                cell_coords = grid.get_cell_coords((entity.position.x, entity.position.y))
                
                if grid.is_valid_cell(cell_coords):
                    cell_type = grid.get_cell_type(cell_coords)
                    if cell_type == CellType.COVER:
                        # Entity is in a cover cell, check cover objects
                        for cover in self.cover_objects:
                            x, y, width, height, cover_type = cover
                            if (x <= entity.position.x <= x + width and 
                                y <= entity.position.y <= y + height):
                                
                                # Store cover info
                                self.entity_cover[entity] = (cover_type, None, cell_coords)
                                return cover_type
            
            # No cover
            if entity in self.entity_cover:
                del self.entity_cover[entity]
            return CoverType.NONE
        
        # With a target, check line of sight and cover
        entity_pos = pygame.Vector2(entity.position)
        target_pos = pygame.Vector2(target.position)
        
        # Direction from entity to target
        direction = target_pos - entity_pos
        distance = direction.length()
        
        if distance < 1:
            return CoverType.NONE
            
        direction = direction.normalize()
        
        # Check if entity is using a cover object
        best_cover = CoverType.NONE
        best_cover_distance = float('inf')
        
        for cover in self.cover_objects:
            x, y, width, height, cover_type = cover
            
            # Check if entity is near cover
            entity_near_cover = False
            
            # Check all 4 edges of the cover object
            edges = [
                ((x, y), (x + width, y)),           # Top edge
                ((x, y + height), (x + width, y + height)),  # Bottom edge
                ((x, y), (x, y + height)),          # Left edge
                ((x + width, y), (x + width, y + height))    # Right edge
            ]
            
            for edge_start, edge_end in edges:
                # Calculate distance from entity to this edge
                dist = self._point_to_segment_distance(
                    (entity_pos.x, entity_pos.y), edge_start, edge_end)
                
                if dist < 30:  # Within 30 pixels of the edge
                    entity_near_cover = True
                    
                    # Calculate if the cover is between entity and target
                    cover_center = pygame.Vector2(x + width/2, y + height/2)
                    entity_to_cover = cover_center - entity_pos
                    entity_to_target = target_pos - entity_pos
                    
                    # Check if angles are similar (cover is roughly in the same direction as target)
                    angle_diff = self._angle_between(entity_to_cover, entity_to_target)
                    
                    if angle_diff < 0.5 * math.pi:  # Less than 90 degrees difference
                        # Check distance to cover
                        cover_distance = entity_to_cover.length()
                        
                        if cover_distance < best_cover_distance:
                            best_cover = cover_type
                            best_cover_distance = cover_distance
            
            # Store cover info
            if best_cover != CoverType.NONE:
                # Direction of cover (from entity to target)
                cover_direction = direction
                
                # Cell coords if using grid
                cell_coords = None
                if self.movement_controller:
                    grid = self.movement_controller.combat_grid
                    cell_coords = grid.get_cell_coords((entity_pos.x, entity_pos.y))
                
                self.entity_cover[entity] = (best_cover, cover_direction, cell_coords)
                return best_cover
        
        # No cover
        if entity in self.entity_cover:
            del self.entity_cover[entity]
            
        return CoverType.NONE
    
    def get_entity_cover_against(self, entity, target):
        """
        Get an entity's cover status against a specific target
        
        Args:
            entity: The entity checking for cover
            target: The target entity
            
        Returns:
            str: Cover type (CoverType constant)
        """
        return self.update_entity_cover_status(entity, target)
    
    def get_cover_modifier(self, entity, target, modifier_type):
        """
        Get a cover modifier for an entity against a target
        
        Args:
            entity: The entity with cover
            target: The target entity
            modifier_type (str): Type of modifier to get ('damage_reduction', 'hit_penalty', 'evasion_bonus')
            
        Returns:
            float or int: Modifier value
        """
        cover_type = self.get_entity_cover_against(entity, target)
        modifiers = self.cover_modifiers.get(cover_type, self.cover_modifiers[CoverType.NONE])
        return modifiers.get(modifier_type, 0)
    
    def is_in_cover_stance(self, entity):
        """
        Check if entity is actively using cover
        
        Args:
            entity: The entity to check
            
        Returns:
            bool: True if in cover stance
        """
        return entity.combat_state == CombatState.TAKING_COVER
    
    def take_cover(self, entity):
        """
        Make an entity take cover
        
        Args:
            entity: The entity taking cover
            
        Returns:
            bool: True if successful
        """
        if not entity.is_alive() or entity.combat_state != CombatState.IDLE:
            return False
            
        # Check if entity is near cover
        cover_type = self.update_entity_cover_status(entity)
        if cover_type == CoverType.NONE:
            return False
            
        # Update entity state
        entity.combat_state = CombatState.TAKING_COVER
        entity.state_start_time = pygame.time.get_ticks() / 1000.0
        
        return True
    
    def find_nearest_cover(self, entity, max_distance=200):
        """
        Find the nearest cover position for an entity
        
        Args:
            entity: The entity looking for cover
            max_distance (float): Maximum search distance
            
        Returns:
            tuple: (x, y) cover position or None if no cover found
        """
        if not entity or not hasattr(entity, 'position'):
            return None
            
        entity_pos = pygame.Vector2(entity.position)
        best_cover_pos = None
        best_cover_dist = float('inf')
        
        # Check cover objects
        for cover in self.cover_objects:
            x, y, width, height, cover_type = cover
            
            # Skip full cover (obstacles)
            if cover_type == CoverType.FULL:
                continue
                
            # Check all 4 edges of the cover object
            edges = [
                ((x, y), (x + width, y)),           # Top edge
                ((x, y + height), (x + width, y + height)),  # Bottom edge
                ((x, y), (x, y + height)),          # Left edge
                ((x + width, y), (x + width, y + height))    # Right edge
            ]
            
            for edge_start, edge_end in edges:
                # Sample points along the edge
                steps = max(2, int(math.hypot(edge_end[0] - edge_start[0], edge_end[1] - edge_start[1]) / 20))
                for i in range(steps):
                    t = i / (steps - 1)
                    sample_x = edge_start[0] + t * (edge_end[0] - edge_start[0])
                    sample_y = edge_start[1] + t * (edge_end[1] - edge_start[1])
                    
                    # Check if position is valid
                    if self.movement_controller:
                        grid = self.movement_controller.combat_grid
                        if not grid.is_position_free((sample_x, sample_y)):
                            continue
                    
                    # Calculate distance
                    dist = math.hypot(sample_x - entity_pos.x, sample_y - entity_pos.y)
                    
                    if dist < max_distance and dist < best_cover_dist:
                        best_cover_pos = (sample_x, sample_y)
                        best_cover_dist = dist
        
        return best_cover_pos
    
    def break_cover(self, entity):
        """
        Make an entity break cover
        
        Args:
            entity: The entity breaking cover
            
        Returns:
            bool: True if successful
        """
        if not entity.is_alive() or entity.combat_state != CombatState.TAKING_COVER:
            return False
            
        # Update entity state
        entity.combat_state = CombatState.IDLE
        entity.state_start_time = pygame.time.get_ticks() / 1000.0
        
        return True
    
    def update(self, delta_time):
        """
        Update cover status for all entities
        
        Args:
            delta_time (float): Time since last update
        """
        # Nothing to update in the base implementation
        pass
    
    def render(self, screen):
        """
        Render cover objects and debug visualizations
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        # Only render in debug mode
        if not getattr(self.movement_controller, 'debug_render', False):
            return
        
        # Render cover objects
        for cover in self.cover_objects:
            x, y, width, height, cover_type = cover
            
            # Different colors for different cover types
            if cover_type == CoverType.HALF:
                color = (0, 150, 0, 128)  # Light green
            elif cover_type == CoverType.THREE_QUARTERS:
                color = (0, 100, 0, 128)  # Medium green
            else:  # FULL
                color = (0, 50, 0, 128)   # Dark green
            
            # Create semi-transparent surface
            cover_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            cover_surface.fill(color)
            screen.blit(cover_surface, (x, y))
            
            # Draw border
            pygame.draw.rect(screen, (0, 255, 0), (x, y, width, height), 1)
        
        # Render entity cover status
        font = pygame.font.SysFont("Arial", 12)
        for entity, (cover_type, direction, _) in self.entity_cover.items():
            if hasattr(entity, 'position'):
                text = font.render(f"Cover: {cover_type}", True, (0, 255, 0))
                screen.blit(text, (entity.position.x - text.get_width() // 2, 
                                 entity.position.y - 40))
                
                # Draw cover direction if available
                if direction:
                    start_pos = (entity.position.x, entity.position.y)
                    end_pos = (entity.position.x + direction.x * 30, 
                              entity.position.y + direction.y * 30)
                    pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 2)
    
    def _point_to_segment_distance(self, point, segment_start, segment_end):
        """
        Calculate the distance from a point to a line segment
        
        Args:
            point (tuple): (x, y) point
            segment_start (tuple): (x, y) start of line segment
            segment_end (tuple): (x, y) end of line segment
            
        Returns:
            float: Distance from point to line segment
        """
        px, py = point
        x1, y1 = segment_start
        x2, y2 = segment_end
        
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            # Segment is a point
            return math.hypot(px - x1, py - y1)
        
        # Calculate projection
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        
        if t < 0:
            # Point is closest to start of segment
            return math.hypot(px - x1, py - y1)
        elif t > 1:
            # Point is closest to end of segment
            return math.hypot(px - x2, py - y2)
        else:
            # Point is closest to middle of segment
            return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
    
    def _angle_between(self, v1, v2):
        """
        Calculate the angle between two vectors
        
        Args:
            v1 (pygame.Vector2): First vector
            v2 (pygame.Vector2): Second vector
            
        Returns:
            float: Angle in radians
        """
        if v1.length() == 0 or v2.length() == 0:
            return 0
            
        v1_normalized = v1.normalize()
        v2_normalized = v2.normalize()
        
        dot = v1_normalized.dot(v2_normalized)
        # Clamp dot product to [-1, 1] to avoid numerical issues
        dot = max(-1.0, min(1.0, dot))
        
        return math.acos(dot)
