"""
Battle Integration - Provides integration between different battle system components
"""
import pygame

def add_integration_methods(battle_manager):
    """
    Add spatial combat integration methods to a battle manager instance
    
    Args:
        battle_manager: The battle manager instance to modify
    """
    # Extract methods from the BattleSystemsIntegration class in realtime_battle_manager.py
    from combat.realtime_battle_manager import BattleSystemsIntegration
    
    # Add initialization method
    battle_manager.initialize_spatial_combat_systems = lambda width, height: BattleSystemsIntegration.init_systems(battle_manager, width, height)
    
    # Add internal initialization
    battle_manager._initialize_spatial_combat = lambda: BattleSystemsIntegration._initialize_spatial_combat(battle_manager)
    
    # Add start battle method (using original but adding spatial systems)
    original_start_battle = battle_manager.start_battle
    battle_manager.start_battle = lambda: (original_start_battle(), BattleSystemsIntegration.start_battle(battle_manager))
    
    # Add update method
    battle_manager._update_spatial_combat_systems = lambda delta_time: BattleSystemsIntegration.update_all_systems(battle_manager, delta_time)
    
    # Add render method
    battle_manager._render_spatial_combat_systems = lambda screen: BattleSystemsIntegration.render_all_systems(battle_manager, screen)
    
    # Add event handling methods
    battle_manager.handle_mouse_event = lambda event: BattleSystemsIntegration.handle_mouse_event(battle_manager, event)
    battle_manager.handle_key_event = lambda key: BattleSystemsIntegration.handle_key_event(battle_manager, key)
    
    # Add positioning method
    battle_manager.position_entity = lambda entity, position: BattleSystemsIntegration.position_entity(battle_manager, entity, position)
    
    # Add cleanup method
    battle_manager.clean_up_spatial_systems = lambda: BattleSystemsIntegration.clean_up(battle_manager)
    
    return battle_manager
