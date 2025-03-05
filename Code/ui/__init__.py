"""
UI module initialization
Contains UI classes and elements for rendering the game
"""

# Import UI components
from .ui_manager import UIManager
from .party_ui import PartyBattleUI, PartySelectionUI
from .character_creation_dialog import CharacterCreationDialog
from .combat_log import CombatLog
from .status_bars import HealthBar, XPBar, CooldownIndicator

# Import ASCII and animation components
from .ascii_sprites import ASCIISprite, get_class_sprite, get_enemy_sprite
from .animation import Animation, AttackAnimation
from .animation_helper import AnimationHelper
from .rest_animation import FirePitAnimation
from .ascii_background import ASCIIBackground

# Define exports
__all__ = [
    # UI management
    'UIManager',
    'PartyBattleUI',
    'PartySelectionUI',
    'CharacterCreationDialog',
    'CombatLog',
    'HealthBar',
    'XPBar',
    'CooldownIndicator',
    
    # Visual elements
    'ASCIISprite',
    'get_class_sprite',
    'get_enemy_sprite',
    'Animation',
    'AttackAnimation',
    'AnimationHelper',
    'FirePitAnimation',
    'ASCIIBackground'
]