"""
Combat Grid Test - A standalone module to test and visualize the combat grid
"""
import sys
import os
import pygame
import random
import time
import math

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from combat.combat_grid import CombatGrid, CellType
from combat.pathfinding import AStar
from combat.movement_controller import MovementController

class DummyEntity:
    """Dummy entity for testing"""
    def __init__(self, name, position=(0, 0), speed=100):
        self.name = name
        self.position = pygame.Vector2(position)
        self.movement_speed = speed
        self.is_alive = lambda: True
        self.is_moving = False
        self.target_position = None
        
        # Create a simple sprite
        self.sprite = pygame.Surface((20, 20))
        self.sprite.fill((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

class GridTestApp:
    """Test application for combat grid and movement system"""
    def __init__(self, width=800, height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Combat Grid Test")
        
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14)
        
        # Create movement controller
        self.movement_controller = MovementController(width, height, 40)
        self.movement_controller.debug_render = True
        
        # Create some test entities
        self.entities = [
            DummyEntity(f"Entity {i}", 
                       (random.randint(50, width-50), random.randint(50, height-50)), 
                       random.randint(50, 150))
            for i in range(5)
        ]
        
        # Register entities
        for entity in self.entities:
            self.movement_controller.register_entity(entity)
        
        # Add some obstacles
        grid = self.movement_controller.combat_grid
        for _ in range(10):
            row = random.randint(0, grid.rows - 1)
            col = random.randint(0, grid.cols - 1)
            grid.set_cell_type((row, col), CellType.OBSTACLE)
        
        # Test parameters
        self.selected_entity = None
        self.path_start = None
        self.path_end = None
        self.current_path = None
        self.show_help = True
        
        self.running = True
    
    def run(self):
        """Run the test application"""
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos, event.button)
            
            # Update
            self.update(delta_time)
            
            # Render
            self.render()
            
            pygame.display.flip()
    
    def handle_key(self, key):
        """Handle keyboard input"""
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_h:
            self.show_help = not self.show_help
        elif key == pygame.K_c:
            # Clear paths and selection
            self.selected_entity = None
            self.path_start = None
            self.path_end = None
            self.current_path = None
        elif key == pygame.K_r:
            # Randomize entity positions
            for entity in self.entities:
                new_pos = (random.randint(50, self.width-50), 
                          random.randint(50, self.height-50))
                self.movement_controller.move_entity(entity, new_pos)
        elif key == pygame.K_s:
            # Stop all movements
            for entity in self.entities:
                self.movement_controller.stop_movement(entity)
    
    def handle_mouse_click(self, pos, button):
        """Handle mouse click"""
        if button == 1:  # Left click
            # Check if clicked on an entity
            for entity in self.entities:
                entity_rect = pygame.Rect(
                    entity.position.x - 10, entity.position.y - 10, 20, 20)
                if entity_rect.collidepoint(pos):
                    self.selected_entity = entity
                    print(f"Selected entity: {entity.name}")
                    break
            else:
                # If we have a selected entity, start movement
                if self.selected_entity:
                    self.movement_controller.start_movement(self.selected_entity, pos)
                    print(f"Moving {self.selected_entity.name} to {pos}")
                
                # Otherwise, set path start/end for testing
                elif self.path_start is None:
                    self.path_start = pos
                    self.current_path = None
                    print(f"Path start set to {pos}")
                else:
                    self.path_end = pos
                    self.calculate_test_path()
        
        elif button == 3:  # Right click
            # Create or remove obstacle
            grid = self.movement_controller.combat_grid
            cell_coords = grid.get_cell_coords(pos)
            
            if grid.is_valid_cell(cell_coords):
                if grid.get_cell_type(cell_coords) == CellType.OBSTACLE:
                    grid.set_cell_type(cell_coords, CellType.EMPTY)
                    print(f"Removed obstacle at {cell_coords}")
                else:
                    grid.set_cell_type(cell_coords, CellType.OBSTACLE)
                    print(f"Added obstacle at {cell_coords}")
    
    def calculate_test_path(self):
        """Calculate path between path_start and path_end"""
        if self.path_start and self.path_end:
            # Find path
            self.current_path = self.movement_controller.pathfinder.find_path(
                self.path_start, self.path_end)
            
            if self.current_path:
                print(f"Found path with {len(self.current_path)} waypoints")
            else:
                print("No path found")
    
    def update(self, delta_time):
        """Update the test application"""
        # Update movement controller
        self.movement_controller.update(delta_time)
    
    def render(self):
        """Render the test application"""
        # Clear screen
        self.screen.fill((20, 20, 30))
        
        # Draw combat grid and paths
        self.movement_controller.render(self.screen)
        
        # Draw test path
        if self.current_path:
            pygame.draw.lines(self.screen, (255, 255, 0), False, self.current_path, 2)
            
            # Draw waypoints
            for point in self.current_path:
                pygame.draw.circle(self.screen, (255, 0, 0), (int(point[0]), int(point[1])), 3)
        
        # Draw path start/end markers
        if self.path_start:
            pygame.draw.circle(self.screen, (0, 255, 0), 
                             (int(self.path_start[0]), int(self.path_start[1])), 5, 2)
        if self.path_end:
            pygame.draw.circle(self.screen, (255, 0, 0), 
                             (int(self.path_end[0]), int(self.path_end[1])), 5, 2)
        
        # Draw entities
        for entity in self.entities:
            # Draw entity
            pygame.draw.rect(self.screen, (255, 255, 255), 
                           (entity.position.x - 10, entity.position.y - 10, 20, 20))
            
            # Highlight selected entity
            if entity == self.selected_entity:
                pygame.draw.rect(self.screen, (255, 255, 0), 
                               (entity.position.x - 12, entity.position.y - 12, 24, 24), 2)
            
            # Draw entity name
            text = self.font.render(entity.name, True, (255, 255, 255))
            self.screen.blit(text, (entity.position.x - text.get_width() // 2, 
                                   entity.position.y - 30))
        
        # Draw help text
        if self.show_help:
            help_texts = [
                "Left-click: Select entity / Set movement target",
                "Right-click: Add/remove obstacle",
                "H: Toggle help text",
                "C: Clear selection and paths",
                "R: Randomize entity positions",
                "S: Stop all movements",
                "ESC: Quit"
            ]
            
            y = 10
            for text in help_texts:
                surface = self.font.render(text, True, (255, 255, 255))
                self.screen.blit(surface, (10, y))
                y += 20

if __name__ == "__main__":
    app = GridTestApp()
    app.run()
    pygame.quit()
