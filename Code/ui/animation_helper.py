"""
Animation helper for coordinating various animations and visual effects
"""
import pygame
import random
from ui.animation import AttackAnimation
from ui.rest_animation import FirePitAnimation
from ui.ascii_background import ASCIIBackground
from ui.ascii_sprites import get_class_sprite, get_enemy_sprite

class AnimationHelper:
    """
    Helper class to coordinate animations and keep track of visual state
    """
    def __init__(self, screen_width, screen_height):
        """
        Initialize the animation helper
        
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create background
        self.background = ASCIIBackground(screen_width, screen_height)
        
        # Animation lists
        self.attack_animations = []
        self.particle_effects = []
        
        # Timing and state
        self.last_update_time = 0
        self.animation_paused = False
    
    def update(self, delta_time):
        """
        Update all animations
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        if self.animation_paused:
            return
            
        # Update background
        self.background.update(delta_time)
        
        # Update attack animations, remove completed ones
        self.attack_animations = [anim for anim in self.attack_animations if anim.update()]
        
        # Update particle effects, remove completed ones
        for i in reversed(range(len(self.particle_effects))):
            particle = self.particle_effects[i]
            particle["life"] -= delta_time
            if particle["life"] <= 0:
                self.particle_effects.pop(i)
            else:
                # Update position
                particle["x"] += particle["vx"] * delta_time
                particle["y"] += particle["vy"] * delta_time
    
    def render(self, screen):
        """
        Render all animations
        
        Args:
            screen (pygame.Surface): The screen to render to
        """
        # Render background
        self.background.render(screen)
        
        # Render attack animations
        for animation in self.attack_animations:
            animation.render(screen)
        
        # Render particle effects
        for particle in self.particle_effects:
            font = pygame.font.SysFont("Courier New", particle["size"])
            text = font.render(particle["char"], True, particle["color"])
            text.set_alpha(int(255 * (particle["life"] / particle["max_life"])))
            screen.blit(text, (particle["x"], particle["y"]))
    
    def add_attack_animation(self, attacker, target, animation_type=None):
        """
        Add an attack animation
        
        Args:
            attacker (BaseCharacter): The attacking character
            target (BaseCharacter): The target character
            animation_type (str, optional): Type of animation ("slash", "arrow", "spell")
        """
        # Determine animation type based on character class or enemy type if not specified
        if animation_type is None:
            if hasattr(attacker, 'enemy_type'):
                if attacker.enemy_type == "dragon":
                    animation_type = "spell"  # Dragon uses spell animation
                else:
                    animation_type = "slash"  # Other enemies use slash
            else:
                # Player character - determine by class
                class_name = attacker.__class__.__name__.lower()
                if class_name == "warrior":
                    animation_type = "slash"
                elif class_name == "archer":
                    animation_type = "arrow"
                elif class_name == "mage":
                    animation_type = "spell"
        
        # Create animation
        animation = AttackAnimation(attacker, target, animation_type)
        animation.start()
        self.attack_animations.append(animation)
        
        # Add particle effects for hits
        self.add_hit_particles(target.position[0] + target.sprite.get_width() // 2,
                              target.position[1] + target.sprite.get_height() // 2,
                              animation_type)
    
    def add_hit_particles(self, x, y, effect_type="slash", count=10):
        """
        Add particle effects for a hit
        
        Args:
            x (int): X position
            y (int): Y position
            effect_type (str): Type of effect
            count (int): Number of particles
        """
        for _ in range(count):
            if effect_type == "slash":
                chars = ["/", "\\", "|", "-"]
                colors = [(255, 0, 0), (255, 50, 50)]
            elif effect_type == "arrow":
                chars = [">", "}", ")", "-"]
                colors = [(0, 255, 0), (50, 255, 50)]
            elif effect_type == "spell":
                chars = ["*", "+", ".", "o"]
                colors = [(0, 100, 255), (100, 100, 255), (200, 100, 255)]
            else:
                chars = ["*", "+", ".", "o"]
                colors = [(255, 255, 255), (200, 200, 200)]
            
            # Create particle
            self.particle_effects.append({
                "x": x,
                "y": y,
                "vx": random.uniform(-30, 30),
                "vy": random.uniform(-30, 30),
                "char": random.choice(chars),
                "color": random.choice(colors),
                "size": random.randint(10, 20),
                "life": random.uniform(0.3, 1.0),
                "max_life": random.uniform(0.3, 1.0)
            })
    
    def create_rest_animation(self):
        """
        Create a fire pit animation for resting
        
        Returns:
            FirePitAnimation: The fire pit animation
        """
        return FirePitAnimation(self.screen_width, self.screen_height)
    
    def pause_animations(self):
        """Pause all animations"""
        self.animation_paused = True
    
    def resume_animations(self):
        """Resume all animations"""
        self.animation_paused = False
