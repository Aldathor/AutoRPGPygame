"""
Updates to the Battle Manager to support party battles
"""
from game.config import BATTLE_TIMER_INTERVAL
from ui.combat_log import CombatLog

class BattleManager:
    """
    Manages battles between party members and enemies
    """
    def __init__(self, game_state):
        """
        Initialize the battle manager
        
        Args:
            game_state (GameState): Reference to the game state
        """
        self.game_state = game_state
        self.combat_log = CombatLog()
        self.last_action_time = 0
        self.target_selection = {
            "active": False,
            "source_character": None,
            "potential_targets": [],
            "callback": None
        }
        
        # Add animation list
        self.animations = []
    
    def update(self, delta_time):
        """
        Update the battle system
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update all combat entities
        for character in self.game_state.party:
            if character and character.is_alive():
                character.update(delta_time)
        
        for enemy in self.game_state.enemies:
            if enemy.is_alive():
                enemy.update(delta_time)
        
        # Update animations
        self.animations = [anim for anim in self.animations if anim.update()]
        
        # Remove dead enemies
        self.game_state.enemies = [enemy for enemy in self.game_state.enemies if enemy.is_alive()]
        
        # Process battle actions based on timer if no animations are playing
        if not self.target_selection["active"] and not self.animations:  # Don't process during animations
            self.last_action_time += delta_time
            if self.last_action_time >= BATTLE_TIMER_INTERVAL:
                self.last_action_time = 0
                self._process_battle_actions()

        print(f"Animations: {len(self.animations)}, Character cooldowns: {[c.attack_cooldown for c in self.game_state.party if c]}")        
    
    def _process_battle_actions(self):
        """Process one round of battle actions"""
        # Skip if no party members are alive or no enemies
        if not self._is_party_alive() or not self.game_state.enemies:
            return
        
        # Skip if animations are currently playing
        if hasattr(self.game_state, 'animation_helper') and self.game_state.animation_helper.attack_animations:
            return
        
        # Process party member actions
        for character in self.game_state.party:
            if character and character.is_alive() and character.can_attack():
                # Auto-select target based on character's role/strategy
                target = self._select_target_for_character(character)
                if target:
                    result = character.attack_target(target)
                    self._log_attack(character, target, result)
                    
                    # Add attack animation if we have an animation helper
                    if hasattr(self.game_state, 'animation_helper'):
                        anim_type = character.get_animation_type()
                        self.game_state.animation_helper.add_attack_animation(character, target, anim_type)
                    
                    # Check if enemy died
                    if not target.is_alive():
                        self._handle_enemy_defeat(target, character)
                    
                    # Only process one character attack at a time
                    return
        
        # Process enemy actions
        for enemy in self.game_state.enemies:
            if enemy.is_alive() and enemy.can_attack():
                # Select target from party
                target = self._select_target_for_enemy(enemy)
                if target:
                    result = enemy.attack_target(target)
                    self._log_attack(enemy, target, result)
                    
                    # Add attack animation if we have an animation helper
                    if hasattr(self.game_state, 'animation_helper'):
                        anim_type = enemy.get_animation_type()
                        self.game_state.animation_helper.add_attack_animation(enemy, target, anim_type)
                    
                    # Check if character died
                    if not target.is_alive():
                        self._log_message(f"{target.name} has been defeated!")
                        
                        # Check if all party members are dead
                        if not self._is_party_alive():
                            self._log_message("The party has been defeated!")
                            break
                    
                    # Only process one enemy attack at a time
                    return
    
    def _is_party_alive(self):
        """Check if any party member is alive"""
        return any(char and char.is_alive() for char in self.game_state.party)
    
    def _select_target_for_character(self, character):
        """
        Select a target for a character to attack
        
        Args:
            character (BaseCharacter): The character selecting a target
            
        Returns:
            Enemy: The selected target
        """
        # For now, simply select the first living enemy
        # This will be replaced with more sophisticated targeting logic
        for enemy in self.game_state.enemies:
            if enemy.is_alive():
                return enemy
        return None
    
    def _select_target_for_enemy(self, enemy):
        """
        Select a target for an enemy to attack
        
        Args:
            enemy (Enemy): The enemy selecting a target
            
        Returns:
            BaseCharacter: The selected target
        """
        # Basic targeting strategy based on enemy type
        # Can be expanded with more sophisticated enemy AI
        living_party = [char for char in self.game_state.party if char and char.is_alive()]
        
        if not living_party:
            return None
            
        # Different enemy types might have different targeting strategies
        if enemy.enemy_type == "goblin":
            # Goblins prefer to attack the weakest target
            return min(living_party, key=lambda char: char.current_hp)
        elif enemy.enemy_type == "orc":
            # Orcs prefer to attack the strongest target
            return max(living_party, key=lambda char: char.attack)
        elif enemy.enemy_type == "dragon":
            # Dragons prefer to attack the character with highest magic (most threat)
            return max(living_party, key=lambda char: char.magic)
        else:
            # Default: random target
            import random
            return random.choice(living_party)
    
    def initiate_target_selection(self, source_character, potential_targets, callback):
        """
        Start the target selection process
        
        Args:
            source_character (BaseCharacter): Character selecting a target
            potential_targets (list): List of potential targets
            callback (function): Function to call with selected target
        """
        self.target_selection = {
            "active": True,
            "source_character": source_character,
            "potential_targets": potential_targets,
            "callback": callback
        }
    
    def select_target(self, target_index):
        """
        Complete target selection
        
        Args:
            target_index (int): Index of selected target
        """
        if not self.target_selection["active"]:
            return
            
        if 0 <= target_index < len(self.target_selection["potential_targets"]):
            target = self.target_selection["potential_targets"][target_index]
            self.target_selection["callback"](target)
            
        # Reset target selection state
        self.target_selection = {
            "active": False,
            "source_character": None,
            "potential_targets": [],
            "callback": None
        }
    
    def _handle_enemy_defeat(self, enemy, character):
        """
        Handle effects of defeating an enemy
        
        Args:
            enemy (Enemy): The defeated enemy
            character (BaseCharacter): Character that defeated the enemy
        """
        # Award XP to all living party members
        # The character that dealt the killing blow gets a bonus
        xp_gained = enemy.get_xp_value()
        
        # Calculate shared XP (70% of total, divided among all living party members)
        living_party_count = sum(1 for char in self.game_state.party if char and char.is_alive())
        shared_xp = int(xp_gained * 0.7 / living_party_count) if living_party_count > 0 else 0
        
        # Killer gets bonus XP (30% of total)
        killer_bonus = int(xp_gained * 0.3)
        
        # Award XP to all living party members
        for char in self.game_state.party:
            if char and char.is_alive():
                # Award shared XP
                char_xp = shared_xp
                
                # Add bonus for the killer
                if char == character:
                    char_xp += killer_bonus
                
                # Apply XP gain
                leveled_up = char.gain_xp(char_xp)
                
                # Log results
                self._log_message(f"{char.name} gained {char_xp} XP")
                if leveled_up:
                    self._log_message(f"{char.name} leveled up to level {char.level}!")
        
        # Log the defeat
        self._log_message(f"{enemy.name} has been defeated!")
    
    def _log_attack(self, attacker, target, result):
        """
        Log an attack to the combat log
        
        Args:
            attacker (BaseCharacter): The attacking character
            target (BaseCharacter): The target character
            result (dict): Attack result
        """
        # Use the combat log component's method
        self.combat_log.log_attack(attacker, target, result)
    
    def _log_message(self, message):
        """
        Add a message to the combat log
        
        Args:
            message (str): The message to log
        """
        # Use the combat log component's method
        self.combat_log.add_entry(message)
    
    def get_recent_log(self, count=10):
        """
        Get the most recent log messages
        
        Args:
            count (int): Number of messages to return
            
        Returns:
            list: Recent combat log messages
        """
        return self.combat_log.get_recent_entries(count)
    
    def add_attack_animation(self, attacker, target, animation_type="slash"):
        """
        Add an attack animation
        
        Args:
            attacker (BaseCharacter): The attacking character
            target (BaseCharacter): The target character
            animation_type (str): Type of animation
        """
        # Determine animation type based on character class or enemy type
        if hasattr(attacker, 'enemy_type'):
            if attacker.enemy_type == "dragon":
                animation_type = "spell"  # Dragon uses spell animation
            else:
                animation_type = "slash"  # Other enemies use slash
        else:
            # Player character - determine by class
            class_name = attacker.__class__.__name__.lower()
            if class_name == "warrior":
                animation_type = "slash"
            elif class_name == "archer":
                animation_type = "arrow"
            elif class_name == "mage":
                animation_type = "spell"
        
        # Create and add animation
        from ui.animation import AttackAnimation
        animation = AttackAnimation(attacker, target, animation_type)
        animation.start()
        self.animations.append(animation)

    def render_animations(self, screen):
        """
        Render all active animations
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        for animation in self.animations:
            animation.render(screen)