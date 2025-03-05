"""
Combat module - Battle system and mechanics
"""
from combat.enemy_spawner import EnemySpawner
from combat.combat_calculator import CombatCalculator
from combat.combat_state import CombatState, CombatEventQueue, AttackPhase, MovementPhase
from combat.realtime_battle_manager import RealtimeBattleManager
from combat.combat_grid import CombatGrid, CellType
from combat.pathfinding import AStar
from combat.movement_controller import MovementController

# Tactical combat systems
from combat.tactical_ai import TacticalAI
from combat.formation_system import FormationType, FormationSystem
from combat.cover_system import CoverType, CoverSystem
from combat.area_effect_system import AoEShape, AoEEffect, AoEManager
from combat.tactical_ui import TacticalUIController
from combat.combat_modifiers import ModifierManager, CombatModifier, CombatModifierType, CombatModifierSource

__all__ = [
    # Core combat
    'RealtimeBattleManager',
    'EnemySpawner', 
    'CombatCalculator',
    'CombatState',
    'CombatEventQueue',
    'AttackPhase',
    'MovementPhase',
    
    # Spatial combat
    'CombatGrid',
    'CellType',
    'AStar',
    'MovementController',
    
    # Tactical combat
    'TacticalAI',
    'FormationType',
    'FormationSystem',
    'CoverType', 
    'CoverSystem',
    'AoEShape',
    'AoEEffect',
    'AoEManager',
    'TacticalUIController',
    'ModifierManager',
    'CombatModifier',
    'CombatModifierType',
    'CombatModifierSource'
]