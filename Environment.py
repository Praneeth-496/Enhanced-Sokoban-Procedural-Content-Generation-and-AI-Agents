"""
Environment class for Sokoban game
Handles game environment setup and screen management
"""

import pygame
import os

class Environment:
    def __init__(self, width=800, height=600):
        """Initialize the game environment"""
        # Initialize pygame
        if not pygame.get_init():
            pygame.init()
        
        # Set up the screen
        self.size = self.width, self.height = width, height
        self.screen = pygame.display.set_mode(self.size)
        
        # Set up the game path
        self.path = os.path.dirname(os.path.abspath(__file__))
    
    def getPath(self):
        """Return the game path"""
        return self.path
    
    def getScreen(self):
        """Return the game screen"""
        return self.screen
    
    def getSize(self):
        """Return the screen size"""
        return self.size
