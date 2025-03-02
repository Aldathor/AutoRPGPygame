"""
Auto-Battler RPG Prototype - Main Entry Point
"""
import sys
import os
# Add the project root to Python path to help with imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from game.game_controller import GameController
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE

def main():
    """Main function to initialize and run the game"""
    # Initialize pygame
    pygame.init()
    pygame.display.set_caption(GAME_TITLE)
    
    # Create the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    # Create game controller
    game = GameController(screen)
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    game.handle_key_event(event.key)
        
        # Update game state
        game.update(clock.get_time() / 1000.0)  # Convert to seconds
        
        # Render the game
        screen.fill((0, 0, 0))  # Clear the screen
        game.render()
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
