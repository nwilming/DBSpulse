import pygame
import os

class Display(object):
    def __init__(self, size=(2560, 1600), default_color=128, fullscreen = 1):
        """
        size - width, height tuple specifying the display resolution
        fullscreen - 0 or 1
        """
        self._default_color = default_color
        self._size = size
        self._full = fullscreen * pygame.FULLSCREEN 
        self.doinit()

    def get_wid(self):
        try:
            w = pygame.display.get_wm_info()['fswindow']
        except:
            w = '1'
        return w

    def clear(self, color=None):
        surf = self.get_surface()
        if not color:
            color = self._default_color
        surf.fill((color,color,color,255))
        pygame.display.flip()

    def doinit(self):
        pygame.init()
        pygame.display.init()
        pygame.display.set_mode(self._size, self._full | pygame.DOUBLEBUF | pygame.RLEACCEL | pygame.HWSURFACE, 32)
        pygame.mouse.set_visible(False)

    def get_surface(self):
        """
        Get the current Display Surface
        """
        return pygame.display.get_surface()

    def finish(self):
        pygame.display.quit()
