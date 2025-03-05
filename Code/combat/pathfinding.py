"""
Pathfinding - Implements A* pathfinding algorithm for combat movement
"""
import heapq
import math
from collections import defaultdict
from combat.combat_grid import CellType  # Import CellType directly

class PriorityQueue:
    """A Priority Queue implementation for A* algorithm"""
    def __init__(self):
        self.elements = []
        self.count = 0
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        # Count is used to break ties consistently when items have the same priority
        self.count += 1
        heapq.heappush(self.elements, (priority, self.count, item))
    
    def get(self):
        return heapq.heappop(self.elements)[2]

class AStar:
    """
    A* pathfinding implementation for grid-based movement
    """
    def __init__(self, combat_grid):
        """
        Initialize the pathfinder
        
        Args:
            combat_grid (CombatGrid): Reference to the combat grid
        """
        self.grid = combat_grid
    
    def heuristic(self, a, b):
        """
        Calculate heuristic (estimated distance) between two grid coordinates
        
        Args:
            a (tuple): (row, col) starting coordinates
            b (tuple): (row, col) target coordinates
            
        Returns:
            float: Estimated distance
        """
        # Diagonal distance heuristic
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    
    def find_path(self, start_position, goal_position, max_iterations=1000):
        """
        Find a path from start to goal using A*
        
        Args:
            start_position (tuple): (x, y) starting pixel position
            goal_position (tuple): (x, y) target pixel position
            max_iterations (int): Maximum number of search iterations
            
        Returns:
            list: List of (x, y) positions forming a path or None if no path found
        """
        # Convert pixel positions to grid coordinates
        start = self.grid.get_cell_coords(start_position)
        goal = self.grid.get_cell_coords(goal_position)
        
        # If start or goal is invalid, find nearest valid cell
        if not self.grid.is_valid_cell(start) or self.grid.get_cell_type(start) != CellType.EMPTY:  # Fixed reference
            return None
        
        # If goal is not empty, find nearest empty cell to the goal
        # But skip this check if the goal position has an entity (common for attack moves)
        if (not self.grid.is_valid_cell(goal) or 
            (self.grid.get_cell_type(goal) != CellType.EMPTY and  # Fixed reference
             self.grid.get_entity_at(goal) is None)):
            return None
        
        # If start and goal are the same, return a single-point path
        if start == goal:
            return [start_position]
        
        # Initialize the A* algorithm
        frontier = PriorityQueue()
        frontier.put(start, 0)
        
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        iteration_count = 0
        
        # Main A* loop
        while not frontier.empty() and iteration_count < max_iterations:
            iteration_count += 1
            current = frontier.get()
            
            # Early exit if we've reached the goal
            if current == goal:
                break
            
            # Explore neighbors
            for next_cell in self.grid.get_neighbors(current):
                # Calculate movement cost to this neighbor
                new_cost = cost_so_far[current] + self.grid.get_path_cost(current, next_cell)
                
                # If this is a better path to this neighbor
                if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                    cost_so_far[next_cell] = new_cost
                    priority = new_cost + self.heuristic(goal, next_cell)
                    frontier.put(next_cell, priority)
                    came_from[next_cell] = current
        
        # Check if we found a path
        if goal not in came_from:
            # Try to find a path to a nearby cell instead
            for distance in range(1, 4):
                for d_row in range(-distance, distance + 1):
                    for d_col in range(-distance, distance + 1):
                        # Only check cells at the current distance
                        if max(abs(d_row), abs(d_col)) != distance:
                            continue
                        
                        alt_goal = (goal[0] + d_row, goal[1] + d_col)
                        if (self.grid.is_valid_cell(alt_goal) and 
                            self.grid.get_cell_type(alt_goal) == CellType.EMPTY and  # Fixed reference
                            alt_goal in came_from):
                            # Use this alternative goal
                            goal = alt_goal
                            return self._reconstruct_path(came_from, start, goal)
                
            # No path found
            return None
        
        # Reconstruct the path
        return self._reconstruct_path(came_from, start, goal)
    
    def _reconstruct_path(self, came_from, start, goal):
        """
        Reconstruct the path from start to goal
        
        Args:
            came_from (dict): Dict mapping each cell to the cell it came from
            start (tuple): (row, col) starting coordinates
            goal (tuple): (row, col) target coordinates
            
        Returns:
            list: List of (x, y) positions forming a path
        """
        current = goal
        path = []
        
        while current != start:
            # Convert grid coords to pixel position (cell center)
            pixel_coords = self.grid.get_pixel_coords(current)
            path.append(pixel_coords)
            current = came_from[current]
        
        # Add start position
        path.append(self.grid.get_pixel_coords(start))
        
        # Reverse to get path from start to goal
        path.reverse()
        
        return path
    
    def find_path_to_nearest_cell_to_target(self, start_position, target_entity, max_distance=1):
        """
        Find a path to the nearest accessible cell adjacent to a target entity
        
        Args:
            start_position (tuple): (x, y) starting pixel position
            target_entity: Target entity to approach
            max_distance (int): Maximum distance in grid cells to consider as "adjacent"
            
        Returns:
            list: List of (x, y) positions forming a path or None if no path found
        """
        if target_entity not in self.grid.entity_positions:
            return None
        
        # Get target entity's grid position
        target_coords = self.grid.entity_positions[target_entity]
        
        # Find all empty cells around the target
        nearby_cells = []
        for d_row in range(-max_distance, max_distance + 1):
            for d_col in range(-max_distance, max_distance + 1):
                # Skip the target's own cell
                if d_row == 0 and d_col == 0:
                    continue
                
                cell = (target_coords[0] + d_row, target_coords[1] + d_col)
                if (self.grid.is_valid_cell(cell) and 
                    self.grid.get_cell_type(cell) == CellType.EMPTY):  # Fixed reference
                    nearby_cells.append(cell)
        
        if not nearby_cells:
            return None
        
        # Convert start position to grid coordinates
        start_coords = self.grid.get_cell_coords(start_position)
        
        # Find the nearest cell to the start position
        nearest_cell = min(nearby_cells, key=lambda cell: 
                          (abs(cell[0] - start_coords[0]) + abs(cell[1] - start_coords[1])))
        
        # Find path to this cell
        nearest_pixel_pos = self.grid.get_pixel_coords(nearest_cell)
        return self.find_path(start_position, nearest_pixel_pos)
    
    def get_next_move(self, current_position, path, move_distance=None):
        """
        Get the next position to move to along a path within a given distance
        
        Args:
            current_position (tuple): (x, y) current pixel position
            path (list): List of (x, y) positions forming a path
            move_distance (float, optional): Maximum move distance in pixels
            
        Returns:
            tuple: (x, y) next position to move to
        """
        if not path or len(path) < 2:
            return current_position
        
        # Skip points in the path that are behind the current position
        current_index = 0
        for i, point in enumerate(path):
            if i < len(path) - 1:
                # Check if we're closer to the next point than this one
                next_point = path[i + 1]
                dist_to_current = math.hypot(point[0] - current_position[0], point[1] - current_position[1])
                dist_to_next = math.hypot(next_point[0] - current_position[0], next_point[1] - current_position[1])
                
                if dist_to_next < dist_to_current:
                    current_index = i + 1
        
        # If we're at the last point already
        if current_index >= len(path) - 1:
            return path[-1]
        
        # Get the next point in the path
        next_point = path[current_index + 1]
        
        # If no move distance specified, return the next point directly
        if move_distance is None:
            return next_point
        
        # Otherwise, move toward the next point but limited by move_distance
        dx = next_point[0] - current_position[0]
        dy = next_point[1] - current_position[1]
        distance = math.hypot(dx, dy)
        
        if distance <= move_distance:
            return next_point
        else:
            # Move a fraction of the way toward the next point
            fraction = move_distance / distance
            return (
                current_position[0] + dx * fraction,
                current_position[1] + dy * fraction
            )
    
    def simplify_path(self, path, tolerance=10):
        """
        Simplify a path by removing unnecessary waypoints
        
        Args:
            path (list): List of (x, y) positions forming a path
            tolerance (float): Maximum deviation from original path
            
        Returns:
            list: Simplified path
        """
        if not path or len(path) < 3:
            return path
        
        # Start with the first point
        simplified = [path[0]]
        current_point = 0
        
        while current_point < len(path) - 1:
            # Look ahead as far as possible
            for i in range(len(path) - 1, current_point, -1):
                # Check if we can go directly from current_point to i
                direct_path = True
                
                start = path[current_point]
                end = path[i]
                
                for j in range(current_point + 1, i):
                    point = path[j]
                    # Calculate distance from point to line segment
                    dist = self._point_to_segment_distance(point, start, end)
                    
                    if dist > tolerance:
                        direct_path = False
                        break
                
                if direct_path:
                    simplified.append(path[i])
                    current_point = i
                    break
            
            # If we didn't find a simplification, just add the next point
            if current_point == i:
                continue
            else:
                simplified.append(path[current_point + 1])
                current_point += 1
        
        return simplified
    
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
