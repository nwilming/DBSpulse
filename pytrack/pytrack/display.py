import pygame
import pylink
import os

class Display(object):
    def __init__(self, size=(2560, 1600), default_color=128):
        """
        size - width, height tuple specifying the display resolution
        """
        self._default_color = default_color
        self._size = size
        self.doinit()

    def get_wid(self):
        #pipe_in, pipe_out = os.popen2("xwininfo -name 'pygame window' | awk '/Window id/ { print $4; }'")
        #return pipe_out.read().strip()
        w = pygame.display.get_wm_info()
        print w
        # 'window'  'wmwindow' 
        return w['fswindow']

    def clear(self, color=None):
        surf = self.get_surface()
        if not color:
            color = self._default_color
        surf.fill((color,color,color,255))
        pygame.display.flip()

    def doinit(self):
        pygame.init()
        pygame.display.init()
        pygame.display.set_mode(self._size, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.RLEACCEL | pygame.HWSURFACE, 32)
        pygame.mouse.set_visible(False)
        pylink.openGraphics()

    def get_surface(self):
        """
        Get the current Display Surface
        """
        return pygame.display.get_surface()

    def finish(self):
        pylink.closeGraphics()
        pygame.display.quit()
