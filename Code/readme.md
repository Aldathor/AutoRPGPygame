# Auto-Battler RPG Prototype

An auto-battler RPG game with modular components, character progression, and AI-driven combat.

## Project Overview

This prototype implements the core systems of an auto-battler RPG, including:

- Turn-based auto-battle system with state-driven AI
- Character classes with unique abilities and progression
- Enemy AI with varied difficulty levels
- Data persistence for saving/loading game state
- Basic UI for displaying combat and character information

## Architecture

The project follows a modular architecture

## Dependencies

- Python 3.8+
- Pygame 2.0.1+

## Setup Instructions

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python main.py`

## Game Controls

- Space: Start/pause auto-battle
- 1-3: Select character class (Warrior, Archer, Mage)
- S: Save game
- L: Load game
- ESC: Exit game

## Extensibility

The codebase is designed for easy extension:
- Add new character classes by extending BaseCharacter
- Create new enemy types in the enemies module
- Implement additional combat mechanics in the combat system
- Expand UI with new visual elements

## Performance Considerations

- Object pooling for projectiles and effects
- Efficient state management to minimize update overhead
- Optimized collision detection for combat interactions
