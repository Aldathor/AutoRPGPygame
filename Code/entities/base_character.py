"""
Enhanced base character class for real-time combat
"""
from abc import ABC, abstractmethod
import math
import pygame
import time
from game.config import (
    BASE_HP, BASE_ATTACK, BASE_DEFENSE, BASE_MAGIC, BASE_SPEED,
    XP_PER_LEVEL, XP_LEVEL_MULTIPLIER, ATTACK_COOLDOWN_BASE
)
from combat.combat_state import CombatState, AttackPhase

class BaseCharacter(ABC):
    """
    Abstract base class for all characters (players and enemies)
    Enhanced for real-time combat
    """
    def __init__(self, name, level=1):
        """
        Initialize a character with base stats
        
        Args:
            name (str): Character name
            level (int): Starting level
        """
        self.name = name
        self.level = level
        self.xp = 0
        self.xp_to_next_level = self._calculate_xp_for_level(self.level + 1)
        
        # Base stats (to be modified by derived classes)
        self.base_hp = BASE_HP
        self.base_attack = BASE_ATTACK
        self.base_defense = BASE_DEFENSE
        self.base_magic = BASE_MAGIC
        self.base_speed = BASE_SPEED
        
        # Current stats (calculated from base stats and level)
        self.max_hp = self._calculate_max_hp()
        self.attack = self._calculate_attack()
        self.defense = self._calculate_defense()
        self.magic = self._calculate_magic()
        self.speed = self._calculate_speed()
        
        # Current state
        self.current_hp = self.max_hp
        self.attack_cooldown = 0
        self.alive = True
        
        # Visual representation
        self.sprite = None
        self.position = pygame.Vector2(0, 0)
        
        # Real-time combat state tracking
        self.combat_state = CombatState.IDLE
        self.state_start_time = 0
        self.current_target = None
        
        # Attack phase timing (default values, should be overridden by subclasses)
        self.attack_phase = self._create_default_attack_phase()
        
        # Interrupt tracking
        self.can_be_interrupted = True
        self.interrupt_resistance = self.defense * 0.1  # Base interrupt resistance
        
        # Positioning for real-time combat
        self.movement_speed = self.speed * 0.5  # Base movement speed
        self.attack_range = 50  # Default attack range in pixels
        
        # Movement and targeting
        self.target_position = None
        self.is_moving = False
    
    def _create_default_attack_phase(self):
        """
        Create default attack phase timing based on character stats
        
        Returns:
            AttackPhase: Default attack phase timing
        """
        # Speed affects all phases - faster characters have quicker attacks
        speed_factor = self.speed / 10.0
        
        # Default timing values in seconds
        wind_up_time = max(0.2, 0.5 - 0.03 * speed_factor)
        attack_time = max(0.1, 0.2 - 0.01 * speed_factor)
        recovery_time = max(0.3, 0.7 - 0.04 * speed_factor)
        
        return AttackPhase(wind_up_time, attack_time, recovery_time)
    
    def stop_movement(self, battle_manager=None):
        """
        Stop the character's movement
        
        Args:
            battle_manager: Reference to battle manager (optional)
            
        Returns:
            bool: True if was moving and is now stopped
        """
        was_moving = self.is_moving or self.combat_state == CombatState.MOVING
        
        # Use battle manager if provided
        if battle_manager and hasattr(battle_manager, 'movement_controller'):
            if battle_manager.movement_controller.is_entity_moving(self):
                battle_manager.movement_controller.stop_movement(self)
        
        # Reset movement state
        self.is_moving = False
        self.target_position = None
        
        # Update combat state if currently moving
        if self.combat_state == CombatState.MOVING:
            self.combat_state = CombatState.IDLE
            self.state_start_time = time.time()
        
        return was_moving

    def is_in_range(self, target, battle_manager=None):
        """
        Check if target is within attack range
        
        Args:
            target (BaseCharacter): Target to check
            battle_manager: Reference to battle manager (optional)
            
        Returns:
            bool: True if in range
        """
        if not target:
            return False
        
        # Use battle manager if provided (for grid-based distance)
        if battle_manager and hasattr(battle_manager, 'movement_controller'):
            grid = battle_manager.movement_controller.combat_grid
            if self in grid.entity_positions and target in grid.entity_positions:
                # Convert attack range to grid distance
                grid_range = max(1, int(self.attack_range / grid.cell_size))
                
                # Check if within grid range
                pos1 = grid.entity_positions[self]
                pos2 = grid.entity_positions[target]
                grid_distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
                
                return grid_distance <= grid_range
        
        # Legacy range check (direct distance)
        if not hasattr(target, 'position'):
            return False
            
        # Calculate distance between characters
        direction = target.position - self.position
        distance = direction.length()
        
        # Compare with attack range
        return distance <= self.attack_range

    def can_see_target(self, target, battle_manager=None):
        """
        Check if there is line of sight to target
        
        Args:
            target (BaseCharacter): Target to check
            battle_manager: Reference to battle manager (optional)
            
        Returns:
            bool: True if target is visible
        """
        if not target or not target.is_alive():
            return False
        
        # Use battle manager if provided (for grid-based line of sight)
        if battle_manager and hasattr(battle_manager, 'movement_controller'):
            grid = battle_manager.movement_controller.combat_grid
            
            # Convert positions to grid coordinates
            if self not in grid.entity_positions or target not in grid.entity_positions:
                return False
                
            start_cell = grid.entity_positions[self]
            end_cell = grid.entity_positions[target]
            
            # Simple line of sight check using Bresenham's line algorithm
            return self._has_line_of_sight(grid, start_cell, end_cell)
        
        # Without grid, assume line of sight if in range
        return self.is_in_range(target)

    def _has_line_of_sight(self, grid, start_cell, end_cell):
        """
        Check if there is line of sight between two grid cells
        
        Args:
            grid (CombatGrid): The combat grid
            start_cell (tuple): (row, col) starting coordinates
            end_cell (tuple): (row, col) ending coordinates
            
        Returns:
            bool: True if there is line of sight
        """
        # Bresenham's line algorithm for line of sight check
        x0, y0 = start_cell[1], start_cell[0]  # Convert row,col to x,y
        x1, y1 = end_cell[1], end_cell[0]
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while x0 != x1 or y0 != y1:
            # Skip start and end cells
            if (y0, x0) != start_cell and (y0, x0) != end_cell:
                # Check if cell blocks line of sight
                cell_type = grid.get_cell_type((y0, x0))
                if cell_type == grid.CellType.OBSTACLE:
                    return False
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        
        return True

    def update(self, delta_time):
        """
        Update character state for real-time combat
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0, self.attack_cooldown - delta_time)
        
        # Check elapsed time since state change
        current_time = time.time()
        state_elapsed_time = current_time - self.state_start_time
        
        # Handle state transitions based on timing
        if self.combat_state == CombatState.WIND_UP:
            if state_elapsed_time >= self.attack_phase.wind_up_time:
                # Transition to attack phase
                self.combat_state = CombatState.ATTACK
                self.state_start_time = current_time
                
                # If we have a current target, complete the attack
                if self.current_target and self.current_target.is_alive():
                    self.complete_attack(self.current_target)
                else:
                    # No valid target, go straight to recovery
                    self.combat_state = CombatState.RECOVERY
                    self.state_start_time = current_time
        
        elif self.combat_state == CombatState.ATTACK:
            if state_elapsed_time >= self.attack_phase.attack_time:
                # Transition to recovery phase
                self.combat_state = CombatState.RECOVERY
                self.state_start_time = current_time
        
        elif self.combat_state == CombatState.RECOVERY:
            if state_elapsed_time >= self.attack_phase.recovery_time:
                # Return to idle state
                self.combat_state = CombatState.IDLE
                self.current_target = None
        
        elif self.combat_state == CombatState.STAGGERED:
            # Staggered state lasts a fixed time (0.5 seconds)
            if state_elapsed_time >= 0.5:
                self.combat_state = CombatState.IDLE
        
        elif self.combat_state == CombatState.KNOCKED_BACK:
            # Knocked back state lasts a fixed time (0.5 seconds)
            if state_elapsed_time >= 0.5:
                self.combat_state = CombatState.IDLE
        
        elif self.combat_state == CombatState.STUNNED:
            # Stunned state lasts a fixed time (2.0 seconds)
            if state_elapsed_time >= 2.0:
                self.combat_state = CombatState.IDLE
        
        # Handle movement if we have a target position and we're moving
        if self.is_moving and self.target_position:
            direction = self.target_position - self.position
            distance = direction.length()
            
            # If we're close enough, stop moving
            if distance < 5:
                self.is_moving = False
                self.target_position = None
            else:
                # Normalize direction and apply movement
                if distance > 0:
                    direction.normalize_ip()
                    move_distance = self.movement_speed * delta_time
                    move_distance = min(move_distance, distance)  # Don't overshoot
                    self.position += direction * move_distance
    
    def complete_attack(self, target):
        """
        Complete an attack sequence against a target
        
        Args:
            target (BaseCharacter): The target of the attack
            
        Returns:
            dict: Attack result containing damage and effects
        """
        # Calculate base damage
        base_damage = self.attack
        
        # Apply damage to target
        result = target.take_damage(base_damage)
        
        # Set cooldown for next attack
        self.attack_cooldown = self.get_attack_cooldown()
        
        # Reset combat state
        self.combat_state = CombatState.RECOVERY
        self.state_start_time = time.time()
        
        return result
    
    @abstractmethod
    def take_damage(self, damage, damage_type="physical"):
        """
        Take damage from an attack
        
        Args:
            damage (int): Amount of damage
            damage_type (str): Type of damage ("physical" or "magical")
            
        Returns:
            dict: Damage result containing actual damage taken and effects
        """
        if not self.is_alive():
            return {"damage": 0, "hit": False}
        
        # Check for possible interrupt
        if self.combat_state in [CombatState.WIND_UP, CombatState.CASTING] and self.can_be_interrupted:
            # Higher damage increases chance of interrupt
            interrupt_chance = min(0.8, damage / (self.max_hp * 0.5))
            
            # Resistance reduces interrupt chance
            interrupt_chance = max(0.0, interrupt_chance - (self.interrupt_resistance / 100.0))
            
            # Roll for interrupt
            if pygame.time.get_ticks() % 100 / 100 < interrupt_chance:
                self.interrupt()
        
        # Calculate damage reduction
        damage_reduction = self.defense
        
        # Calculate actual damage
        actual_damage = max(1, int(damage - damage_reduction))
        
        # Apply damage
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        # Check if dead
        if self.current_hp <= 0:
            self.alive = False
            self.combat_state = CombatState.IDLE  # Reset state on death
        
        return {"damage": actual_damage, "hit": True}
    
    def interrupt(self):
        """
        Interrupt the character's current action
        
        Returns:
            bool: True if interrupt was successful
        """
        if not self.can_be_interrupted:
            return False
            
        # Only certain states can be interrupted
        if self.combat_state in [CombatState.WIND_UP, CombatState.CASTING, CombatState.RECOVERY]:
            # Reset to idle state
            self.combat_state = CombatState.STAGGERED
            self.state_start_time = time.time()
            self.attack_cooldown = self.get_attack_cooldown() * 0.5  # Partial cooldown on interrupt
            return True
            
        return False
    
    def move_to(self, target_position):
        """
        Begin moving to a target position
        
        Args:
            target_position (pygame.Vector2): Target position to move to
            
        Returns:
            bool: True if movement was initiated
        """
        # Only idle characters can start moving
        if self.combat_state != CombatState.IDLE:
            return False
        
        self.target_position = pygame.Vector2(target_position)
        self.is_moving = True
        return True
    
    def move_towards_target(self, target, preferred_distance=None):
        """
        Move towards a target character
        
        Args:
            target (BaseCharacter): Target character to move towards
            preferred_distance (float, optional): Preferred distance to maintain
            
        Returns:
            bool: True if movement was initiated
        """
        if not target or not target.is_alive():
            return False
        
        if preferred_distance is None:
            # Default to attack range
            preferred_distance = self.attack_range * 0.8
        
        # Calculate direction to target
        direction = target.position - self.position
        distance = direction.length()
        
        # If we're already at preferred distance, don't move
        if abs(distance - preferred_distance) < 10:
            self.is_moving = False
            return False
        
        # Calculate target position
        if distance > 0:
            direction.normalize_ip()
            if distance > preferred_distance:
                # Move closer
                target_pos = self.position + direction * (distance - preferred_distance)
            else:
                # Move away
                target_pos = self.position - direction * (preferred_distance - distance)
            
            return self.move_to(target_pos)
        
        return False
    
    def render(self, screen, position=None):
        """
        Render the character
        
        Args:
            screen (pygame.Surface): Screen to render to
            position (tuple, optional): Position override
        """
        if position:
            self.position = pygame.Vector2(position)
        
        # If there's a sprite, render it
        if self.sprite:
            # Check if character is alive
            if self.is_alive():
                # Normal rendering
                screen.blit(self.sprite, self.position)
                
                # Render combat state indicator
                self._render_state_indicator(screen)
            else:
                # For defeated characters, render with reduced alpha
                sprite_copy = self.sprite.copy()
                sprite_copy.set_alpha(128)  # Semi-transparent
                screen.blit(sprite_copy, self.position)
                
                # Draw an X over defeated characters
                x1 = self.position[0]
                y1 = self.position[1]
                x2 = x1 + self.sprite.get_width()
                y2 = y1 + self.sprite.get_height()
                
                pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 2)
                pygame.draw.line(screen, (255, 0, 0), (x1, y2), (x2, y1), 2)
    
    def _render_state_indicator(self, screen):
        """
        Render an indicator for the current combat state
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        indicator_size = 10
        x = self.position[0] + self.sprite.get_width() // 2
        y = self.position[1] - indicator_size - 5
        
        if self.combat_state == CombatState.IDLE:
            # No indicator for idle state
            pass
        elif self.combat_state == CombatState.WIND_UP:
            # Yellow circle for wind-up
            pygame.draw.circle(screen, (255, 255, 0), (x, y), indicator_size)
        elif self.combat_state == CombatState.ATTACK:
            # Red circle for attack
            pygame.draw.circle(screen, (255, 0, 0), (x, y), indicator_size)
        elif self.combat_state == CombatState.RECOVERY:
            # Blue circle for recovery
            pygame.draw.circle(screen, (0, 0, 255), (x, y), indicator_size)
        elif self.combat_state == CombatState.STAGGERED:
            # Gray circle for staggered
            pygame.draw.circle(screen, (150, 150, 150), (x, y), indicator_size)
        elif self.combat_state == CombatState.DODGING:
            # Green circle for dodging
            pygame.draw.circle(screen, (0, 255, 0), (x, y), indicator_size)
        elif self.combat_state == CombatState.PARRYING:
            # White circle for parrying
            pygame.draw.circle(screen, (255, 255, 255), (x, y), indicator_size)
        elif self.combat_state == CombatState.CASTING:
            # Purple circle for casting
            pygame.draw.circle(screen, (128, 0, 128), (x, y), indicator_size)
    
    def get_animation_type(self):
        """
        Get the appropriate animation type for this character
        
        Returns:
            str: Animation type ("slash", "arrow", "spell")
        """
        # Default implementation, overridden by subclasses
        return "slash"

    def can_attack(self):
        """
        Check if character can initiate an attack
        
        Returns:
            bool: True if can attack, False otherwise
        """
        return (self.attack_cooldown <= 0 and 
                self.alive and 
                self.combat_state == CombatState.IDLE)
    
    def is_attacking(self):
        """
        Check if character is currently in attack sequence
        
        Returns:
            bool: True if in attack sequence
        """
        return self.combat_state in [CombatState.WIND_UP, CombatState.ATTACK, CombatState.RECOVERY]
    
    def get_attack_progress(self):
        """
        Get the progress of the current attack sequence
        
        Returns:
            float: Progress from 0.0 to 1.0, or None if not attacking
        """
        if not self.is_attacking():
            return None
        
        current_time = time.time()
        elapsed = current_time - self.state_start_time
        
        if self.combat_state == CombatState.WIND_UP:
            return min(1.0, elapsed / self.attack_phase.wind_up_time)
        elif self.combat_state == CombatState.ATTACK:
            return min(1.0, elapsed / self.attack_phase.attack_time)
        elif self.combat_state == CombatState.RECOVERY:
            return min(1.0, elapsed / self.attack_phase.recovery_time)
        
        return None
    
    def is_alive(self):
        """Check if character is alive"""
        return self.current_hp > 0 and self.alive
    
    def gain_xp(self, amount):
        """
        Gain experience points and level up if needed
        
        Args:
            amount (int): Amount of XP to gain
            
        Returns:
            bool: True if leveled up, False otherwise
        """
        self.xp += amount
        leveled_up = False
        
        # Check for level up
        while self.xp >= self.xp_to_next_level:
            self.level_up()
            leveled_up = True
        
        return leveled_up
    
    def level_up(self):
        """Level up the character and increase stats"""
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = self._calculate_xp_for_level(self.level + 1)
        
        # Recalculate stats
        old_max_hp = self.max_hp
        self.max_hp = self._calculate_max_hp()
        self.attack = self._calculate_attack()
        self.defense = self._calculate_defense()
        self.magic = self._calculate_magic()
        self.speed = self._calculate_speed()
        
        # Heal on level up (only the difference in max HP)
        self.current_hp += (self.max_hp - old_max_hp)
        
        # Update attack phase timing
        self.attack_phase = self._create_default_attack_phase()
        
        # Update interrupt resistance and movement speed
        self.interrupt_resistance = self.defense * 0.1
        self.movement_speed = self.speed * 0.5
        
        print(f"{self.name} leveled up to level {self.level}!")
    
    def heal(self, amount):
        """
        Heal the character
        
        Args:
            amount (int): Amount to heal
            
        Returns:
            int: Actual amount healed
        """
        if not self.is_alive():
            return 0
        
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
    
    def get_attack_cooldown(self):
        """
        Calculate attack cooldown based on speed
        
        Returns:
            float: Cooldown time in seconds
        """
        # Higher speed means lower cooldown
        cooldown = ATTACK_COOLDOWN_BASE * (1 - (self.speed / 100))
        # Ensure cooldown is at least 0.2 seconds
        return max(0.2, cooldown)
    
    def is_in_range(self, target):
        """
        Check if target is within attack range
        
        Args:
            target (BaseCharacter): Target to check
            
        Returns:
            bool: True if in range
        """
        if not target:
            return False
            
        # Calculate distance between characters
        direction = target.position - self.position
        distance = direction.length()
        
        # Compare with attack range
        return distance <= self.attack_range
    
    def _calculate_xp_for_level(self, level):
        """
        Calculate XP required for a given level
        
        Args:
            level (int): The level to calculate XP for
            
        Returns:
            int: XP required to reach this level
        """
        return int(XP_PER_LEVEL * (level ** XP_LEVEL_MULTIPLIER))
    
    def _calculate_max_hp(self):
        """Calculate max HP based on level and base stats"""
        return int(self.base_hp * (1 + 0.1 * (self.level - 1)))
    
    def _calculate_attack(self):
        """Calculate attack based on level and base stats"""
        return int(self.base_attack * (1 + 0.1 * (self.level - 1)))
    
    def _calculate_defense(self):
        """Calculate defense based on level and base stats"""
        return int(self.base_defense * (1 + 0.1 * (self.level - 1)))
    
    def _calculate_magic(self):
        """Calculate magic based on level and base stats"""
        return int(self.base_magic * (1 + 0.1 * (self.level - 1)))
    
    def _calculate_speed(self):
        """Calculate speed based on level and base stats"""
        return int(self.base_speed * (1 + 0.05 * (self.level - 1)))
    
    def to_dict(self):
        """
        Convert character to dictionary for serialization
        
        Returns:
            dict: Character data
        """
        return {
            "name": self.name,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
            "base_hp": self.base_hp,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "base_magic": self.base_magic,
            "base_speed": self.base_speed,
            "current_hp": self.current_hp
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create character from dictionary
        
        Args:
            data (dict): Character data
            
        Returns:
            BaseCharacter: Character instance
        """
        character = cls(data["name"], data["level"])
        character.xp = data["xp"]
        character.xp_to_next_level = data["xp_to_next_level"]
        character.base_hp = data["base_hp"]
        character.base_attack = data["base_attack"]
        character.base_defense = data["base_defense"]
        character.base_magic = data["base_magic"]
        character.base_speed = data["base_speed"]
        
        # Recalculate derived stats
        character.max_hp = character._calculate_max_hp()
        character.attack = character._calculate_attack()
        character.defense = character._calculate_defense()
        character.magic = character._calculate_magic()
        character.speed = character._calculate_speed()
        
        # Update attack phase timing
        character.attack_phase = character._create_default_attack_phase()
        
        # Set current state
        character.current_hp = data["current_hp"]
        character.alive = character.current_hp > 0
        character.combat_state = CombatState.IDLE
        
        return character