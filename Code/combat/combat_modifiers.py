"""
Combat Modifiers - Handles situational combat bonuses and penalties
"""
import math

class CombatModifierType:
    """Types of modifiers that can be applied to combat"""
    DAMAGE = "damage"           # Damage dealt/taken
    HIT_CHANCE = "hit_chance"   # Chance to hit
    CRIT_CHANCE = "crit_chance" # Chance for critical hits
    DODGE = "dodge"             # Chance to dodge
    DEFENSE = "defense"         # Defense bonus/penalty
    SPEED = "speed"             # Speed bonus/penalty
    COOLDOWN = "cooldown"       # Attack cooldown
    RANGE = "range"             # Attack range

class CombatModifierSource:
    """Sources of combat modifiers"""
    FLANKING = "flanking"       # Attacking from flank
    HIGH_GROUND = "high_ground" # Attacking from elevated position
    COVER = "cover"             # In cover
    TERRAIN = "terrain"         # Special terrain effect
    STATUS = "status"           # Status effect
    FORMATION = "formation"     # Formation bonus
    ABILITY = "ability"         # Special ability
    EQUIPMENT = "equipment"     # Equipment bonus

class CombatModifier:
    """
    Individual combat modifier
    """
    def __init__(self, modifier_type, value, source, duration=None, description=None):
        """
        Initialize a combat modifier
        
        Args:
            modifier_type (str): Type of modifier (use CombatModifierType constants)
            value (float): Modifier value (bonus or penalty)
            source (str): Source of modifier (use CombatModifierSource constants)
            duration (float, optional): Duration in seconds or None for permanent
            description (str, optional): Description of the modifier
        """
        self.type = modifier_type
        self.value = value
        self.source = source
        self.duration = duration
        self.description = description
        self.time_remaining = duration
    
    def update(self, delta_time):
        """
        Update time-based modifiers
        
        Args:
            delta_time (float): Time since last update in seconds
            
        Returns:
            bool: True if still active, False if expired
        """
        if self.duration is None:
            return True
            
        self.time_remaining -= delta_time
        return self.time_remaining > 0
    
    def get_formatted_description(self):
        """
        Get a formatted description of the modifier
        
        Returns:
            str: Formatted description
        """
        if self.description:
            return self.description
            
        # Generate a description based on type and value
        sign = "+" if self.value > 0 else ""
        
        if self.type == CombatModifierType.DAMAGE:
            if isinstance(self.value, float):
                return f"{sign}{self.value:.0%} {self.source} damage"
            else:
                return f"{sign}{self.value} {self.source} damage"
        
        elif self.type == CombatModifierType.HIT_CHANCE:
            return f"{sign}{self.value:.0%} {self.source} hit chance"
        
        elif self.type == CombatModifierType.CRIT_CHANCE:
            return f"{sign}{self.value:.0%} {self.source} critical chance"
        
        elif self.type == CombatModifierType.DODGE:
            return f"{sign}{self.value:.0%} {self.source} dodge chance"
        
        elif self.type == CombatModifierType.DEFENSE:
            return f"{sign}{self.value} {self.source} defense"
        
        elif self.type == CombatModifierType.SPEED:
            return f"{sign}{self.value} {self.source} speed"
        
        elif self.type == CombatModifierType.COOLDOWN:
            modifier = "faster" if self.value < 0 else "slower"
            return f"{abs(self.value):.0%} {modifier} cooldown from {self.source}"
        
        elif self.type == CombatModifierType.RANGE:
            return f"{sign}{self.value} {self.source} range"
        
        else:
            return f"{self.source} modifier: {sign}{self.value}"

class ModifierManager:
    """
    Manages combat modifiers for entities
    """
    def __init__(self):
        """Initialize the modifier manager"""
        self.entity_modifiers = {}  # entity -> {modifier_type -> [modifiers]}
    
    def add_modifier(self, entity, modifier):
        """
        Add a modifier to an entity
        
        Args:
            entity: The entity to modify
            modifier (CombatModifier): The modifier to add
            
        Returns:
            bool: True if added
        """
        # Initialize if needed
        if entity not in self.entity_modifiers:
            self.entity_modifiers[entity] = {}
        
        # Initialize modifier type list if needed
        if modifier.type not in self.entity_modifiers[entity]:
            self.entity_modifiers[entity][modifier.type] = []
        
        # Add modifier
        self.entity_modifiers[entity][modifier.type].append(modifier)
        
        return True
    
    def remove_modifier(self, entity, modifier):
        """
        Remove a specific modifier from an entity
        
        Args:
            entity: The entity to modify
            modifier (CombatModifier): The modifier to remove
            
        Returns:
            bool: True if removed
        """
        if (entity in self.entity_modifiers and 
            modifier.type in self.entity_modifiers[entity] and
            modifier in self.entity_modifiers[entity][modifier.type]):
            
            self.entity_modifiers[entity][modifier.type].remove(modifier)
            return True
            
        return False
    
    def remove_modifiers_by_source(self, entity, source):
        """
        Remove all modifiers from a specific source
        
        Args:
            entity: The entity to modify
            source (str): The source to remove
            
        Returns:
            int: Number of modifiers removed
        """
        if entity not in self.entity_modifiers:
            return 0
            
        removed_count = 0
        
        for modifier_type in list(self.entity_modifiers[entity].keys()):
            # Create a copy of the list to safely remove items during iteration
            modifiers = list(self.entity_modifiers[entity][modifier_type])
            
            for modifier in modifiers:
                if modifier.source == source:
                    self.entity_modifiers[entity][modifier_type].remove(modifier)
                    removed_count += 1
        
        return removed_count
    
    def clear_modifiers(self, entity):
        """
        Clear all modifiers for an entity
        
        Args:
            entity: The entity to clear
            
        Returns:
            int: Number of modifiers cleared
        """
        if entity not in self.entity_modifiers:
            return 0
            
        # Count total modifiers
        count = sum(len(modifiers) for modifiers in self.entity_modifiers[entity].values())
        
        # Clear all modifiers
        self.entity_modifiers[entity] = {}
        
        return count
    
    def get_modifier_value(self, entity, modifier_type):
        """
        Get the total value of all modifiers of a specific type
        
        Args:
            entity: The entity to check
            modifier_type (str): Type of modifier
            
        Returns:
            float: Total modifier value
        """
        if entity not in self.entity_modifiers:
            return 0
            
        if modifier_type not in self.entity_modifiers[entity]:
            return 0
            
        # Sum all modifier values
        total = 0
        for modifier in self.entity_modifiers[entity][modifier_type]:
            total += modifier.value
            
        return total
    
    def get_modifiers(self, entity, modifier_type=None):
        """
        Get all modifiers for an entity
        
        Args:
            entity: The entity to check
            modifier_type (str, optional): Type of modifier or None for all
            
        Returns:
            list: List of modifiers
        """
        if entity not in self.entity_modifiers:
            return []
            
        if modifier_type is not None:
            return self.entity_modifiers[entity].get(modifier_type, [])
            
        # Return all modifiers
        all_modifiers = []
        for modifiers in self.entity_modifiers[entity].values():
            all_modifiers.extend(modifiers)
            
        return all_modifiers
    
    def update(self, delta_time):
        """
        Update all time-based modifiers
        
        Args:
            delta_time (float): Time since last update in seconds
            
        Returns:
            int: Number of expired modifiers removed
        """
        removed_count = 0
        
        for entity in list(self.entity_modifiers.keys()):
            for modifier_type in list(self.entity_modifiers[entity].keys()):
                # Create a copy of the list to safely remove items during iteration
                modifiers = list(self.entity_modifiers[entity][modifier_type])
                
                for modifier in modifiers:
                    if not modifier.update(delta_time):
                        # Modifier expired
                        self.entity_modifiers[entity][modifier_type].remove(modifier)
                        removed_count += 1
        
        return removed_count
    
    def apply_flanking_bonus(self, attacker, target):
        """
        Apply flanking bonus to an attacker
        
        Args:
            attacker: The attacking entity
            target: The target entity
            
        Returns:
            bool: True if bonus applied
        """
        # Check if already has a flanking bonus
        existing_modifiers = self.get_modifiers(attacker)
        for modifier in existing_modifiers:
            if modifier.source == CombatModifierSource.FLANKING:
                return False
        
        # Create flanking modifiers
        hit_modifier = CombatModifier(
            CombatModifierType.HIT_CHANCE, 
            0.15,  # +15% hit chance
            CombatModifierSource.FLANKING,
            10.0,  # 10 second duration
            "Flanking: +15% hit chance"
        )
        
        crit_modifier = CombatModifier(
            CombatModifierType.CRIT_CHANCE,
            0.1,  # +10% crit chance
            CombatModifierSource.FLANKING,
            10.0,  # 10 second duration
            "Flanking: +10% critical chance"
        )
        
        # Add modifiers
        self.add_modifier(attacker, hit_modifier)
        self.add_modifier(attacker, crit_modifier)
        
        return True
    
    def apply_high_ground_bonus(self, attacker, target):
        """
        Apply high ground bonus to an attacker
        
        Args:
            attacker: The attacking entity
            target: The target entity
            
        Returns:
            bool: True if bonus applied
        """
        # Check if already has a high ground bonus
        existing_modifiers = self.get_modifiers(attacker)
        for modifier in existing_modifiers:
            if modifier.source == CombatModifierSource.HIGH_GROUND:
                return False
        
        # Create high ground modifiers
        hit_modifier = CombatModifier(
            CombatModifierType.HIT_CHANCE, 
            0.2,  # +20% hit chance
            CombatModifierSource.HIGH_GROUND,
            None,  # Permanent until position changes
            "High Ground: +20% hit chance"
        )
        
        damage_modifier = CombatModifier(
            CombatModifierType.DAMAGE,
            0.15,  # +15% damage
            CombatModifierSource.HIGH_GROUND,
            None,  # Permanent until position changes
            "High Ground: +15% damage"
        )
        
        range_modifier = CombatModifier(
            CombatModifierType.RANGE,
            30,  # +30 range
            CombatModifierSource.HIGH_GROUND,
            None,  # Permanent until position changes
            "High Ground: +30 range"
        )
        
        # Add modifiers
        self.add_modifier(attacker, hit_modifier)
        self.add_modifier(attacker, damage_modifier)
        self.add_modifier(attacker, range_modifier)
        
        return True
    
    def apply_formation_bonus(self, entity, formation_type):
        """
        Apply formation bonus to an entity
        
        Args:
            entity: The entity to receive the bonus
            formation_type (str): Type of formation
            
        Returns:
            bool: True if bonus applied
        """
        # Remove any existing formation bonuses
        self.remove_modifiers_by_source(entity, CombatModifierSource.FORMATION)
        
        # Create formation modifiers based on formation type
        from combat.formation_system import FormationType
        
        if formation_type == FormationType.LINE:
            # Line formation gives defensive bonus
            modifier = CombatModifier(
                CombatModifierType.DEFENSE,
                2,  # +2 defense
                CombatModifierSource.FORMATION,
                None,  # Permanent until formation changes
                "Line Formation: +2 defense"
            )
            self.add_modifier(entity, modifier)
            
        elif formation_type == FormationType.TRIANGLE:
            # Triangle formation gives varied bonuses by position
            # Front character gets defense, back characters get range
            # This requires knowing position in formation, simplified here
            modifier = CombatModifier(
                CombatModifierType.DEFENSE,
                3,  # +3 defense
                CombatModifierSource.FORMATION,
                None,  # Permanent until formation changes
                "Triangle Formation: +3 defense"
            )
            self.add_modifier(entity, modifier)
            
        elif formation_type == FormationType.SPREAD:
            # Spread formation gives dodge bonus
            modifier = CombatModifier(
                CombatModifierType.DODGE,
                0.1,  # +10% dodge
                CombatModifierSource.FORMATION,
                None,  # Permanent until formation changes
                "Spread Formation: +10% dodge"
            )
            self.add_modifier(entity, modifier)
            
        elif formation_type == FormationType.CIRCLE:
            # Circle formation gives all-around defense
            modifier = CombatModifier(
                CombatModifierType.DEFENSE,
                1,  # +1 defense
                CombatModifierSource.FORMATION,
                None,  # Permanent until formation changes
                "Circle Formation: +1 defense"
            )
            self.add_modifier(entity, modifier)
            
        elif formation_type == FormationType.FLANK:
            # Flank formation gives flanking bonus
            modifier = CombatModifier(
                CombatModifierType.HIT_CHANCE,
                0.05,  # +5% hit chance
                CombatModifierSource.FORMATION,
                None,  # Permanent until formation changes
                "Flank Formation: +5% hit chance"
            )
            self.add_modifier(entity, modifier)
            
        elif formation_type == FormationType.WEDGE:
            # Wedge formation gives offensive bonus
            modifier = CombatModifier(
                CombatModifierType.DAMAGE,
                0.1,  # +10% damage
                CombatModifierSource.FORMATION,
                None,  # Permanent until formation changes
                "Wedge Formation: +10% damage"
            )
            self.add_modifier(entity, modifier)
            
        else:
            return False
            
        return True