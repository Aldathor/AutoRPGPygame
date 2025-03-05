"""
Movement Controller - Manages entity movement using pathfinding and combat grid
"""
import pygame
import math
import time
from combat.combat_grid import CombatGrid
from combat.pathfinding import AStar

class MovementController:
    """
    Controls the movement of entities in combat using a grid and pathfinding
    """
    def __init__(self, screen_width, screen_height, cell_size=40):
        """
        Initialize the movement controller
        
        Args:
            screen_width (int): Width of the screen in pixels
            screen_height (int): Height of the screen in pixels
            cell_size (int): Size of each grid cell in pixels
        """
        self.combat_grid = CombatGrid(screen_width, screen_height, cell_size)
        self.pathfinder = AStar(self.combat_grid)
        
        # Entity tracking
        self.moving_entities = {}  # entity -> {path, target, speed, current_waypoint}
        
        # Debug visualization
        self.debug_render = False
    
    def register_entity(self, entity, position=None):
        """
        Register an entity with the movement controller
        
        Args:
            entity (BaseCharacter): Entity to register
            position (tuple, optional): Initial position or None to use entity.position
            
        Returns:
            bool: True if successful
        """
        if position is None:
            position = (entity.position.x, entity.position.y)
        
        # Try to find a valid position nearby if the exact one is occupied
        if not self.combat_grid.is_position_free(position):
            alternative_position = self.combat_grid.get_nearest_free_position(position)
            if alternative_position:
                position = alternative_position
            else:
                return False
        
        return self.combat_grid.register_entity(entity, position)
    
    def remove_entity(self, entity):
        """
        Remove an entity from the movement controller
        
        Args:
            entity (BaseCharacter): Entity to remove
            
        Returns:
            bool: True if removed
        """
        # Cancel any movement
        if entity in self.moving_entities:
            del self.moving_entities[entity]
        
        return self.combat_grid.remove_entity(entity)
    
    def start_movement(self, entity, target_position, speed=None, use_pathfinding=True):
        """
        Start moving an entity to a target position
        
        Args:
            entity (BaseCharacter): Entity to move
            target_position (tuple): (x, y) target position
            speed (float, optional): Movement speed or None to use entity.movement_speed
            use_pathfinding (bool): Whether to use pathfinding or direct movement
            
        Returns:
            bool: True if movement started
        """
        if entity not in self.combat_grid.entity_positions:
            # Entity needs to be registered first
            if not self.register_entity(entity):
                return False
        
        # Use entity's speed if none provided
        if speed is None:
            speed = getattr(entity, 'movement_speed', 100)
        
        # Current entity position
        current_position = (entity.position.x, entity.position.y)
        
        if use_pathfinding:
            # Find path to target
            path = self.pathfinder.find_path(current_position, target_position)
            
            if not path:
                # Try to find a nearby free position if the exact target is occupied
                if not self.combat_grid.is_position_free(target_position):
                    alt_position = self.combat_grid.get_nearest_free_position(target_position)
                    if alt_position:
                        path = self.pathfinder.find_path(current_position, alt_position)
                
                # If still no path, fail
                if not path:
                    return False
            
            # Simplify the path to remove unnecessary waypoints
            path = self.pathfinder.simplify_path(path)
        else:
            # Direct movement without pathfinding
            path = [current_position, target_position]
        
        # Store movement data
        self.moving_entities[entity] = {
            'path': path,
            'target': target_position,
            'speed': speed,
            'start_time': time.time(),
            'current_waypoint': 0,
            'next_position': None
        }
        
        # Update entity state
        entity.is_moving = True
        entity.target_position = pygame.Vector2(target_position)
        
        return True
    
    def move_towards_entity(self, mover, target_entity, preferred_distance=None, speed=None):
        """
        Move towards another entity, stopping at a preferred distance
        
        Args:
            mover (BaseCharacter): Entity that will move
            target_entity (BaseCharacter): Entity to move towards
            preferred_distance (float, optional): Preferred distance to maintain
            speed (float, optional): Movement speed
            
        Returns:
            bool: True if movement started
        """
        if target_entity not in self.combat_grid.entity_positions:
            return False
        
        # Default preferred distance to attack range if not specified
        if preferred_distance is None:
            preferred_distance = getattr(mover, 'attack_range', 60)
            # Convert to grid cells (approximate)
            preferred_distance_cells = max(1, int(preferred_distance / self.combat_grid.cell_size))
        else:
            preferred_distance_cells = max(1, int(preferred_distance / self.combat_grid.cell_size))
        
        # Find path to a cell near the target
        current_position = (mover.position.x, mover.position.y)
        path = self.pathfinder.find_path_to_nearest_cell_to_target(
            current_position, target_entity, preferred_distance_cells)
        
        if not path:
            return False
        
        # Store movement data
        self.moving_entities[mover] = {
            'path': path,
            'target': path[-1],  # Last point in path
            'speed': speed if speed is not None else getattr(mover, 'movement_speed', 100),
            'start_time': time.time(),
            'current_waypoint': 0,
            'next_position': None
        }
        
        # Update entity state
        mover.is_moving = True
        mover.target_position = pygame.Vector2(path[-1])
        
        return True
    
    def stop_movement(self, entity):
        """
        Stop an entity's movement
        
        Args:
            entity (BaseCharacter): Entity to stop
            
        Returns:
            bool: True if entity was moving
        """
        if entity in self.moving_entities:
            del self.moving_entities[entity]
            entity.is_moving = False
            return True
        return False
    
    def is_entity_moving(self, entity):
        """
        Check if an entity is currently moving
        
        Args:
            entity (BaseCharacter): Entity to check
            
        Returns:
            bool: True if entity is moving
        """
        return entity in self.moving_entities
    
    def is_entity_at_target(self, entity):
        """
        Check if an entity has reached its target position
        
        Args:
            entity (BaseCharacter): Entity to check
            
        Returns:
            bool: True if entity is at target
        """
        if entity not in self.moving_entities:
            return False
        
        movement_data = self.moving_entities[entity]
        current_position = (entity.position.x, entity.position.y)
        target_position = movement_data['target']
        
        # Calculate distance to target
        dx = target_position[0] - current_position[0]
        dy = target_position[1] - current_position[1]
        distance = math.hypot(dx, dy)
        
        # Check if close enough to target (within half a cell)
        return distance < self.combat_grid.cell_size / 2
    
    def update(self, delta_time):
        """
        Update entity movement
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Process each moving entity
        entities_to_remove = []
        
        for entity, movement_data in self.moving_entities.items():
            if not entity.is_alive():
                entities_to_remove.append(entity)
                continue
            
            path = movement_data['path']
            speed = movement_data['speed']
            current_position = (entity.position.x, entity.position.y)
            
            # Calculate how far the entity can move this frame
            move_distance = speed * delta_time
            
            # Get the next position to move to
            next_position = self.pathfinder.get_next_move(current_position, path, move_distance)
            
            # Store for visualization
            movement_data['next_position'] = next_position
            
            # CRITICAL: Directly update entity position without using grid
            # This ensures the visual position changes even if grid movement fails
            import math
            dx = next_position[0] - current_position[0]
            dy = next_position[1] - current_position[1]
            dist = math.hypot(dx, dy)
            
            if dist > 0:
                # Only move if there's a distance to travel
                move_ratio = min(1.0, move_distance / dist)
                new_x = current_position[0] + dx * move_ratio
                new_y = current_position[1] + dy * move_ratio
                
                # Update entity position directly
                entity.position.x = new_x
                entity.position.y = new_y
                
                # Log the movement (for debugging)
                import pygame
                if pygame.time.get_ticks() % 30 == 0:  # Only log occasionally to avoid spam
                    print(f"Moving {entity.name} from {current_position} to ({new_x}, {new_y})")
            
            # Check if we've reached the end of the path
            end_dist = math.hypot(entity.position.x - path[-1][0], entity.position.y - path[-1][1])
            if end_dist < self.cell_size / 2:
                # Reached the target
                entities_to_remove.append(entity)
                entity.is_moving = False
                entity.target_position = None
                
                # Also update grid position
                self.combat_grid.move_entity(entity, (entity.position.x, entity.position.y))
        
        # Remove entities that have finished moving
        for entity in entities_to_remove:
            if entity in self.moving_entities:
                del self.moving_entities[entity]
    
    def render(self, screen):
        """
        Render debug visualization
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        if not self.debug_render:
            return
        
        # Render combat grid
        self.combat_grid.render(screen)
        
        # Render paths for moving entities
        for entity, movement_data in self.moving_entities.items():
            path = movement_data['path']
            
            # Draw the path
            if len(path) > 1:
                pygame.draw.lines(screen, (0, 255, 0), False, path, 2)
                
                # Draw waypoints
                for point in path:
                    pygame.draw.circle(screen, (255, 255, 0), point, 3)
                
                # Highlight the next position
                if movement_data['next_position']:
                    pygame.draw.circle(screen, (255, 0, 0), movement_data['next_position'], 5, 1)
    
    def toggle_debug_render(self):
        """Toggle debug rendering"""
        self.debug_render = not self.debug_render
        self.combat_grid.debug_render = self.debug_render
        return self.debug_render
