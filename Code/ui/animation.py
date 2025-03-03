"""
Animation system for ASCII sprites
"""
import pygame
import time

class Animation:
    """
    Base class for animations
    """
    def __init__(self, duration=0.5):
        """
        Initialize an animation
        
        Args:
            duration (float): Duration of the animation in seconds
        """
        self.duration = duration
        self.start_time = None
        self.is_playing = False
    
    def start(self):
        """Start the animation"""
        self.start_time = time.time()
        self.is_playing = True
    
    def update(self):
        """
        Update the animation
        
        Returns:
            bool: True if animation is still playing, False if finished
        """
        if not self.is_playing:
            return False
            
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.is_playing = False
            return False
            
        return True
    
    def render(self, screen, position):
        """
        Render the animation
        
        Args:
            screen (pygame.Surface): The screen to render to
            position (tuple): The position (x, y) to render at
        """
        pass  # Implemented by derived classes


class AttackAnimation(Animation):
    """
    Attack animation for characters and enemies
    """
    def __init__(self, source, target, animation_type="slash", duration=0.5):
        """
        Initialize an attack animation
        
        Args:
            source (BaseCharacter): The character performing the attack
            target (BaseCharacter): The target of the attack
            animation_type (str): Type of animation ("slash", "arrow", "spell")
            duration (float): Duration of the animation in seconds
        """
        super().__init__(duration)
        self.source = source
        self.target = target
        self.animation_type = animation_type
        self.frames = self._create_frames()
        self.current_frame = 0
    
    def _create_frames(self):
        """
        Create animation frames based on type
        
        Returns:
            list: List of surfaces for each frame
        """
        frames = []
        
        if self.animation_type == "slash":
            # Create slash animation frames (ASCII slashes)
            slash_frames = [
                ["   ", " / ", "   "],
                ["   ", " | ", "   "],
                ["   ", " \\ ", "   "],
                ["   ", " - ", "   "],
                ["   ", " / ", "   "]
            ]
            
            for ascii_frame in slash_frames:
                surface = pygame.Surface((30, 30), pygame.SRCALPHA)
                font = pygame.font.SysFont("Courier New", 20)
                for i, line in enumerate(ascii_frame):
                    text = font.render(line, True, (255, 255, 255))
                    surface.blit(text, (0, i * 20))
                frames.append(surface)
                
        elif self.animation_type == "arrow":
            # Create arrow animation frames (ASCII arrows)
            arrow_frames = [
                ["    -->"],
                ["   --->"],
                ["  ---->"],
                [" ----->"],
                ["------>"]
            ]
            
            for ascii_frame in arrow_frames:
                surface = pygame.Surface((60, 20), pygame.SRCALPHA)
                font = pygame.font.SysFont("Courier New", 16)
                text = font.render(ascii_frame[0], True, (255, 255, 255))
                surface.blit(text, (0, 0))
                frames.append(surface)
                
        elif self.animation_type == "spell":
            # Create spell animation frames (ASCII magic)
            spell_frames = [
                ["  *  "],
                [" *** "],
                ["*****"],
                [" *** "],
                ["  *  "]
            ]
            
            for ascii_frame in spell_frames:
                surface = pygame.Surface((40, 20), pygame.SRCALPHA)
                font = pygame.font.SysFont("Courier New", 16)
                text = font.render(ascii_frame[0], True, (100, 100, 255))
                surface.blit(text, (0, 0))
                frames.append(surface)
        
        return frames
    
    def update(self):
        """Update the animation"""
        if super().update():
            # Calculate current frame based on elapsed time
            elapsed = time.time() - self.start_time
            progress = elapsed / self.duration
            self.current_frame = min(int(progress * len(self.frames)), len(self.frames) - 1)
            return True
        return False
    
    def render(self, screen, position=None):
        """
        Render the current animation frame
        
        Args:
            screen (pygame.Surface): The screen to render to
            position (tuple, optional): Override position
        """
        if not self.is_playing or self.current_frame >= len(self.frames):
            return
            
        # Calculate position between source and target
        if position is None:
            # Get source and target positions
            source_pos = (
                self.source.position[0] + self.source.sprite.get_width() // 2,
                self.source.position[1] + self.source.sprite.get_height() // 2
            )
            target_pos = (
                self.target.position[0] + self.target.sprite.get_width() // 2,
                self.target.position[1] + self.target.sprite.get_height() // 2
            )
            
            # Linear interpolation between source and target
            elapsed = time.time() - self.start_time
            progress = elapsed / self.duration
            
            x = source_pos[0] + (target_pos[0] - source_pos[0]) * progress
            y = source_pos[1] + (target_pos[1] - source_pos[1]) * progress
            
            position = (x, y)
        
        # Render current frame
        frame_width = self.frames[self.current_frame].get_width()
        frame_height = self.frames[self.current_frame].get_height()
        screen.blit(self.frames[self.current_frame], 
                  (position[0] - frame_width // 2, position[1] - frame_height // 2))
