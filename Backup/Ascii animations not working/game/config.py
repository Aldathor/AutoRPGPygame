"""
Game configuration constants with party system support
"""

# Display settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
GAME_TITLE = "Auto-Battler RPG Prototype (Party Edition)"

# Game settings
BATTLE_TIMER_INTERVAL = 0.5  # Time between battle actions in seconds
MAX_PARTY_SIZE = 3  # Maximum number of characters in a party
MAX_ENEMY_COUNT = 3  # Maximum number of enemies in a battle

# UI Settings
UI_FONT = "Arial"
UI_FONT_SIZE = 20
UI_PADDING = 10
HEALTH_BAR_HEIGHT = 20
XP_BAR_HEIGHT = 10
COMBAT_LOG_LINES = 10
COMBAT_LOG_WIDTH = 400
COMBAT_LOG_HEIGHT = 200
COMBAT_LOG_BG_COLOR = (0, 0, 0, 180)  # RGBA with alpha for transparency
COMBAT_LOG_TEXT_COLOR = (255, 255, 255)

# Party management settings
PARTY_SLOT_WIDTH = 150
PARTY_SLOT_HEIGHT = 100
PARTY_SELECTOR_COLOR = (100, 100, 255, 128)  # RGBA with alpha for transparency
PARTY_INACTIVE_COLOR = (100, 100, 100)
PARTY_ACTIVE_COLOR = (150, 150, 255)
PARTY_MEMBER_SPACING = 120  # Vertical spacing between party members in battle

# Character settings
BASE_HP = 100
BASE_ATTACK = 10
BASE_DEFENSE = 5
BASE_MAGIC = 10
BASE_SPEED = 5
XP_PER_LEVEL = 100  # XP needed for first level up (increases per level)
XP_LEVEL_MULTIPLIER = 1.5  # XP requirement increase per level
XP_GAIN_BASE = 20  # Base XP gain per enemy defeated

# XP distribution settings
XP_KILLER_BONUS = 0.3  # Extra XP percentage for character dealing killing blow
XP_SHARED_PERCENTAGE = 0.7  # Percentage of XP that is shared among party members

# Character class-specific modifiers
CLASS_MODIFIERS = {
    "warrior": {
        "hp": 1.5,
        "attack": 1.2,
        "defense": 1.3,
        "magic": 0.8,
        "speed": 0.9
    },
    "archer": {
        "hp": 0.9,
        "attack": 1.4,
        "defense": 0.8,
        "magic": 0.9,
        "speed": 1.5
    },
    "mage": {
        "hp": 0.8,
        "attack": 0.7,
        "defense": 0.7,
        "magic": 1.8,
        "speed": 1.1
    }
}

# Enemy settings
ENEMY_LEVEL_SCALING = 0.5  # How much stats increase per enemy level
ENEMY_SPAWN_BASE_TIME = 2.0  # Base time between enemy spawns
ENEMY_TYPES = ["goblin", "orc", "troll", "skeleton", "zombie", "dragon"]
ENEMY_TYPE_MODIFIERS = {
    "goblin": {
        "hp": 0.7,
        "attack": 0.8,
        "defense": 0.6,
        "magic": 0.5,
        "speed": 1.5,
        "xp_value": 1.0
    },
    "orc": {
        "hp": 1.2,
        "attack": 1.3,
        "defense": 1.0,
        "magic": 0.4,
        "speed": 0.8,
        "xp_value": 1.5
    },
    "troll": {
        "hp": 1.8,
        "attack": 1.5,
        "defense": 1.3,
        "magic": 0.3,
        "speed": 0.6,
        "xp_value": 2.0
    },
    "skeleton": {
        "hp": 0.8,
        "attack": 1.0,
        "defense": 1.0,
        "magic": 0.9,
        "speed": 1.2,
        "xp_value": 1.2
    },
    "zombie": {
        "hp": 1.1,
        "attack": 0.9,
        "defense": 0.7,
        "magic": 0.5,
        "speed": 0.7,
        "xp_value": 1.3
    },
    "dragon": {
        "hp": 2.5,
        "attack": 2.0,
        "defense": 1.8,
        "magic": 2.0,
        "speed": 1.0,
        "xp_value": 5.0
    }
}

# Enemy AI targeting priorities
ENEMY_TARGETING_PRIORITIES = {
    "goblin": "weakest",  # Target lowest HP character
    "orc": "strongest",   # Target highest attack character
    "troll": "random",    # Random targeting
    "skeleton": "magical", # Target highest magic character
    "zombie": "weakest",  # Target lowest HP character
    "dragon": "magical"   # Target highest magic character
}

# Combat settings
CRITICAL_HIT_CHANCE = 0.1  # 10% chance
CRITICAL_HIT_MULTIPLIER = 2.0  # Double damage on critical hits
DODGE_CHANCE_BASE = 0.05  # 5% base dodge chance
DODGE_CHANCE_PER_SPEED = 0.005  # Additional dodge chance per speed point
MAGIC_RESISTANCE_BASE = 0.1  # Base magic resistance
MAGIC_RESISTANCE_PER_DEFENSE = 0.01  # Magic resistance per defense point
ATTACK_COOLDOWN_BASE = 1.0  # Base cooldown between attacks in seconds

# Game states
STATE_MENU = "menu"
STATE_CHARACTER_SELECT = "character_select"
STATE_PARTY_SELECT = "party_select"  # New state for party selection
STATE_BATTLE = "battle"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"

# Data persistence
SAVE_FILE_NAME = "save_game.json"
CHARACTER_ROSTER_FILE = "character_roster.json"