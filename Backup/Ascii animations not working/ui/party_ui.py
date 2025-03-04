"""
Party UI - UI components for party selection and battle displays
"""
import pygame
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, MAX_PARTY_SIZE, UI_PADDING
)

class PartySelectionUI:
    """
    UI component for selecting party members and managing the roster
    """
    def __init__(self, game_state):
        """
        Initialize the party selection UI
        
        Args:
            game_state (GameState): Reference to the game state
        """
        self.game_state = game_state
        
        # UI state
        self.selected_roster_index = -1
        self.selected_party_slot = -1
        self.roster_scroll_offset = 0
        self.max_visible_roster = 8  # Maximum number of roster entries visible at once
    
    def update(self, delta_time):
        """
        Update UI state
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # UI state updates if needed
        pass
    
    def render(self, screen, font, title_font, colors):
        """
        Render the party selection UI
        
        Args:
            screen (pygame.Surface): The screen to render to
            font (pygame.font.Font): Regular font
            title_font (pygame.font.Font): Title font
            colors (dict): Color definitions
        """
        # Title
        title_text = title_font.render("Select Your Party", True, colors["text"])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_text, title_rect)
        
        # Store section coordinates for mouse handling
        self.party_section_width = SCREEN_WIDTH // 2
        self.party_section_height = 200
        self.party_section_x = (SCREEN_WIDTH - self.party_section_width) // 2
        self.party_section_y = 100
        
        # Party section background
        pygame.draw.rect(
            screen,
            (30, 30, 50),
            (self.party_section_x, self.party_section_y, self.party_section_width, self.party_section_height),
            0,  # Filled
            10  # Border radius
        )
        
        # Party section title
        party_title = font.render("Active Party", True, colors["text"])
        party_title_rect = party_title.get_rect(center=(SCREEN_WIDTH // 2, self.party_section_y + 20))
        screen.blit(party_title, party_title_rect)
        
        # Render party slots
        self.slot_width = 150
        self.slot_height = 120
        self.slots_x = self.party_section_x + (self.party_section_width - (self.slot_width * MAX_PARTY_SIZE) - 
                                (UI_PADDING * (MAX_PARTY_SIZE - 1))) // 2
        self.slots_y = self.party_section_y + 50
        
        for i in range(MAX_PARTY_SIZE):
            slot_x = self.slots_x + i * (self.slot_width + UI_PADDING)
            
            # Slot background (with different color if selected)
            slot_color = colors["selected_slot"] if i == self.selected_party_slot else colors["character_slot"]
            pygame.draw.rect(
                screen,
                slot_color,
                (slot_x, self.slots_y, self.slot_width, self.slot_height),
                0,  # Filled
                5   # Border radius
            )
            
            # Draw character if slot is filled
            if i < len(self.game_state.party) and self.game_state.party[i]:
                character = self.game_state.party[i]
                
                # Character name
                name_text = font.render(character.name, True, colors["text"])
                name_rect = name_text.get_rect(center=(slot_x + self.slot_width // 2, self.slots_y + 25))
                screen.blit(name_text, name_rect)
                
                # Character class
                class_text = font.render(character.__class__.__name__, True, colors["text"])
                class_rect = class_text.get_rect(center=(slot_x + self.slot_width // 2, self.slots_y + 50))
                screen.blit(class_text, class_rect)
                
                # Character level
                level_text = font.render(f"Level {character.level}", True, colors["text"])
                level_rect = level_text.get_rect(center=(slot_x + self.slot_width // 2, self.slots_y + 75))
                screen.blit(level_text, level_rect)
                
                # Remove button
                remove_btn = pygame.Rect(slot_x + self.slot_width - 30, self.slots_y + 5, 25, 25)
                pygame.draw.rect(screen, (200, 50, 50), remove_btn)
                
                # X mark
                pygame.draw.line(screen, (255, 255, 255), 
                            (remove_btn.left + 5, remove_btn.top + 5),
                            (remove_btn.right - 5, remove_btn.bottom - 5), 2)
                pygame.draw.line(screen, (255, 255, 255), 
                            (remove_btn.left + 5, remove_btn.bottom - 5),
                            (remove_btn.right - 5, remove_btn.top + 5), 2)
            else:
                # Empty slot text
                empty_text = font.render("Empty Slot", True, colors["text"])
                empty_rect = empty_text.get_rect(center=(slot_x + self.slot_width // 2, self.slots_y + self.slot_height // 2))
                screen.blit(empty_text, empty_rect)
                
                # Selection number
                slot_num_text = font.render(f"{i+1}", True, colors["text"])
                slot_num_rect = slot_num_text.get_rect(topleft=(slot_x + 5, self.slots_y + 5))
                screen.blit(slot_num_text, slot_num_rect)
        
        # Store roster section coordinates for mouse handling
        self.roster_section_width = SCREEN_WIDTH * 3 // 4
        self.roster_section_height = 350
        self.roster_section_x = (SCREEN_WIDTH - self.roster_section_width) // 2
        self.roster_section_y = self.party_section_y + self.party_section_height + 30
        
        # Roster section background
        pygame.draw.rect(
            screen,
            (30, 50, 30),
            (self.roster_section_x, self.roster_section_y, self.roster_section_width, self.roster_section_height),
            0,  # Filled
            10  # Border radius
        )
        
        # Roster section title
        roster_title = font.render("Character Roster", True, colors["text"])
        roster_title_rect = roster_title.get_rect(center=(SCREEN_WIDTH // 2, self.roster_section_y + 20))
        screen.blit(roster_title, roster_title_rect)
        
        # Roster list
        self.item_height = 40
        visible_area_height = self.roster_section_height - 50  # Accounting for title
        self.max_visible_roster = min(8, visible_area_height // self.item_height)
        
        self.list_start_y = self.roster_section_y + 50
        self.list_width = self.roster_section_width - 40  # Padding on both sides
        self.list_start_x = self.roster_section_x + 20
        
        # Calculate max scroll offset
        max_offset = max(0, len(self.game_state.character_roster) - self.max_visible_roster)
        self.roster_scroll_offset = min(self.roster_scroll_offset, max_offset)
        
        # Render scroll indicators if needed
        if self.roster_scroll_offset > 0:
            up_arrow = font.render("▲", True, colors["text"])
            screen.blit(up_arrow, (self.roster_section_x + self.roster_section_width // 2, self.roster_section_y + 35))
            
        if self.roster_scroll_offset < max_offset:
            down_arrow = font.render("▼", True, colors["text"])
            screen.blit(down_arrow, (self.roster_section_x + self.roster_section_width // 2, 
                                self.roster_section_y + self.roster_section_height - 20))
        
        # Render visible roster items
        for i in range(self.max_visible_roster):
            roster_idx = i + self.roster_scroll_offset
            if roster_idx < len(self.game_state.character_roster):
                character = self.game_state.character_roster[roster_idx]
                
                # Item background (with different color if selected)
                item_color = colors["selected_slot"] if roster_idx == self.selected_roster_index else (40, 60, 40)
                item_rect = pygame.Rect(self.list_start_x, self.list_start_y + i * self.item_height, self.list_width, self.item_height - 5)
                pygame.draw.rect(
                    screen,
                    item_color,
                    item_rect,
                    0,  # Filled
                    5   # Border radius
                )
                
                # Item number
                num_text = font.render(f"{roster_idx+1}", True, colors["text"])
                screen.blit(num_text, (item_rect.left + 10, item_rect.top + 10))
                
                # Character name and class
                char_text = font.render(f"{character.name} - {character.__class__.__name__} (Lv.{character.level})", 
                                    True, colors["text"])
                screen.blit(char_text, (item_rect.left + 40, item_rect.top + 10))
                
                # Add to party button
                if not any(char is character for char in self.game_state.party if char):
                    add_btn = pygame.Rect(item_rect.right - 100, item_rect.top + 5, 90, self.item_height - 15)
                    pygame.draw.rect(screen, (50, 150, 50), add_btn, 0, 5)
                    
                    add_text = font.render("Add", True, colors["text"])
                    add_text_rect = add_text.get_rect(center=add_btn.center)
                    screen.blit(add_text, add_text_rect)
        
        # Render new character button - make it larger and more visible
        new_char_btn = pygame.Rect(self.roster_section_x + 20, self.roster_section_y + self.roster_section_height - 40, 
                                200, 30)
        pygame.draw.rect(screen, (50, 100, 150), new_char_btn, 0, 5)
        
        new_char_text = font.render("Create New Character", True, colors["text"])
        new_char_text_rect = new_char_text.get_rect(center=new_char_btn.center)
        screen.blit(new_char_text, new_char_text_rect)
        
        # Start battle button (only if party has at least one character)
        if any(self.game_state.party):
            start_btn = pygame.Rect(self.roster_section_x + self.roster_section_width - 220, 
                                self.roster_section_y + self.roster_section_height - 40, 
                                200, 30)
            pygame.draw.rect(screen, (150, 50, 50), start_btn, 0, 5)
            
            start_text = font.render("Start Battle", True, colors["text"])
            start_text_rect = start_text.get_rect(center=start_btn.center)
            screen.blit(start_text, start_text_rect)
        
        # Instructions
        instruction_text = font.render("ESC to return to menu", True, colors["text"])
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        screen.blit(instruction_text, instruction_rect)


class PartyBattleUI:
    """
    UI component for displaying party members during battle
    """
    def __init__(self, game_state):
        """
        Initialize the party battle UI
        
        Args:
            game_state (GameState): Reference to the game state
        """
        self.game_state = game_state
    
    def update(self, delta_time):
        """
        Update UI state
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # UI state updates if needed
        pass
    
    def render(self, screen, font, health_bar, xp_bar):
        """
        Render the party in battle
        
        Args:
            screen (pygame.Surface): The screen to render to
            font (pygame.font.Font): Font for text
            health_bar (HealthBar): Health bar component
            xp_bar (XPBar): XP bar component
        """
        # Calculate positions for party members
        character_spacing = 180
        party_center_x = SCREEN_WIDTH // 4
        party_center_y = SCREEN_HEIGHT // 2
        
        # Draw party members
        for i, character in enumerate(self.game_state.party):
            if character:
                # Calculate position (vertical arrangement)
                char_y = party_center_y + (i - 1) * character_spacing * 1.2
                
                # Highlight active character
                if i == self.game_state.active_character_index:
                    # Draw highlight around active character
                    highlight_rect = pygame.Rect(
                        party_center_x - 50,
                        char_y - 60,
                        100,
                        120
                    )
                    pygame.draw.rect(screen, (100, 100, 255, 100), highlight_rect, 2, 5)
                
                # Render character
                if character.is_alive():
                    # Render character sprite
                    character.render(screen, (party_center_x - character.sprite.get_width() // 2, 
                                            char_y - character.sprite.get_height() // 2))
                    
                    # Render character name and level
                    name_text = font.render(f"{character.name} (Lv.{character.level})", True, (255, 255, 255))
                    name_rect = name_text.get_rect(center=(party_center_x, char_y - 50))
                    screen.blit(name_text, name_rect)
                    
                    # Render health bar
                    health_bar.render(screen, character, party_center_x, char_y + 30, font)
                    
                    # Render XP bar below health bar
                    xp_bar.render(screen, character, party_center_x, char_y + 60, font)
                    
                    # Render ready indicator if character can attack
                    if character.can_attack():
                        ready_text = font.render("READY", True, (0, 255, 0))
                        ready_rect = ready_text.get_rect(center=(party_center_x + 80, char_y))
                        screen.blit(ready_text, ready_rect)
                else:
                    # Render defeated state
                    # Draw an X over the character sprite
                    pygame.draw.line(screen, (255, 0, 0), 
                                   (party_center_x - 20, char_y - 20),
                                   (party_center_x + 20, char_y + 20), 3)
                    pygame.draw.line(screen, (255, 0, 0), 
                                   (party_center_x - 20, char_y + 20),
                                   (party_center_x + 20, char_y - 20), 3)
                    
                    # Render "Defeated" text
                    defeated_text = font.render(f"{character.name} (Defeated)", True, (255, 50, 50))
                    defeated_rect = defeated_text.get_rect(center=(party_center_x, char_y - 50))
                    screen.blit(defeated_text, defeated_rect)
            
            # Draw next/prev character indicators
            if len([c for c in self.game_state.party if c and c.is_alive()]) > 1:
                next_char_text = font.render("TAB to cycle characters", True, (200, 200, 200))
                next_char_rect = next_char_text.get_rect(center=(party_center_x, SCREEN_HEIGHT - 40))
                screen.blit(next_char_text, next_char_rect)