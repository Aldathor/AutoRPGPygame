"""
Data Manager - Handles saving and loading game data
"""
import os
import json
from entities.player_classes.warrior import Warrior
from entities.player_classes.archer import Archer
from entities.player_classes.mage import Mage
from game.config import SAVE_FILE_NAME
from data.character_data import CharacterData, create_character_data, apply_character_data

class DataManager:
    """
    Manages saving and loading game data
    """
    def __init__(self):
        """Initialize the data manager"""
        self.save_file = SAVE_FILE_NAME
        self.class_map = {
            "Warrior": Warrior,
            "Archer": Archer,
            "Mage": Mage
        }
    
    def save_game(self, game_state):
        """
        Save the current game state
        
        Args:
            game_state (GameState): The current game state
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Create save data structure
            save_data = {
                "player_character": self._serialize_character(game_state.player_character),
                "victory_count": game_state.victory_count,
                "defeat_count": game_state.defeat_count
            }
            
            # Write to file
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self):
        """
        Load a saved game
        
        Returns:
            dict: Loaded game data or None if failed
        """
        try:
            # Check if save file exists
            if not os.path.exists(self.save_file):
                print("No save file found")
                return None
            
            # Read save data
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            # Deserialize player character
            if "player_character" in save_data:
                character_data = save_data["player_character"]
                character_class = character_data.get("class")
                
                if character_class in self.class_map:
                    # Create character of the correct class
                    class_constructor = self.class_map[character_class]
                    player_character = class_constructor.from_dict(character_data)
                    save_data["player_character"] = player_character
                else:
                    print(f"Unknown character class: {character_class}")
                    return None
            
            return save_data
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def _serialize_character(self, character):
        """
        Serialize a character object for saving
        
        Args:
            character (BaseCharacter): The character to serialize
            
        Returns:
            dict: Serialized character data
        """
        if not character:
            return None
        
        # Use character_data module to create serializable data
        data = create_character_data(character)
        
        # Add class type to ensure proper reconstruction
        if isinstance(character, Warrior):
            data["class"] = "Warrior"
        elif isinstance(character, Archer):
            data["class"] = "Archer"
        elif isinstance(character, Mage):
            data["class"] = "Mage"
        else:
            data["class"] = "Unknown"
        
        return data
