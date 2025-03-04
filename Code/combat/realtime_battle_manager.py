"""
Real-time Battle Manager - Handles real-time combat flow and character interactions
"""
import time
import pygame
from combat.combat_state import CombatState, CombatEventQueue
from combat.combat_calculator import CombatCalculator

class RealtimeBattleManager:
    """
    Manages real-time battles between party members and enemies
    """
    def __init__(self, game_state):
        """
        Initialize the real-time battle manager
        
        Args:
            game_state (GameState): Reference to the game state
        """
        self.game_state = game_state
        self.combat_log = getattr(game_state, 'combat_log', None)
        if not self.combat_log:
            from ui.combat_log import CombatLog
            self.combat_log = CombatLog()
        
        self.event_queue = CombatEventQueue()
        self.animations = []
        self.battle_time = 0
        self.paused = False
        
        # Combat encounter tracking
        self.combat_encounter_count = 0
        
        # Target selection handling
        self.target_selection_active = False
        self.selecting_character = None
        
        # AI update frequency
        self.ai_update_interval = 0.5  # seconds
        self.last_ai_update = 0
    
    def start_battle(self):
        """Initialize a new battle"""
        self.event_queue.clear()
        self.battle_time = 0
        self.animations = []
        
        # Schedule initial AI update
        self.event_queue.schedule(0.1, 10, self._update_enemy_ai)
        
        # Log battle start
        self._log_message("Battle started!")
    
    def update(self, delta_time):
        """
        Update the real-time battle system
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        if self.paused:
            return
            
        # Update battle time
        self.battle_time += delta_time
        
        # Process events from the queue
        self.event_queue.update(delta_time)
        
        # Update all combat entities
        for character in self.game_state.party:
            if character:
                character.update(delta_time)
        
        for enemy in self.game_state.enemies:
            enemy.update(delta_time)
        
        # Update animations
        self.animations = [anim for anim in self.animations if anim.update()]
        
        # AI updates at fixed intervals
        self.last_ai_update += delta_time
        if self.last_ai_update >= self.ai_update_interval:
            self._update_enemy_ai()
            self.last_ai_update = 0
        
        # Check battle state (victory/defeat)
        self._check_battle_state()
    
    def _check_battle_state(self):
        """Check for battle end conditions"""
        # Check for party defeat
        if not self._is_party_alive():
            self.game_state.defeat_count += 1
            self.game_state.change_state("game_over")
            return
            
        # Check for enemy defeat
        if not self.game_state.enemies or all(not enemy.is_alive() for enemy in self.game_state.enemies):
            self.game_state.victory_count += 1
            self.game_state.change_state("victory")
            return
    
    def _is_party_alive(self):
        """Check if any party member is alive"""
        return any(char and char.is_alive() for char in self.game_state.party)
    
    def _update_enemy_ai(self):
        """Update AI decisions for all enemies"""
        # Process each enemy's AI
        for enemy in self.game_state.enemies:
            if enemy.is_alive() and enemy.combat_state == CombatState.IDLE:
                # Select target from party
                target = self._select_target_for_enemy(enemy)
                
                if target:
                    # Check if in range
                    if not enemy.is_in_range(target):
                        # Move towards target if not in range
                        enemy.move_towards_target(target)
                    else:
                        # Attack if in range and ready
                        if enemy.can_attack():
                            attack_success = enemy.attack_target(target)
                            if attack_success:
                                # Schedule completion of attack (end of wind-up)
                                self.event_queue.schedule(
                                    enemy.attack_phase.wind_up_time,
                                    5,
                                    self._process_enemy_attack,
                                    enemy,
                                    target
                                )
        
        # Schedule next AI update
        self.event_queue.schedule(self.ai_update_interval, 10, self._update_enemy_ai)
    
    def _process_enemy_attack(self, enemy, target):
        """
        Process an enemy's attack when wind-up completes
        
        Args:
            enemy (Enemy): The attacking enemy
            target (BaseCharacter): The target character
        """
        # Make sure enemy and target are still valid
        if not enemy.is_alive() or enemy.combat_state != CombatState.WIND_UP:
            return
            
        if not target.is_alive():
            # Target died before attack completed, find new target
            new_target = self._select_target_for_enemy(enemy)
            if new_target:
                target = new_target
            else:
                # No valid targets, cancel attack
                enemy.combat_state = CombatState.RECOVERY
                enemy.state_start_time = time.time()
                return
        
        # Complete the attack
        result = enemy.complete_attack(target)
        
        # Log the attack
        self._log_attack(enemy, target, result)
        
        # Add attack animation
        if hasattr(self.game_state, 'animation_helper'):
            animation_type = enemy.get_animation_type()
            self.game_state.animation_helper.add_attack_animation(enemy, target, animation_type)
        
        # Check if character died
        if not target.is_alive():
            self._log_message(f"{target.name} has been defeated!")
            
            # Check if all party members are dead
            if not self._is_party_alive():
                self._log_message("The party has been defeated!")
        
        # Schedule transition to idle after recovery
        self.event_queue.schedule(
            enemy.attack_phase.recovery_time,
            5,
            self._complete_recovery,
            enemy
        )
    
    def _complete_recovery(self, character):
        """
        Complete recovery phase and return to idle
        
        Args:
            character (BaseCharacter): The character completing recovery
        """
        if character.is_alive() and character.combat_state == CombatState.RECOVERY:
            character.combat_state = CombatState.IDLE
            character.state_start_time = time.time()
    
    def _select_target_for_enemy(self, enemy):
        """
        Select a target for an enemy to attack
        
        Args:
            enemy (Enemy): The enemy selecting a target
            
        Returns:
            BaseCharacter: The selected target
        """
        # Basic targeting strategy based on enemy type
        living_party = [char for char in self.game_state.party if char and char.is_alive()]
        
        if not living_party:
            return None
            
        # Different enemy types might have different targeting strategies
        if hasattr(enemy, 'targeting_priority'):
            if enemy.targeting_priority == "weakest":
                # Target character with lowest HP percentage
                return min(living_party, key=lambda char: char.current_hp / char.max_hp)
            elif enemy.targeting_priority == "strongest":
                # Target character with highest attack
                return max(living_party, key=lambda char: char.attack)
            elif enemy.targeting_priority == "magical":
                # Target character with highest magic
                return max(living_party, key=lambda char: char.magic)
            elif enemy.targeting_priority == "random":
                # Random targeting
                import random
                return random.choice(living_party)
        
        # Default: random target
        import random
        return random.choice(living_party)
    
    def initiate_player_attack(self, character, target):
        """
        Initiate an attack by a player character
        
        Args:
            character (BaseCharacter): The attacking character
            target (BaseCharacter): The target
            
        Returns:
            bool: True if attack was initiated
        """
        if not character.can_attack() or not target.is_alive():
            return False
        
        # Start attack sequence
        attack_started = character.attack_target(target)
        if not attack_started:
            return False
        
        # Schedule completion of attack (end of wind-up)
        self.event_queue.schedule(
            character.attack_phase.wind_up_time,
            5,
            self._process_player_attack,
            character,
            target
        )
        
        return True
    
    def _process_player_attack(self, character, target):
        """
        Process a player's attack when wind-up completes
        
        Args:
            character (BaseCharacter): The attacking character
            target (BaseCharacter): The target
        """
        # Make sure character and target are still valid
        if not character.is_alive() or character.combat_state != CombatState.WIND_UP:
            return
            
        if not target.is_alive():
            # Target died before attack completed, cancel attack
            character.combat_state = CombatState.RECOVERY
            character.state_start_time = time.time()
            return
        
        # Complete the attack
        result = character.complete_attack(target)
        
        # Log the attack
        self._log_attack(character, target, result)
        
        # Add attack animation
        if hasattr(self.game_state, 'animation_helper'):
            animation_type = character.get_animation_type()
            self.game_state.animation_helper.add_attack_animation(character, target, animation_type)
        
        # Check if enemy died
        if not target.is_alive():
            self._handle_enemy_defeat(target, character)
        
        # Schedule transition to idle after recovery
        self.event_queue.schedule(
            character.attack_phase.recovery_time,
            5,
            self._complete_recovery,
            character
        )
    
    def initiate_target_selection(self, character):
        """
        Start the target selection process for a player character
        
        Args:
            character (BaseCharacter): Character selecting a target
            
        Returns:
            bool: True if selection was initiated
        """
        if not character.can_attack():
            return False
        
        # Get living enemies as potential targets
        potential_targets = [enemy for enemy in self.game_state.enemies if enemy.is_alive()]
        if not potential_targets:
            return False
        
        # Set target selection state
        self.target_selection_active = True
        self.selecting_character = character
        self.game_state.selecting_target = True
        self.game_state.potential_targets = potential_targets
        
        return True
    
    def select_target(self, target_index):
        """
        Complete target selection and initiate attack
        
        Args:
            target_index (int): Index of selected target
            
        Returns:
            bool: True if attack was initiated
        """
        if not self.target_selection_active:
            return False
            
        if 0 <= target_index < len(self.game_state.potential_targets):
            target = self.game_state.potential_targets[target_index]
            character = self.selecting_character
            
            # Check if target is in range
            if not character.is_in_range(target):
                # Begin moving towards target if not in range
                character.move_towards_target(target)
                
                # Schedule attack when character gets in range
                self.event_queue.schedule(
                    0.1, 5, self._check_attack_range, character, target
                )
            else:
                # Initiate attack if in range
                result = self.initiate_player_attack(character, target)
                
                # Reset target selection state
                self.target_selection_active = False
                self.selecting_character = None
                self.game_state.selecting_target = False
                self.game_state.potential_targets = []
                
                return result
        
        # Reset target selection state if attack wasn't initiated
        self.cancel_target_selection()
        return False
    
    def _check_attack_range(self, character, target):
        """
        Check if character is in range to attack target, and attack if possible
        
        Args:
            character (BaseCharacter): The character moving to attack
            target (BaseCharacter): The target
            
        Returns:
            bool: True if attack was initiated
        """
        if not character.is_alive() or not target.is_alive():
            # Reset target selection if either character is not alive
            self.cancel_target_selection()
            return False
            
        # Check if in range
        if character.is_in_range(target):
            # Stop movement
            character.is_moving = False
            
            # Initiate attack if ready
            if character.can_attack():
                result = self.initiate_player_attack(character, target)
                
                # Reset target selection
                self.cancel_target_selection()
                return result
        else:
            # Not in range yet, keep moving and check again
            character.move_towards_target(target)
            self.event_queue.schedule(
                0.1, 5, self._check_attack_range, character, target
            )
        
        return False
    
    def cancel_target_selection(self):
        """Cancel the current target selection"""
        self.target_selection_active = False
        self.selecting_character = None
        self.game_state.selecting_target = False
        self.game_state.potential_targets = []
    
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
        if hasattr(self.combat_log, 'log_attack'):
            self.combat_log.log_attack(attacker, target, result)
        else:
            # Fallback if log_attack method is not available
            hit_status = "hit" if result.get("hit", False) else "missed"
            damage = result.get("damage", 0)
            self._log_message(f"{attacker.name} {hit_status} {target.name} for {damage} damage")
    
    def _log_message(self, message):
        """
        Add a message to the combat log
        
        Args:
            message (str): The message to log
        """
        # Use the combat log component's method
        if self.combat_log:
            self.combat_log.add_entry(message)
        else:
            # Fallback if combat log is not available
            print(f"[COMBAT] {message}")
    
    def toggle_pause(self):
        """
        Toggle the battle pause state
        
        Returns:
            bool: New pause state
        """
        self.paused = not self.paused
        return self.paused
    
    def render_animations(self, screen):
        """
        Render battle effects and indicators
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Render animations
        for animation in self.animations:
            animation.render(screen)
        
        # Render range indicators for target selection
        if self.target_selection_active and self.selecting_character:
            char = self.selecting_character
            char_center = (char.position[0] + char.sprite.get_width() // 2, 
                         char.position[1] + char.sprite.get_height() // 2)
            
            # Draw attack range circle
            pygame.draw.circle(
                screen,
                (255, 255, 0),  # Yellow
                char_center,
                char.attack_range,
                1  # Line width
            )
    
    def get_recent_log(self, count=10):
        """
        Get the most recent log messages
        
        Args:
            count (int): Number of messages to return
            
        Returns:
            list: Recent combat log messages
        """
        if hasattr(self.combat_log, 'get_recent_entries'):
            return self.combat_log.get_recent_entries(count)
        return []