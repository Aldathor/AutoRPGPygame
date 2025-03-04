"""
Character Data - Data structures and handling for character persistence
"""

class CharacterData:
    """
    Data structure for character information storage and serialization
    """
    def __init__(self):
        """Initialize character data with default values"""
        # Basic info
        self.name = ""
        self.character_class = ""
        self.level = 1
        
        # Stats
        self.max_hp = 0
        self.current_hp = 0
        self.attack = 0
        self.defense = 0
        self.magic = 0
        self.speed = 0
        
        # Progression
        self.xp = 0
        self.xp_to_next_level = 0
        
        # Base stats (for recalculation)
        self.base_hp = 0
        self.base_attack = 0
        self.base_defense = 0
        self.base_magic = 0
        self.base_speed = 0
    
    @classmethod
    def from_character(cls, character):
        """
        Create a CharacterData object from a character instance
        
        Args:
            character: The character object
            
        Returns:
            CharacterData: The data object
        """
        data = cls()
        
        # Set basic info
        data.name = character.name
        data.level = character.level
        
        # Set class type
        if hasattr(character, '__class__'):
            data.character_class = character.__class__.__name__
        
        # Set stats
        data.max_hp = character.max_hp
        data.current_hp = character.current_hp
        data.attack = character.attack
        data.defense = character.defense
        data.magic = character.magic
        data.speed = character.speed
        
        # Set progression
        data.xp = character.xp
        data.xp_to_next_level = character.xp_to_next_level
        
        # Set base stats
        data.base_hp = character.base_hp
        data.base_attack = character.base_attack
        data.base_defense = character.base_defense
        data.base_magic = character.base_magic
        data.base_speed = character.base_speed
        
        return data
    
    def to_dict(self):
        """
        Convert to dictionary for serialization
        
        Returns:
            dict: Dictionary representation
        """
        return {
            "name": self.name,
            "class": self.character_class,
            "level": self.level,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "attack": self.attack,
            "defense": self.defense,
            "magic": self.magic,
            "speed": self.speed,
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
            "base_hp": self.base_hp,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "base_magic": self.base_magic,
            "base_speed": self.base_speed
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a CharacterData object from a dictionary
        
        Args:
            data (dict): Dictionary with character data
            
        Returns:
            CharacterData: The data object
        """
        char_data = cls()
        
        # Set all attributes from dictionary
        char_data.name = data.get("name", "")
        char_data.character_class = data.get("class", "")
        char_data.level = data.get("level", 1)
        char_data.max_hp = data.get("max_hp", 0)
        char_data.current_hp = data.get("current_hp", 0)
        char_data.attack = data.get("attack", 0)
        char_data.defense = data.get("defense", 0)
        char_data.magic = data.get("magic", 0)
        char_data.speed = data.get("speed", 0)
        char_data.xp = data.get("xp", 0)
        char_data.xp_to_next_level = data.get("xp_to_next_level", 0)
        char_data.base_hp = data.get("base_hp", 0)
        char_data.base_attack = data.get("base_attack", 0)
        char_data.base_defense = data.get("base_defense", 0)
        char_data.base_magic = data.get("base_magic", 0)
        char_data.base_speed = data.get("base_speed", 0)
        
        return char_data
    
    def validate(self):
        """
        Validate character data for consistency
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation rules
        if self.level < 1:
            return False
        
        if self.current_hp > self.max_hp:
            return False
            
        if self.current_hp < 0:
            return False
            
        if self.xp < 0:
            return False
            
        if not self.name:
            return False
            
        if not self.character_class:
            return False
            
        # All validations passed
        return True

def create_character_data(character):
    """
    Create a serializable data representation of a character
    
    Args:
        character: The character object
        
    Returns:
        dict: Serializable character data
    """
    # Create character data object
    char_data = CharacterData.from_character(character)
    
    # Convert to dictionary for serialization
    return char_data.to_dict()

def apply_character_data(character, data):
    """
    Apply saved data to a character object
    
    Args:
        character: The character object to update
        data (dict): Character data dictionary
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create CharacterData object from dict
        char_data = CharacterData.from_dict(data)
        
        # Validate the data
        if not char_data.validate():
            return False
        
        # Apply basic attributes
        character.name = char_data.name
        character.level = char_data.level
        character.xp = char_data.xp
        character.xp_to_next_level = char_data.xp_to_next_level
        
        # Apply base stats
        character.base_hp = char_data.base_hp
        character.base_attack = char_data.base_attack
        character.base_defense = char_data.base_defense
        character.base_magic = char_data.base_magic
        character.base_speed = char_data.base_speed
        
        # Recalculate derived stats
        character.max_hp = character._calculate_max_hp()
        character.attack = character._calculate_attack()
        character.defense = character._calculate_defense()
        character.magic = character._calculate_magic()
        character.speed = character._calculate_speed()
        
        # Set current HP
        character.current_hp = min(char_data.current_hp, character.max_hp)
        
        return True
    except Exception as e:
        print(f"Error applying character data: {e}")
        return False
