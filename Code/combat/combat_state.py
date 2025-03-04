"""
Combat state management and event scheduling system for real-time combat
"""
import heapq
import time
from enum import Enum, auto

class CombatState(Enum):
    """Combat states for characters and enemies"""
    IDLE = auto()
    WIND_UP = auto()
    ATTACK = auto()
    RECOVERY = auto()
    STAGGERED = auto()
    DODGING = auto()
    PARRYING = auto()
    CASTING = auto()

class CombatEvent:
    """
    Represents a scheduled combat event with timing and priority
    """
    def __init__(self, timestamp, priority, callback, *args, **kwargs):
        """
        Initialize a combat event
        
        Args:
            timestamp (float): When the event should execute
            priority (int): Priority level (lower executes first if same timestamp)
            callback (function): Function to call when event executes
            *args, **kwargs: Arguments to pass to the callback
        """
        self.timestamp = timestamp
        self.priority = priority
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.canceled = False
    
    def __lt__(self, other):
        """
        Compare events for priority queue ordering
        
        Args:
            other (CombatEvent): Another event to compare with
            
        Returns:
            bool: True if this event has higher priority
        """
        if self.timestamp == other.timestamp:
            return self.priority < other.priority
        return self.timestamp < other.timestamp
    
    def execute(self):
        """Execute the event callback if not canceled"""
        if not self.canceled:
            self.callback(*self.args, **self.kwargs)
    
    def cancel(self):
        """Cancel this event"""
        self.canceled = True

class CombatEventQueue:
    """
    Priority queue for scheduling and processing combat events
    """
    def __init__(self):
        """Initialize the combat event queue"""
        self.events = []
        self.current_time = 0
    
    def schedule(self, delay, priority, callback, *args, **kwargs):
        """
        Schedule a new combat event
        
        Args:
            delay (float): Delay in seconds before executing
            priority (int): Priority level (lower executes first if same timestamp)
            callback (function): Function to call when event executes
            *args, **kwargs: Arguments to pass to the callback
            
        Returns:
            CombatEvent: The scheduled event
        """
        timestamp = self.current_time + delay
        event = CombatEvent(timestamp, priority, callback, *args, **kwargs)
        heapq.heappush(self.events, event)
        return event
    
    def update(self, delta_time):
        """
        Update the event queue, processing due events
        
        Args:
            delta_time (float): Time since last update in seconds
            
        Returns:
            int: Number of events processed
        """
        self.current_time += delta_time
        processed = 0
        
        while self.events and self.events[0].timestamp <= self.current_time:
            event = heapq.heappop(self.events)
            if not event.canceled:
                event.execute()
                processed += 1
        
        return processed
    
    def clear(self):
        """Clear all pending events"""
        self.events = []
    
    def cancel_character_events(self, character):
        """
        Cancel all events for a specific character
        
        Args:
            character: The character whose events should be canceled
        """
        for event in self.events:
            if event.args and event.args[0] == character:
                event.cancel()

class AttackPhase:
    """
    Represents an attack phase with timing information
    """
    def __init__(self, wind_up_time, attack_time, recovery_time):
        """
        Initialize attack phase timing
        
        Args:
            wind_up_time (float): Duration of wind-up phase in seconds
            attack_time (float): Duration of attack (hit frame) phase in seconds
            recovery_time (float): Duration of recovery phase in seconds
        """
        self.wind_up_time = wind_up_time
        self.attack_time = attack_time
        self.recovery_time = recovery_time
        self.total_time = wind_up_time + attack_time + recovery_time
    
    def get_phase_at_time(self, elapsed_time):
        """
        Get the attack phase at a given elapsed time
        
        Args:
            elapsed_time (float): Time since attack started
            
        Returns:
            CombatState: The current combat state
        """
        if elapsed_time < self.wind_up_time:
            return CombatState.WIND_UP
        elif elapsed_time < self.wind_up_time + self.attack_time:
            return CombatState.ATTACK
        elif elapsed_time < self.total_time:
            return CombatState.RECOVERY
        return CombatState.IDLE