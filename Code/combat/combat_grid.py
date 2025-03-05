"""
Combat Grid - Manages spatial positioning and collision detection for combat
"""
import pygame
import math
from enum import Enum, auto

class CellType(Enum):
    """Types of cells in the combat grid"""
    EMPTY = auto()         # Empty cell that can be moved through
    OCCUPIED = auto()      # Cell occupied by an entity
    OBSTACLE = auto()      # Cell blocked by an obstacle
    OUT_OF_BOUNDS = auto() # Cell outside the valid grid area
    HAZARD = auto()        # Cell with a hazard (causes damage)
    COVER = auto()         # Cell providing cover from ranged attacks

class CombatGrid:
    """
    Manages a 2D spatial grid for combat positioning
    Handles collision detection and provides information for pathfinding
    """
    def __init__(self, width, height, cell_size=40):
        """
        Initialize the combat grid
        
        Args:
            width (int): Width of the combat area in pixels
            height (int): Height of the combat area in pixels
            cell_size (int): Size of each grid cell in pixels
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        
        # Calculate grid dimensions
        self.cols = math.ceil(width / cell_size)
        self.rows = math.ceil(height / cell_size)
        
        # Initialize empty grid
        self.reset_grid()
        
        # Entity-to-position mapping
        self.entity_positions = {}
        
        # Define movement costs
        self.movement_cost = {
            CellType.EMPTY: 1.0,
            CellType.OCCUPIED: float('inf'),  # Can't move through occupied cells
            CellType.OBSTACLE: float('inf'),  # Can't move through obstacles
            CellType.OUT_OF_BOUNDS: float('inf')  # Can't move out of bounds
        }
        
        # Debug visualization options
        self.debug_render = False
        
    def reset_grid(self):
        """Reset the grid to empty state"""
        self.grid = [[CellType.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.entity_positions = {}
        
        # Add obstacles (can be customized for different battle areas)
        self._add_default_obstacles()
    
    def _add_default_obstacles(self):
        """Add default obstacles to the grid"""
        # Example: Add some rocks or barriers near the edges
        # This can be customized per battle area
        
        # Add some boundary obstacles
        for col in range(self.cols):
            # Top and bottom borders (partial)
            if col % 8 == 0 or col % 8 == 1:
                self.grid[0][col] = CellType.OBSTACLE
                self.grid[self.rows-1][col] = CellType.OBSTACLE
    
    def get_cell_coords(self, position):
        """
        Convert pixel position to grid coordinates
        
        Args:
            position (tuple): (x, y) position in pixels
            
        Returns:
            tuple: (row, col) grid coordinates
        """
        col = max(0, min(self.cols - 1, int(position[0] / self.cell_size)))
        row = max(0, min(self.rows - 1, int(position[1] / self.cell_size)))
        return row, col
    
    def get_pixel_coords(self, grid_coords):
        """
        Convert grid coordinates to pixel position (cell center)
        
        Args:
            grid_coords (tuple): (row, col) grid coordinates
            
        Returns:
            tuple: (x, y) pixel position
        """
        row, col = grid_coords
        x = (col + 0.5) * self.cell_size
        y = (row + 0.5) * self.cell_size
        return x, y
    
    def is_valid_cell(self, grid_coords):
        """
        Check if grid coordinates are within bounds
        
        Args:
            grid_coords (tuple): (row, col) grid coordinates
            
        Returns:
            bool: True if cell is within grid bounds
        """
        row, col = grid_coords
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def get_cell_type(self, grid_coords):
        """
        Get the type of a grid cell
        
        Args:
            grid_coords (tuple): (row, col) grid coordinates
            
        Returns:
            CellType: Type of the cell
        """
        row, col = grid_coords
        if not self.is_valid_cell((row, col)):
            return CellType.OUT_OF_BOUNDS
        return self.grid[row][col]
    
    def set_cell_type(self, grid_coords, cell_type):
        """
        Set the type of a grid cell
        
        Args:
            grid_coords (tuple): (row, col) grid coordinates
            cell_type (CellType): New cell type
            
        Returns:
            bool: True if successful, False if out of bounds
        """
        row, col = grid_coords
        if not self.is_valid_cell((row, col)):
            return False
        self.grid[row][col] = cell_type
        return True
    
    def get_entity_at(self, grid_coords):
        """
        Get the entity at a grid position
        
        Args:
            grid_coords (tuple): (row, col) grid coordinates
            
        Returns:
            entity or None: Entity at the position or None if empty
        """
        for entity, pos in self.entity_positions.items():
            if pos == grid_coords:
                return entity
        return None
    
    def register_entity(self, entity, position):
        """
        Register an entity at a position
        
        Args:
            entity (BaseCharacter): Entity to register
            position (tuple): (x, y) pixel position
            
        Returns:
            bool: True if successful, False if position is occupied
        """
        grid_coords = self.get_cell_coords(position)
        
        # Check if position is available
        if self.grid[grid_coords[0]][grid_coords[1]] != CellType.EMPTY:
            return False
        
        # If entity is already registered, remove from previous position
        if entity in self.entity_positions:
            old_coords = self.entity_positions[entity]
            self.grid[old_coords[0]][old_coords[1]] = CellType.EMPTY
        
        # Register at new position
        self.entity_positions[entity] = grid_coords
        self.grid[grid_coords[0]][grid_coords[1]] = CellType.OCCUPIED
        
        # Update entity's position
        entity.position.x, entity.position.y = self.get_pixel_coords(grid_coords)
        
        return True
    
    def move_entity(self, entity, new_position):
        """
        Move an entity to a new position
        
        Args:
            entity (BaseCharacter): Entity to move
            new_position (tuple): (x, y) new pixel position
            
        Returns:
            bool: True if move successful, False if blocked
        """
        if entity not in self.entity_positions:
            return self.register_entity(entity, new_position)
        
        old_coords = self.entity_positions[entity]
        new_coords = self.get_cell_coords(new_position)
        
        # Check if the move is valid
        if old_coords == new_coords:
            # No actual movement needed
            return True
        
        # Check if target position is available
        if not self.is_valid_cell(new_coords) or self.grid[new_coords[0]][new_coords[1]] != CellType.EMPTY:
            return False
        
        # Update grid
        self.grid[old_coords[0]][old_coords[1]] = CellType.EMPTY
        self.grid[new_coords[0]][new_coords[1]] = CellType.OCCUPIED
        self.entity_positions[entity] = new_coords
        
        # Update entity's position
        entity.position.x, entity.position.y = self.get_pixel_coords(new_coords)
        
        return True
    
    def remove_entity(self, entity):
        """
        Remove an entity from the grid
        
        Args:
            entity (BaseCharacter): Entity to remove
            
        Returns:
            bool: True if removed, False if entity wasn't on the grid
        """
        if entity not in self.entity_positions:
            return False
        
        # Clear old position
        old_coords = self.entity_positions[entity]
        self.grid[old_coords[0]][old_coords[1]] = CellType.EMPTY
        del self.entity_positions[entity]
        
        return True
    
    def is_position_free(self, position):
        """
        Check if a pixel position is free
        
        Args:
            position (tuple): (x, y) pixel position
            
        Returns:
            bool: True if position is free
        """
        grid_coords = self.get_cell_coords(position)
        return self.is_valid_cell(grid_coords) and self.grid[grid_coords[0]][grid_coords[1]] == CellType.EMPTY
    
    def get_nearby_positions(self, position, distance=1):
        """
        Get all valid nearby positions within a given distance
        
        Args:
            position (tuple): (x, y) pixel position
            distance (int): Distance in grid cells
            
        Returns:
            list: List of (x, y) valid nearby positions
        """
        center_coords = self.get_cell_coords(position)
        nearby_positions = []
        
        for d_row in range(-distance, distance + 1):
            for d_col in range(-distance, distance + 1):
                # Skip the center position
                if d_row == 0 and d_col == 0:
                    continue
                
                row = center_coords[0] + d_row
                col = center_coords[1] + d_col
                
                if self.is_valid_cell((row, col)) and self.grid[row][col] == CellType.EMPTY:
                    nearby_positions.append(self.get_pixel_coords((row, col)))
        
        return nearby_positions
    
    def get_nearest_free_position(self, position):
        """
        Find the nearest free position to a given position
        
        Args:
            position (tuple): (x, y) pixel position
            
        Returns:
            tuple: (x, y) nearest free position or None if none found
        """
        center_coords = self.get_cell_coords(position)
        
        # Try expanding outward from the center
        for distance in range(1, max(self.rows, self.cols)):
            for d_row in range(-distance, distance + 1):
                for d_col in range(-distance, distance + 1):
                    # Only check positions at exactly the current distance
                    if max(abs(d_row), abs(d_col)) != distance:
                        continue
                    
                    row = center_coords[0] + d_row
                    col = center_coords[1] + d_col
                    
                    if self.is_valid_cell((row, col)) and self.grid[row][col] == CellType.EMPTY:
                        return self.get_pixel_coords((row, col))
        
        return None
    
    def get_grid_distance(self, position1, position2):
        """
        Calculate the grid distance between two positions
        
        Args:
            position1 (tuple): (x, y) first position
            position2 (tuple): (x, y) second position
            
        Returns:
            int: Manhattan distance in grid cells
        """
        coords1 = self.get_cell_coords(position1)
        coords2 = self.get_cell_coords(position2)
        
        # Manhattan distance
        return abs(coords1[0] - coords2[0]) + abs(coords1[1] - coords2[1])
    
    def are_adjacent(self, entity1, entity2):
        """
        Check if two entities are adjacent on the grid
        
        Args:
            entity1: First entity
            entity2: Second entity
            
        Returns:
            bool: True if entities are adjacent
        """
        if entity1 not in self.entity_positions or entity2 not in self.entity_positions:
            return False
        
        pos1 = self.entity_positions[entity1]
        pos2 = self.entity_positions[entity2]
        
        # Check if positions are adjacent (horizontally, vertically, or diagonally)
        return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1])) <= 1
    
    def get_neighbors(self, grid_coords):
        """
        Get valid neighboring cells for pathfinding
        
        Args:
            grid_coords (tuple): (row, col) grid coordinates
            
        Returns:
            list: List of (row, col) valid neighboring coords
        """
        row, col = grid_coords
        neighbors = []
        
        # Check all 8 adjacent cells (including diagonals)
        for d_row in [-1, 0, 1]:
            for d_col in [-1, 0, 1]:
                # Skip the center cell
                if d_row == 0 and d_col == 0:
                    continue
                
                new_row = row + d_row
                new_col = col + d_col
                
                # Check if cell is valid and passable
                if (self.is_valid_cell((new_row, new_col)) and 
                    self.grid[new_row][new_col] == CellType.EMPTY):
                    neighbors.append((new_row, new_col))
        
        return neighbors
    
    def get_path_cost(self, from_coords, to_coords):
        """
        Calculate movement cost between two adjacent cells
        
        Args:
            from_coords (tuple): (row, col) starting coordinates
            to_coords (tuple): (row, col) target coordinates
            
        Returns:
            float: Movement cost or infinity if not possible
        """
        # Return infinity if cells are not adjacent
        if max(abs(from_coords[0] - to_coords[0]), abs(from_coords[1] - to_coords[1])) > 1:
            return float('inf')
        
        # Check if target is valid
        if not self.is_valid_cell(to_coords):
            return float('inf')
        
        # Base cost
        cost = self.movement_cost[self.grid[to_coords[0]][to_coords[1]]]
        
        # Diagonal movement costs more
        if from_coords[0] != to_coords[0] and from_coords[1] != to_coords[1]:
            cost *= 1.414  # sqrt(2)
        
        return cost
    
    def render(self, screen):
        """
        Render the grid (for debugging)
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        if not self.debug_render:
            return
        
        # Render grid lines
        for row in range(self.rows + 1):
            pygame.draw.line(
                screen,
                (100, 100, 100),
                (0, row * self.cell_size),
                (self.width, row * self.cell_size),
                1
            )
        
        for col in range(self.cols + 1):
            pygame.draw.line(
                screen,
                (100, 100, 100),
                (col * self.cell_size, 0),
                (col * self.cell_size, self.height),
                1
            )
        
        # Render cell types
        for row in range(self.rows):
            for col in range(self.cols):
                cell_rect = pygame.Rect(
                    col * self.cell_size,
                    row * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Different colors for different cell types
                if self.grid[row][col] == CellType.OBSTACLE:
                    pygame.draw.rect(screen, (200, 0, 0, 100), cell_rect, 0)
                elif self.grid[row][col] == CellType.OCCUPIED:
                    pygame.draw.rect(screen, (0, 0, 200, 80), cell_rect, 0)
                
                # Draw cell coordinates for debugging
                if self.cell_size > 20:
                    font = pygame.font.SysFont("Arial", 10)
                    text = font.render(f"{row},{col}", True, (150, 150, 150))
                    screen.blit(text, (col * self.cell_size + 2, row * self.cell_size + 2))
    
    def toggle_debug_render(self):
        """Toggle debug rendering of the grid"""
        self.debug_render = not self.debug_render
        return self.debug_render
