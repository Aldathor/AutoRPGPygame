"""
Area of Effect System - Implements area-based abilities and attacks
"""
import math
import pygame
from enum import Enum, auto
from combat.combat_state import CombatState

class AoEShape(Enum):
    """Types of area of effect shapes"""
    CIRCLE = auto()      # Circular area (radius)
    CONE = auto()        # Cone/triangle area (range, angle)
    LINE = auto()        # Line area (length, width)
    SQUARE = auto()      # Square area (size)
    RECTANGLE = auto()   # Rectangular area (width, height)

class AoEEffect:
    """Base class for area effects"""
    def __init__(self, name, shape, params, duration=0.0, color=(255, 0, 0, 128)):
        """
        Initialize area effect
        
        Args:
            name (str): Name of the effect
            shape (AoEShape): Shape of the area
            params (dict): Parameters defining the area size
                - Circle: {"radius": float}
                - Cone: {"range": float, "angle": float (in degrees)}
                - Line: {"length": float, "width": float}
                - Square: {"size": float}
                - Rectangle: {"width": float, "height": float}
            duration (float): Duration in seconds (0 for instant)
            color (tuple): RGBA color
        """
        self.name = name
        self.shape = shape
        self.params = params
        self.duration = duration
        self.color = color
        self.position = (0, 0)
        self.direction = (1, 0)  # Unit vector for directional effects
        self.owner = None
        self.time_remaining = duration
        self.active = False
        
        # Effect-specific properties
        self.damage = 0
        self.damage_type = "physical"
        self.status_effects = []  # List of (effect_type, chance, duration)
    
    def set_position(self, position, direction=None):
        """
        Set the position and direction of the effect
        
        Args:
            position (tuple): (x, y) position
            direction (tuple, optional): (dx, dy) direction vector
        """
        self.position = position
        if direction is not None:
            # Normalize direction
            length = math.sqrt(direction[0]**2 + direction[1]**2)
            if length > 0:
                self.direction = (direction[0] / length, direction[1] / length)
    
    def set_damage(self, damage, damage_type="physical"):
        """
        Set damage for this effect
        
        Args:
            damage (int): Damage amount
            damage_type (str): Type of damage
        """
        self.damage = damage
        self.damage_type = damage_type
    
    def add_status_effect(self, effect_type, chance=1.0, duration=5.0):
        """
        Add a status effect to this area effect
        
        Args:
            effect_type (str): Type of status effect
            chance (float): Chance to apply (0.0-1.0)
            duration (float): Duration in seconds
        """
        self.status_effects.append((effect_type, chance, duration))
    
    def activate(self, owner=None):
        """
        Activate this effect
        
        Args:
            owner: Entity that created this effect
        """
        self.owner = owner
        self.active = True
        self.time_remaining = self.duration
    
    def update(self, delta_time):
        """
        Update effect state
        
        Args:
            delta_time (float): Time since last update
            
        Returns:
            bool: True if effect is still active
        """
        if not self.active:
            return False
            
        if self.duration <= 0:
            # Instant effect
            self.active = False
            return False
            
        self.time_remaining -= delta_time
        if self.time_remaining <= 0:
            self.active = False
            return False
            
        return True
    
    def contains_point(self, point):
        """
        Check if a point is within this effect's area
        
        Args:
            point (tuple): (x, y) point to check
            
        Returns:
            bool: True if point is in area
        """
        x, y = point
        px, py = self.position
        
        if self.shape == AoEShape.CIRCLE:
            # Circle check
            radius = self.params.get("radius", 0)
            distance = math.sqrt((x - px)**2 + (y - py)**2)
            return distance <= radius
            
        elif self.shape == AoEShape.CONE:
            # Cone check
            cone_range = self.params.get("range", 0)
            cone_angle = math.radians(self.params.get("angle", 90))
            
            # Vector from cone origin to point
            dx, dy = x - px, y - py
            
            # Distance from cone origin
            distance = math.sqrt(dx**2 + dy**2)
            if distance > cone_range:
                return False
                
            # Angle between cone direction and point
            dot_product = dx * self.direction[0] + dy * self.direction[1]
            point_angle = math.acos(max(-1.0, min(1.0, dot_product / distance)))
            
            # Point is in cone if angle is less than half the cone angle
            return point_angle <= cone_angle / 2
            
        elif self.shape == AoEShape.LINE:
            # Line check
            length = self.params.get("length", 0)
            width = self.params.get("width", 0)
            
            # Calculate end point of line
            ex, ey = px + self.direction[0] * length, py + self.direction[1] * length
            
            # Calculate distance from point to line segment
            line_length_squared = (ex - px)**2 + (ey - py)**2
            if line_length_squared == 0:
                # Line is actually a point
                distance = math.sqrt((x - px)**2 + (y - py)**2)
                return distance <= width / 2
                
            # Calculate projection of point onto line
            t = max(0, min(1, ((x - px) * (ex - px) + (y - py) * (ey - py)) / line_length_squared))
            
            # Calculate closest point on line
            closest_x = px + t * (ex - px)
            closest_y = py + t * (ey - py)
            
            # Calculate distance from point to closest point on line
            distance = math.sqrt((x - closest_x)**2 + (y - closest_y)**2)
            
            return distance <= width / 2
            
        elif self.shape == AoEShape.SQUARE:
            # Square check
            size = self.params.get("size", 0) / 2  # Half-size
            
            # Square is always axis-aligned
            return (px - size <= x <= px + size) and (py - size <= y <= py + size)
            
        elif self.shape == AoEShape.RECTANGLE:
            # Rectangle check
            width = self.params.get("width", 0) / 2  # Half-width
            height = self.params.get("height", 0) / 2  # Half-height
            
            # Rectangle can be rotated based on direction
            # For simplicity, we'll assume axis-aligned for now
            return (px - width <= x <= px + width) and (py - height <= y <= py + height)
            
        return False
    
    def affect_entities(self, entities, battle_manager=None):
        """
        Apply effect to all entities in the area
        
        Args:
            entities (list): List of entities to check
            battle_manager: Reference to battle manager for combat effects
            
        Returns:
            list: List of affected entities
        """
        affected = []
        
        for entity in entities:
            if not entity.is_alive():
                continue
                
            # Check if entity is in effect area
            if hasattr(entity, 'position'):
                position = (entity.position.x, entity.position.y)
                
                if self.contains_point(position):
                    # Apply effect to entity
                    self._apply_to_entity(entity, battle_manager)
                    affected.append(entity)
        
        return affected
    
    def _apply_to_entity(self, entity, battle_manager):
        """
        Apply effect to a specific entity
        
        Args:
            entity: Entity to affect
            battle_manager: Reference to battle manager
        """
        # Apply damage if any
        if self.damage > 0 and self.owner != entity:
            if hasattr(entity, 'take_damage'):
                damage_result = entity.take_damage(self.damage, damage_type=self.damage_type)
                
                # Log the effect
                if battle_manager and hasattr(battle_manager, '_log_message'):
                    if damage_result.get("hit", False):
                        battle_manager._log_message(
                            f"{entity.name} takes {damage_result['damage']} {self.damage_type} damage from {self.name}!")
                
                # Check if entity died
                if not entity.is_alive() and battle_manager:
                    if hasattr(battle_manager, '_log_message'):
                        battle_manager._log_message(f"{entity.name} has been defeated by {self.name}!")
                        
                    # Check if owner should get XP for this
                    if self.owner and hasattr(battle_manager, '_handle_enemy_defeat'):
                        battle_manager._handle_enemy_defeat(entity, self.owner)
        
        # Apply status effects
        import random
        for effect_type, chance, duration in self.status_effects:
            if random.random() < chance:
                self._apply_status_effect(entity, effect_type, duration, battle_manager)
    
    def _apply_status_effect(self, entity, effect_type, duration, battle_manager):
        """
        Apply a status effect to an entity
        
        Args:
            entity: Entity to affect
            effect_type (str): Type of status effect
            duration (float): Duration in seconds
            battle_manager: Reference to battle manager
        """
        # Apply different status effects
        if effect_type == "stun":
            # Set entity to stunned state
            entity.combat_state = CombatState.STUNNED
            entity.state_start_time = pygame.time.get_ticks() / 1000.0
            entity.stun_duration = duration  # Custom property
            
            # Log the effect
            if battle_manager and hasattr(battle_manager, '_log_message'):
                battle_manager._log_message(f"{entity.name} is stunned for {duration:.1f} seconds!")
                
        elif effect_type == "slow":
            # Slow the entity (reduce speed)
            if hasattr(entity, 'speed'):
                # Store original speed if not already stored
                if not hasattr(entity, 'original_speed'):
                    entity.original_speed = entity.speed
                
                # Apply slow effect
                entity.speed = int(entity.original_speed * 0.5)  # 50% slow
                
                # Schedule effect removal
                if battle_manager and hasattr(battle_manager, 'event_queue'):
                    battle_manager.event_queue.schedule(
                        duration, 
                        10,
                        self._remove_slow_effect,
                        entity,
                        battle_manager
                    )
                
                # Log the effect
                if battle_manager and hasattr(battle_manager, '_log_message'):
                    battle_manager._log_message(f"{entity.name} is slowed for {duration:.1f} seconds!")
        
        # Could add more status effects here
    
    def _remove_slow_effect(self, entity, battle_manager):
        """
        Remove slow effect from entity
        
        Args:
            entity: Entity to affect
            battle_manager: Reference to battle manager
        """
        if hasattr(entity, 'original_speed'):
            entity.speed = entity.original_speed
            del entity.original_speed
            
            # Log the effect
            if battle_manager and hasattr(battle_manager, '_log_message'):
                battle_manager._log_message(f"{entity.name} is no longer slowed!")
    
    def render(self, screen):
        """
        Render the area effect
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        if not self.active:
            return
            
        # Create a surface with alpha for the effect
        if self.shape == AoEShape.CIRCLE:
            # Circle effect
            radius = self.params.get("radius", 0)
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, self.color, (radius, radius), radius)
            screen.blit(surface, (self.position[0] - radius, self.position[1] - radius))
            
        elif self.shape == AoEShape.CONE:
            # Cone effect (simplified as a polygon)
            cone_range = self.params.get("range", 0)
            cone_angle = math.radians(self.params.get("angle", 90))
            
            # Create polygon points
            points = [(0, 0)]  # Cone origin
            
            # Number of points to use for the arc
            steps = 10
            for i in range(steps + 1):
                angle = -cone_angle / 2 + i * cone_angle / steps
                
                # Rotate by the direction angle
                dir_angle = math.atan2(self.direction[1], self.direction[0])
                total_angle = dir_angle + angle
                
                # Calculate point on arc
                x = math.cos(total_angle) * cone_range
                y = math.sin(total_angle) * cone_range
                points.append((x, y))
            
            # Create a large enough surface
            surface_size = int(cone_range * 2.2)
            surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
            
            # Draw the cone
            pygame.draw.polygon(surface, self.color, 
                               [(p[0] + surface_size/2, p[1] + surface_size/2) for p in points])
            
            # Blit to screen
            screen.blit(surface, (self.position[0] - surface_size/2, self.position[1] - surface_size/2))
            
        elif self.shape == AoEShape.LINE:
            # Line effect
            length = self.params.get("length", 0)
            width = self.params.get("width", 0)
            
            # Calculate end point
            end_x = self.position[0] + self.direction[0] * length
            end_y = self.position[1] + self.direction[1] * length
            
            # Draw the line
            pygame.draw.line(screen, self.color, self.position, (end_x, end_y), int(width))
            
        elif self.shape == AoEShape.SQUARE:
            # Square effect
            size = self.params.get("size", 0)
            
            # Create a surface
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            surface.fill(self.color)
            
            # Blit to screen
            screen.blit(surface, (self.position[0] - size/2, self.position[1] - size/2))
            
        elif self.shape == AoEShape.RECTANGLE:
            # Rectangle effect
            width = self.params.get("width", 0)
            height = self.params.get("height", 0)
            
            # Create a surface
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            surface.fill(self.color)
            
            # Blit to screen
            screen.blit(surface, (self.position[0] - width/2, self.position[1] - height/2))

class AoEManager:
    """
    Manages area effects in combat
    """
    def __init__(self, battle_manager):
        """
        Initialize the AoE manager
        
        Args:
            battle_manager: Reference to the battle manager
        """
        self.battle_manager = battle_manager
        self.active_effects = []
        
        # Templates for common effects
        self.effect_templates = {
            "fireball": self._create_fireball_template(),
            "ice_storm": self._create_ice_storm_template(),
            "lightning_bolt": self._create_lightning_bolt_template(),
            "heal_circle": self._create_heal_circle_template(),
            "shockwave": self._create_shockwave_template()
        }
    
    def _create_fireball_template(self):
        """Create a fireball effect template"""
        effect = AoEEffect(
            "Fireball",
            AoEShape.CIRCLE,
            {"radius": 80},
            0.0,  # Instant
            (255, 100, 0, 180)  # Orange-red with transparency
        )
        effect.set_damage(40, "fire")
        return effect
    
    def _create_ice_storm_template(self):
        """Create an ice storm effect template"""
        effect = AoEEffect(
            "Ice Storm",
            AoEShape.CIRCLE,
            {"radius": 100},
            5.0,  # Lasts 5 seconds
            (100, 200, 255, 150)  # Light blue with transparency
        )
        effect.set_damage(10, "ice")  # Damage per second
        effect.add_status_effect("slow", 0.8, 3.0)  # 80% chance to slow for 3 seconds
        return effect
    
    def _create_lightning_bolt_template(self):
        """Create a lightning bolt effect template"""
        effect = AoEEffect(
            "Lightning Bolt",
            AoEShape.LINE,
            {"length": 300, "width": 30},
            0.0,  # Instant
            (200, 200, 255, 200)  # Light purple with transparency
        )
        effect.set_damage(50, "lightning")
        effect.add_status_effect("stun", 0.3, 1.0)  # 30% chance to stun for 1 second
        return effect
    
    def _create_heal_circle_template(self):
        """Create a healing circle effect template"""
        effect = AoEEffect(
            "Healing Circle",
            AoEShape.CIRCLE,
            {"radius": 60},
            0.0,  # Instant
            (0, 255, 100, 150)  # Green with transparency
        )
        # Healing is handled differently
        return effect
    
    def _create_shockwave_template(self):
        """Create a shockwave effect template"""
        effect = AoEEffect(
            "Shockwave",
            AoEShape.CIRCLE,
            {"radius": 120},
            0.0,  # Instant
            (150, 150, 150, 150)  # Gray with transparency
        )
        effect.set_damage(20, "physical")
        effect.add_status_effect("stun", 0.5, 2.0)  # 50% chance to stun for 2 seconds
        return effect
    
    def create_effect(self, effect_name, position, direction=(1, 0), owner=None):
        """
        Create a new effect from a template
        
        Args:
            effect_name (str): Name of effect template
            position (tuple): (x, y) position for effect
            direction (tuple): (dx, dy) direction vector
            owner: Entity that created this effect
            
        Returns:
            AoEEffect: Created effect or None if template not found
        """
        if effect_name not in self.effect_templates:
            return None
            
        # Create a copy of the template
        template = self.effect_templates[effect_name]
        
        effect = AoEEffect(
            template.name,
            template.shape,
            template.params.copy(),
            template.duration,
            template.color
        )
        
        # Copy properties
        effect.set_damage(template.damage, template.damage_type)
        for status in template.status_effects:
            effect.add_status_effect(*status)
            
        # Set position and ownership
        effect.set_position(position, direction)
        effect.owner = owner
        
        return effect
    
    def activate_effect(self, effect):
        """
        Activate an effect and add it to active effects
        
        Args:
            effect (AoEEffect): Effect to activate
            
        Returns:
            bool: True if activated
        """
        if not effect:
            return False
            
        # Activate the effect
        effect.activate()
        
        # Add to active effects if duration > 0
        if effect.duration > 0:
            self.active_effects.append(effect)
            
        # Apply instant effect
        if effect.duration <= 0:
            all_entities = []
            
            # Get all entities from the battle
            if hasattr(self.battle_manager, 'game_state'):
                all_entities.extend([char for char in self.battle_manager.game_state.party if char])
                all_entities.extend(self.battle_manager.game_state.enemies)
                
            # Apply effect to all entities
            effect.affect_entities(all_entities, self.battle_manager)
        
        return True
    
    def update(self, delta_time):
        """
        Update all active effects
        
        Args:
            delta_time (float): Time since last update
        """
        # Update all active effects
        for effect in list(self.active_effects):
            if not effect.update(delta_time):
                # Effect ended, remove it
                self.active_effects.remove(effect)
                continue
                
            # Apply effect to all entities
            all_entities = []
            
            # Get all entities from the battle
            if hasattr(self.battle_manager, 'game_state'):
                all_entities.extend([char for char in self.battle_manager.game_state.party if char])
                all_entities.extend(self.battle_manager.game_state.enemies)
                
            # Apply effect to all entities
            effect.affect_entities(all_entities, self.battle_manager)
    
    def render(self, screen):
        """
        Render all active effects
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        for effect in self.active_effects:
            effect.render(screen)
    
    def clear_effects(self):
        """Clear all active effects"""
        self.active_effects = []