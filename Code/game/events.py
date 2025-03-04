"""
Events system for game-wide communication with real-time combat support
"""

# Define event types
EVENT_CONTINUE_TO_NEXT_BATTLE = "continue_to_next_battle"

# Real-time combat events
EVENT_COMBAT_ATTACK_START = "combat_attack_start"    # When a character starts attacking
EVENT_COMBAT_ATTACK_HIT = "combat_attack_hit"        # When an attack hits
EVENT_COMBAT_ATTACK_MISS = "combat_attack_miss"      # When an attack misses
EVENT_COMBAT_ATTACK_END = "combat_attack_end"        # When an attack sequence ends
EVENT_COMBAT_ENTITY_DEFEATED = "combat_entity_defeated"  # When a character or enemy is defeated
EVENT_COMBAT_MOVE_START = "combat_move_start"        # When a character starts moving
EVENT_COMBAT_MOVE_END = "combat_move_end"            # When a character stops moving
EVENT_TARGET_SELECTION_START = "target_selection_start"  # When target selection begins
EVENT_TARGET_SELECTION_END = "target_selection_end"      # When target selection ends
EVENT_COMBAT_STATE_CHANGE = "combat_state_change"    # When a character's combat state changes

# Event handlers dictionary
_event_handlers = {}

def register_event_handler(event_type, handler):
    """
    Register a function to handle a specific event type
    
    Args:
        event_type (str): The type of event to handle
        handler (function): The function to call when the event occurs
    """
    if event_type not in _event_handlers:
        _event_handlers[event_type] = []
    
    if handler not in _event_handlers[event_type]:
        _event_handlers[event_type].append(handler)

def unregister_event_handler(event_type, handler):
    """
    Unregister a function from handling a specific event type
    
    Args:
        event_type (str): The type of event
        handler (function): The function to unregister
    """
    if event_type in _event_handlers and handler in _event_handlers[event_type]:
        _event_handlers[event_type].remove(handler)

def trigger_event(event_type, *args, **kwargs):
    """
    Trigger an event, calling all registered handlers
    
    Args:
        event_type (str): The type of event to trigger
        *args, **kwargs: Arguments to pass to the handlers
    """
    if event_type in _event_handlers:
        for handler in _event_handlers[event_type]:
            handler(*args, **kwargs)