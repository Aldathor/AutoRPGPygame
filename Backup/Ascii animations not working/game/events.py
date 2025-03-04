"""
Events system for game-wide communication
"""

# Define event types
EVENT_CONTINUE_TO_NEXT_BATTLE = "continue_to_next_battle"

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