"""
Character Creation Dialog for creating new characters
"""
import pygame

class CharacterCreationDialog:
    """
    Dialog for creating new characters
    """
    def __init__(self):
        """Initialize the character creation dialog"""
        self.active = False
        self.character_name = ""
        self.selected_class = None
        self.current_step = 0  # 0: Class selection, 1: Name entry
        self.result = None
        self.callback = None
        
        # UI elements
        self.font = None
        self.title_font = None
        self.dialog_rect = None
        self.class_buttons = []
        self.name_input_rect = None
        self.confirm_button = None
        self.cancel_button = None
        
        # Debug flag
        self.debug = True
    
    def show(self, callback=None):
        """
        Show the character creation dialog
        
        Args:
            callback (function, optional): Function to call with creation result
        """
        self.active = True
        self.character_name = ""
        self.selected_class = None
        self.current_step = 0
        self.result = None
        self.callback = callback
        
        # Setup fonts if not already created
        if not self.font:
            self.font = pygame.font.SysFont("Arial", 20)
            self.title_font = pygame.font.SysFont("Arial", 24)
            
        if self.debug:
            print("Character creation dialog shown")
    
    def hide(self):
        """Hide the character creation dialog"""
        self.active = False
        
        # If we have a result and callback, call it
        if self.callback:
            self.callback(self.result)
            
        if self.debug:
            print(f"Character creation dialog hidden, result: {self.result}")
    
    def update(self, delta_time):
        """
        Update dialog state
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Nothing to update currently
        pass
    
    def render(self, screen):
        """
        Render the dialog
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        if not self.active:
            return
            
        # Setup dialog rect if not already created
        if not self.dialog_rect:
            # Center on screen
            dialog_width = 500
            dialog_height = 400
            dialog_x = (screen.get_width() - dialog_width) // 2
            dialog_y = (screen.get_height() - dialog_height) // 2
            self.dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
            
            # Setup class buttons
            button_width = 150
            button_height = 80
            button_spacing = 20
            button_start_x = dialog_x + (dialog_width - (button_width * 3 + button_spacing * 2)) // 2
            button_y = dialog_y + 120
            
            self.class_buttons = [
                {
                    "rect": pygame.Rect(button_start_x, button_y, button_width, button_height),
                    "class": "warrior",
                    "color": (200, 0, 0),
                    "hover_color": (255, 50, 50)
                },
                {
                    "rect": pygame.Rect(button_start_x + button_width + button_spacing, button_y, button_width, button_height),
                    "class": "archer",
                    "color": (0, 200, 0),
                    "hover_color": (50, 255, 50)
                },
                {
                    "rect": pygame.Rect(button_start_x + (button_width + button_spacing) * 2, button_y, button_width, button_height),
                    "class": "mage",
                    "color": (0, 0, 200),
                    "hover_color": (50, 50, 255)
                }
            ]
            
            # Setup name input
            name_input_width = 350
            name_input_height = 40
            name_input_x = dialog_x + (dialog_width - name_input_width) // 2
            name_input_y = dialog_y + 180
            self.name_input_rect = pygame.Rect(name_input_x, name_input_y, name_input_width, name_input_height)
            
            # Setup buttons
            button_width = 120
            button_height = 40
            button_spacing = 40
            button_start_x = dialog_x + (dialog_width - (button_width * 2 + button_spacing)) // 2
            button_y = dialog_y + dialog_height - 70
            
            self.confirm_button = pygame.Rect(button_start_x, button_y, button_width, button_height)
            self.cancel_button = pygame.Rect(button_start_x + button_width + button_spacing, button_y, button_width, button_height)
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Draw dialog background
        pygame.draw.rect(screen, (50, 50, 70), self.dialog_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.dialog_rect, 2)
        
        # Draw title
        title_text = self.title_font.render("Create New Character", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.dialog_rect.centerx, self.dialog_rect.top + 30))
        screen.blit(title_text, title_rect)
        
        # Draw content based on current step
        if self.current_step == 0:
            # Class selection
            step_text = self.font.render("Step 1: Select Character Class", True, (255, 255, 255))
            step_rect = step_text.get_rect(center=(self.dialog_rect.centerx, self.dialog_rect.top + 70))
            screen.blit(step_text, step_rect)
            
            # Draw class buttons
            mouse_pos = pygame.mouse.get_pos()
            
            for button in self.class_buttons:
                # Check if mouse is over button
                button_color = button["hover_color"] if button["rect"].collidepoint(mouse_pos) else button["color"]
                highlight = button["class"] == self.selected_class
                
                # Draw button
                pygame.draw.rect(screen, button_color, button["rect"])
                if highlight:
                    pygame.draw.rect(screen, (255, 255, 255), button["rect"], 3)
                
                # Draw button text
                button_text = self.font.render(button["class"].capitalize(), True, (255, 255, 255))
                button_text_rect = button_text.get_rect(center=button["rect"].center)
                screen.blit(button_text, button_text_rect)
            
        elif self.current_step == 1:
            # Name entry
            step_text = self.font.render(f"Step 2: Enter Name for {self.selected_class.capitalize()}", True, (255, 255, 255))
            step_rect = step_text.get_rect(center=(self.dialog_rect.centerx, self.dialog_rect.top + 70))
            screen.blit(step_text, step_rect)
            
            # Draw name input box
            pygame.draw.rect(screen, (30, 30, 40), self.name_input_rect)
            pygame.draw.rect(screen, (150, 150, 150), self.name_input_rect, 1)
            
            # Draw current name with cursor
            cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 0
            display_text = self.character_name + ("|" if cursor_visible else "")
            
            text_surface = self.font.render(display_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(midleft=(self.name_input_rect.left + 10, self.name_input_rect.centery))
            
            # Limit text rendering to input box width
            screen.blit(text_surface, text_rect, 
                      (0, 0, min(self.name_input_rect.width - 20, text_surface.get_width()), text_surface.get_height()))
        
        # Draw confirm button
        confirm_color = (0, 180, 0) if self._can_confirm() else (0, 100, 0)
        pygame.draw.rect(screen, confirm_color, self.confirm_button)
        confirm_text = self.font.render("Confirm", True, (255, 255, 255))
        confirm_text_rect = confirm_text.get_rect(center=self.confirm_button.center)
        screen.blit(confirm_text, confirm_text_rect)
        
        # Draw cancel button
        pygame.draw.rect(screen, (180, 0, 0), self.cancel_button)
        cancel_text = self.font.render("Cancel", True, (255, 255, 255))
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_button.center)
        screen.blit(cancel_text, cancel_text_rect)
    
    def handle_key_event(self, key):
        """
        Handle keyboard input
        
        Args:
            key (int): The key code from pygame.K_*
            
        Returns:
            bool: True if the key was handled, False otherwise
        """
        if not self.active:
            return False
            
        if key == pygame.K_ESCAPE:
            self.hide()
            return True
            
        if key == pygame.K_RETURN:
            if self._can_confirm():
                self._confirm_current_step()
            return True
            
        if self.current_step == 1:
            # Handle name input
            if key == pygame.K_BACKSPACE:
                self.character_name = self.character_name[:-1]
                return True
                
        return False
    
    def handle_text_input(self, text):
        """
        Handle text input (for character name)
        
        Args:
            text (str): The text input
            
        Returns:
            bool: True if the input was handled, False otherwise
        """
        if not self.active or self.current_step != 1:
            return False
            
        # Limit name length
        if len(self.character_name) < 20:
            self.character_name += text
            if self.debug:
                print(f"Character name input: {self.character_name}")
            return True
            
        return False
    
    def handle_mouse_event(self, event):
        """
        Handle mouse events
        
        Args:
            event (pygame.event.Event): The mouse event
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        if not self.active or event.type != pygame.MOUSEBUTTONDOWN:
            return False
            
        mouse_pos = event.pos
        
        # Check if clicked on confirm button
        if self.confirm_button.collidepoint(mouse_pos) and self._can_confirm():
            self._confirm_current_step()
            return True
            
        # Check if clicked on cancel button
        if self.cancel_button.collidepoint(mouse_pos):
            self.hide()
            return True
            
        # Step-specific click handling
        if self.current_step == 0:
            # Class selection
            for button in self.class_buttons:
                if button["rect"].collidepoint(mouse_pos):
                    self.selected_class = button["class"]
                    if self.debug:
                        print(f"Selected class: {self.selected_class}")
                    return True
        
        return False
    
    def _can_confirm(self):
        """
        Check if the current step can be confirmed
        
        Returns:
            bool: True if confirmable, False otherwise
        """
        if self.current_step == 0:
            return self.selected_class is not None
        elif self.current_step == 1:
            return bool(self.character_name)
        return False
    
    def _confirm_current_step(self):
        """Confirm the current step and advance"""
        if self.current_step == 0:
            # Confirm class selection
            if self.selected_class:
                self.current_step = 1
                if self.debug:
                    print(f"Moving to name entry for class: {self.selected_class}")
        elif self.current_step == 1:
            # Confirm name entry
            if self.character_name:
                # Create character result
                self.result = {
                    "name": self.character_name,
                    "class": self.selected_class
                }
                if self.debug:
                    print(f"Creating character: {self.character_name} ({self.selected_class})")
                self.hide()