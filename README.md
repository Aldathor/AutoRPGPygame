Needs to be updated


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
You need a script that:
1. Reads all files in a directory recursively.
2. Concatenates them with `// File: <relative_path>` as a separator.
3. Outputs the concatenated content.
4. (Optional) Writes the concatenated output back into the directory if needed.
5. Allows you to check modifications using `git diff`.

Here's a simple script in Python:

```python
import os

DIRECTORY = "apps"  # Change this to the root directory you want to scan
OUTPUT_FILE = "concatenated_output.js"  # Change this if needed

def collect_files(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return sorted(file_list)  # Sorting ensures consistency

def concatenate_files(file_list):
    output = []
    for file_path in file_list:
        relative_path = os.path.relpath(file_path, DIRECTORY)
        output.append(f"// File: {relative_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            output.append(f.read())
    return "\n".join(output)

if __name__ == "__main__":
    files = collect_files(DIRECTORY)
    concatenated_content = concatenate_files(files)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
        out_file.write(concatenated_content)
    
    print(f"Concatenated file written to {OUTPUT_FILE}")
```

Then, you can use Claude (or any LLM) to process `concatenated_output.js`, make modifications, and save them back.

To write the modified output back to the directory, you need another script to split the concatenated output and restore individual files:

```python
import os
import re

INPUT_FILE = "concatenated_output.js"

def restore_files():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_file = None
    file_contents = {}

    for line in lines:
        match = re.match(r"^// File: (.+)", line)
        if match:
            current_file = os.path.join(DIRECTORY, match.group(1))
            file_contents[current_file] = []
        elif current_file:
            file_contents[current_file].append(line)

    for file_path, content in file_contents.items():
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(content)

    print("Files restored to original locations.")

if __name__ == "__main__":
    restore_files()
```

### Workflow:
1. Run `concatenation_script.py` to generate `concatenated_output.js`.
2. Modify the file using Claude.
3. Run `restore_script.py` to write changes back to the original files.
4. Use `git diff` to check modifications.

Would you like any enhancements, such as handling binary files or excluding certain file types?
