"""
Placeholder for animation helper (to be replaced with sprite animation system)
"""
import pygame
import random

class AnimationHelper:
    """
    Helper class to coordinate animations and visual effects
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
        
        # Animation lists
        self.attack_animations = []
        self.particle_effects = []
        
        # Timing and state
        self.animation_paused = False
    
    def update(self, delta_time):
        """
        Update all animations
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        if self.animation_paused:
            return
            
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
        # Fill with a simple background color
        screen.fill((30, 30, 50))  # Dark blue-gray background
        
        # Render attack animations
        for animation in self.attack_animations:
            animation.render(screen)
        
        # Render simple particle effects
        for particle in self.particle_effects:
            pygame.draw.circle(
                screen,
                particle["color"],
                (int(particle["x"]), int(particle["y"])),
                int(particle["size"] * (particle["life"] / particle["max_life"]))
            )
    
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
        from ui.animation import AttackAnimation
        animation = AttackAnimation(attacker, target, animation_type)
        animation.start()
        self.attack_animations.append(animation)
        
        # Add particle effects for hits
        self.add_hit_particles(target.position[0] + target.sprite.get_width() // 2,
                              target.position[1] + target.sprite.get_height() // 2,
                              animation_type)
    
    def add_hit_particles(self, x, y, effect_type="slash", count=10):
        """
        Add simple particle effects for a hit
        
        Args:
            x (int): X position
            y (int): Y position
            effect_type (str): Type of effect
            count (int): Number of particles
        """
        for _ in range(count):
            if effect_type == "slash":
                color = (255, 0, 0)  # Red for slash
            elif effect_type == "arrow":
                color = (0, 255, 0)  # Green for arrows
            elif effect_type == "spell":
                color = (0, 0, 255)  # Blue for spells
            else:
                color = (255, 255, 255)  # White default
            
            # Create particle
            self.particle_effects.append({
                "x": x,
                "y": y,
                "vx": random.uniform(-30, 30),
                "vy": random.uniform(-30, 30),
                "color": color,
                "size": random.randint(2, 5),
                "life": random.uniform(0.3, 1.0),
                "max_life": random.uniform(0.3, 1.0)
            })
    
    def create_rest_animation(self):
        """
        Create a placeholder for rest animation
        
        Returns:
            object: A placeholder object for rest animation
        """
        from ui.rest_animation import FirePitAnimation
        return FirePitAnimation(self.screen_width, self.screen_height)
    
    def pause_animations(self):
        """Pause all animations"""
        self.animation_paused = True
    
    def resume_animations(self):
        """Resume all animations"""
        self.animation_paused = False