"""
Tactical AI - Enhances enemy AI with positioning strategies
"""
import random
import math
import pygame
from combat.combat_state import CombatState
from game.events import trigger_event, EVENT_COMBAT_MOVE_START

class TacticalAI:
    """
    Enhances enemies with tactical positioning and decision-making
    """
    def __init__(self, battle_manager):
        """
        Initialize the tactical AI system
        
        Args:
            battle_manager: Reference to the battle manager
        """
        self.battle_manager = battle_manager
        self.movement_controller = getattr(battle_manager, 'movement_controller', None)
        
        # Tactical position evaluation weights
        self.weights = {
            'distance_to_target': 2.0,     # Weight for optimal distance to target
            'flanking_position': 1.5,      # Weight for flanking position
            'ally_proximity': 0.8,         # Weight for staying near allies
            'cover_value': 1.2,            # Weight for seeking cover
            'avoid_aoe': 1.5,              # Weight for avoiding area effects
            'threat_avoidance': 1.0,       # Weight for avoiding high-threat targets
            'mobility': 0.7,               # Weight for maintaining mobility
        }
        
        # AI behavior profiles for different enemy types
        self.behavior_profiles = {
            'aggressive': {
                'preferred_distance': 0.8,  # Closer than attack range
                'flanking_bonus': 1.8,      # High flanking preference
                'cover_preference': 0.5,    # Low cover preference
                'ally_grouping': 0.7,       # Moderate grouping
            },
            'cautious': {
                'preferred_distance': 1.2,  # Slightly beyond attack range
                'flanking_bonus': 1.0,      # Moderate flanking preference
                'cover_preference': 1.5,    # High cover preference
                'ally_grouping': 1.2,       # Higher grouping
            },
            'ranged': {
                'preferred_distance': 1.5,  # Far beyond attack range
                'flanking_bonus': 0.8,      # Low flanking preference
                'cover_preference': 1.8,    # Very high cover preference
                'ally_grouping': 0.9,       # Moderate grouping
            },
            'mobile': {
                'preferred_distance': 1.0,  # At attack range
                'flanking_bonus': 1.5,      # High flanking preference
                'cover_preference': 0.7,    # Low cover preference
                'ally_grouping': 0.5,       # Low grouping
            },
            'defensive': {
                'preferred_distance': 1.1,  # Just beyond attack range
                'flanking_bonus': 0.6,      # Low flanking preference
                'cover_preference': 2.0,    # Very high cover preference
                'ally_grouping': 1.5,       # Very high grouping
            },
        }
        
        # Default profile
        self.default_profile = 'cautious'
        
        # Enemy type to behavior profile mapping
        self.enemy_type_profiles = {
            'goblin': 'mobile',
            'orc': 'aggressive',
            'troll': 'defensive',
            'skeleton': 'cautious',
            'dragon': 'aggressive',
        }
        
        # Timing for tactical reassessment
        self.reassessment_interval = 2.0  # Seconds between tactical reassessments
        self.entity_timers = {}  # When entities last made tactical decisions
    
    def get_entity_profile(self, entity):
        """
        Get the behavior profile for an entity
        
        Args:
            entity: The entity to get a profile for
            
        Returns:
            dict: Behavior profile
        """
        # Check if entity has an enemy_type
        if hasattr(entity, 'enemy_type'):
            profile_name = self.enemy_type_profiles.get(
                entity.enemy_type, self.default_profile)
            return self.behavior_profiles[profile_name]
        
        # Fallback to default
        return self.behavior_profiles[self.default_profile]
    
    def evaluate_position(self, entity, position, target=None):
        """
        Evaluate a position for tactical value
        
        Args:
            entity: The entity to evaluate for
            position (tuple): (x, y) position to evaluate
            target: Target entity or None
            
        Returns:
            float: Tactical value score
        """
        if not self.movement_controller or not self.battle_manager:
            return 0.0
            
        grid = self.movement_controller.combat_grid
        
        # Check if position is even valid
        if not grid.is_position_free(position):
            return -1000.0  # Highly negative score for invalid positions
        
        # Get entity's profile
        profile = self.get_entity_profile(entity)
        
        # Get entity's attack range
        attack_range = getattr(entity, 'attack_range', 100)
        
        score = 0.0
        
        # Evaluate distance to target
        if target and hasattr(target, 'position'):
            target_pos = (target.position.x, target.position.y)
            distance = math.hypot(position[0] - target_pos[0], position[1] - target_pos[1])
            
            # Calculate optimal distance factor
            preferred_distance = attack_range * profile['preferred_distance']
            distance_factor = 1.0 - min(1.0, abs(distance - preferred_distance) / preferred_distance)
            
            score += distance_factor * self.weights['distance_to_target']
            
            # Evaluate flanking position
            if hasattr(target, 'position') and hasattr(entity, 'team'):
                # Find other allies targeting this enemy
                allies = [other for other in self.battle_manager.game_state.enemies 
                         if other != entity and other.is_alive() and 
                         getattr(other, 'team', None) == getattr(entity, 'team', None)]
                
                for ally in allies:
                    if hasattr(ally, 'current_target') and ally.current_target == target:
                        # Calculate flanking angle
                        ally_pos = (ally.position.x, ally.position.y)
                        angle1 = math.atan2(position[1] - target_pos[1], position[0] - target_pos[0])
                        angle2 = math.atan2(ally_pos[1] - target_pos[1], ally_pos[0] - target_pos[0])
                        angle_diff = abs(angle1 - angle2)
                        
                        # Normalize angle difference to [0, π]
                        angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
                        
                        # Best flanking is at 90-180 degrees
                        if math.pi / 2 <= angle_diff <= math.pi:
                            flank_value = (angle_diff - math.pi/2) / (math.pi/2)
                            score += flank_value * profile['flanking_bonus'] * self.weights['flanking_position']
        
        # Evaluate proximity to allies
        allies = [other for other in self.battle_manager.game_state.enemies 
                 if other != entity and other.is_alive() and 
                 getattr(other, 'team', None) == getattr(entity, 'team', None)]
        
        ally_proximity = 0.0
        for ally in allies:
            ally_pos = (ally.position.x, ally.position.y)
            distance = math.hypot(position[0] - ally_pos[0], position[1] - ally_pos[1])
            
            # Prefer positions not too close but not too far from allies
            optimal_ally_distance = 120  # About 3 grid cells
            proximity_factor = 1.0 - min(1.0, abs(distance - optimal_ally_distance) / optimal_ally_distance)
            ally_proximity += proximity_factor
        
        if allies:
            ally_proximity /= len(allies)
            score += ally_proximity * profile['ally_grouping'] * self.weights['ally_proximity']
        
        # Evaluate cover value
        if grid.debug_render:  # Only if grid is available for checking
            cell_coords = grid.get_cell_coords(position)
            adjacent_cells = []
            
            # Check 8 adjacent cells
            for d_row in [-1, 0, 1]:
                for d_col in [-1, 0, 1]:
                    if d_row == 0 and d_col == 0:
                        continue
                    
                    adj_cell = (cell_coords[0] + d_row, cell_coords[1] + d_col)
                    if grid.is_valid_cell(adj_cell):
                        adjacent_cells.append(adj_cell)
            
            # Count obstacles in adjacent cells
            cover_count = sum(1 for cell in adjacent_cells 
                             if grid.get_cell_type(cell) in [grid.CellType.OBSTACLE, grid.CellType.COVER])
            
            # More adjacent obstacles means better cover
            cover_value = cover_count / len(adjacent_cells) if adjacent_cells else 0
            score += cover_value * profile['cover_preference'] * self.weights['cover_value']
        
        # Additional tactical evaluations could be added here
        
        return score
    
    def find_best_tactical_position(self, entity, target=None, radius=200, samples=12):
        """
        Find the best tactical position for an entity
        
        Args:
            entity: The entity to find a position for
            target: Target entity or None
            radius (float): Search radius around current position
            samples (int): Number of sample positions to evaluate
            
        Returns:
            tuple: (x, y) best position or None if current position is best
        """
        if not self.movement_controller:
            return None
            
        current_pos = (entity.position.x, entity.position.y)
        
        # Evaluate current position
        current_score = self.evaluate_position(entity, current_pos, target)
        
        # Generate sample positions
        sample_positions = []
        for i in range(samples):
            angle = 2 * math.pi * i / samples
            for dist_factor in [0.4, 0.7, 1.0]:  # Try different distances
                dx = math.cos(angle) * radius * dist_factor
                dy = math.sin(angle) * radius * dist_factor
                sample_pos = (current_pos[0] + dx, current_pos[1] + dy)
                sample_positions.append(sample_pos)
        
        # Add target-relative positions if target exists
        if target and hasattr(target, 'position'):
            target_pos = (target.position.x, target.position.y)
            attack_range = getattr(entity, 'attack_range', 100)
            profile = self.get_entity_profile(entity)
            preferred_distance = attack_range * profile['preferred_distance']
            
            # Add positions at preferred distance around target
            for i in range(samples):
                angle = 2 * math.pi * i / samples
                dx = math.cos(angle) * preferred_distance
                dy = math.sin(angle) * preferred_distance
                sample_pos = (target_pos[0] + dx, target_pos[1] + dy)
                sample_positions.append(sample_pos)
        
        # Evaluate all positions
        best_pos = current_pos
        best_score = current_score
        
        for pos in sample_positions:
            score = self.evaluate_position(entity, pos, target)
            if score > best_score:
                best_score = score
                best_pos = pos
        
        # Only return a new position if it's significantly better
        if best_pos == current_pos or best_score < current_score + 0.5:
            return None
            
        return best_pos
    
    def update_entity_tactical_ai(self, entity, delta_time):
        """
        Update tactical AI for an entity
        
        Args:
            entity: The entity to update
            delta_time (float): Time since last update
            
        Returns:
            bool: True if a tactical action was taken
        """
        if not entity.is_alive() or entity.combat_state != CombatState.IDLE:
            return False
        
        # Check if it's time for tactical reassessment
        entity_id = id(entity)
        if entity_id in self.entity_timers:
            self.entity_timers[entity_id] -= delta_time
            if self.entity_timers[entity_id] > 0:
                return False
        
        # Reset timer
        self.entity_timers[entity_id] = self.reassessment_interval
        
        # Get current target
        target = getattr(entity, 'current_target', None)
        
        # If no target, find one
        if not target or not target.is_alive():
            target = self._select_target_for_entity(entity)
            if not target:
                return False
            
            # Store new target
            entity.current_target = target
        
        # Check if in attack range
        if entity.is_in_range(target) and entity.can_attack():
            # If in range and can attack, initiate attack
            attack_success = entity.attack_target(target)
            if attack_success:
                # Schedule completion of attack (end of wind-up)
                self.battle_manager.event_queue.schedule(
                    entity.attack_phase.wind_up_time,
                    5,
                    self.battle_manager._process_enemy_attack,
                    entity,
                    target
                )
                return True
        
        # If not in range or can't attack, find best tactical position
        best_pos = self.find_best_tactical_position(entity, target)
        
        if best_pos:
            # Move to best tactical position
            if hasattr(self.battle_manager, 'initiate_movement'):
                movement_started = self.battle_manager.initiate_movement(
                    entity, best_pos, 
                    lambda e: self._on_tactical_movement_complete(e, target))
                
                if movement_started:
                    return True
        
        return False
    
    def _on_tactical_movement_complete(self, entity, target):
        """
        Handle completion of tactical movement
        
        Args:
            entity: The entity that completed movement
            target: The target entity
        """
        if not entity.is_alive() or not target or not target.is_alive():
            return
            
        # Check if in attack range now
        if entity.is_in_range(target) and entity.can_attack():
            # If in range and can attack, initiate attack
            attack_success = entity.attack_target(target)
            if attack_success:
                # Schedule completion of attack (end of wind-up)
                self.battle_manager.event_queue.schedule(
                    entity.attack_phase.wind_up_time,
                    5,
                    self.battle_manager._process_enemy_attack,
                    entity,
                    target
                )
    
    def _select_target_for_entity(self, entity):
        """
        Select a target for an entity using tactical considerations
        
        Args:
            entity: The entity selecting a target
            
        Returns:
            Entity: Selected target or None
        """
        # Reuse battle manager's target selection logic
        return self.battle_manager._select_target_for_enemy(entity)
    
    def update(self, delta_time):
        """
        Update all entities' tactical AI
        
        Args:
            delta_time (float): Time since last update
        """
        if not self.battle_manager or not hasattr(self.battle_manager, 'game_state'):
            return
            
        # Update each enemy's tactical AI
        for enemy in self.battle_manager.game_state.enemies:
            if enemy.is_alive():
                self.update_entity_tactical_ai(enemy, delta_time)
