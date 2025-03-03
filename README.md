```
auto_RPG_Pygame/
├── main.py                 # Entry point
├── __init__.py
├── game/
│   ├── __init__.py
│   ├── game_state.py       # Game state management
│   ├── game_controller.py  # Main game controller
│   ├── config.py           # Game configuration constants
│   └── events.py           # Game simple event system
├── entities/
│   ├── __init__.py
│   ├── base_character.py   # Abstract base character class
│   ├── player_classes/     # Player character implementations
│   │   ├── __init__.py
│   │   ├── warrior.py
│   │   ├── archer.py
│   │   └── mage.py
│   └── enemies/            # Enemy implementations
│       ├── __init__.py
│       ├── enemy_base.py
│       └── enemy_types.py
├── combat/
│   ├── __init__.py
│   ├── battle_manager.py   # Controls battle flow
│   ├── combat_calculator.py # Damage calculations
│   └── enemy_spawner.py    # Generates enemies
├── ui/
│   ├── __init__.py
│   ├── ui_manager.py  *     # Manages UI elements
│   ├── party_ui.py
│   ├── animation_helper.py
│   ├── animation.py
│   ├── ascii_sprites.py
│   ├── rest_animation.py
│   ├── ascii_background.py
│   ├── status_bars.py      # HP/XP bars
│   ├── combat_log.py       # combat log for fights
│   └── character_creation.py # Dialog for creating new characters
└── data/
    ├── __init__.py
    ├── data_manager.py     # Save/load functionality
    └── character_data.py   # Character data structure

```
