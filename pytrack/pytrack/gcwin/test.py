import pygame
import time
from gcwin import GC

pygame.display.init()
res = (1280, 1024)
print pygame.display.set_mode(res, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.RLEACCEL | pygame.HWSURFACE, 32).get_size()

#f = GC(40, ('foo.jpg',10))
f = GC(40, ['foor.jpg','foog.jpg','foob.jpg'])
s = time.time()
a, c = 0, 0.0
while time.time()-s<10:
         x, y = pygame.mouse.get_pos()
         pygame.event.clear()
         a += f.render(res[0]-x,res[1]-y)
         c +=1
print a/c
