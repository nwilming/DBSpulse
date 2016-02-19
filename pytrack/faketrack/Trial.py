import pygame
import time
import os

BINOCULAR = 2
LEFT_EYE = 0
RIGHT_EYE = 1

class BasicTrial(object):
    def __init__(self, disp, track, filename):
        self._disp = disp
        self._track = track
        self._filename = filename


class Image(BasicTrial):
    def __init__(self, disp, track, filename):
        BasicTrial.__init__(self, disp, track, filename)
        self._bmp = pygame.image.load(filename)

    def run(self, duration=10000):
        surf = self._disp.get_surface()
        self._track.start_trial()
        surf.blit(self._bmp, (0,0))
        pygame.display.flip()
        self._track.sendMessage("SYNCTIME %d" % 0)
        time.sleep(duration/1000.0)
        self._track.end_trial()


class MPlayer(BasicTrial):
    #TODO try -idle and cmd loadfile for pre-loading
    """
    Encapsulates a mplayer instance for movie playback
    Spawns a pre-caching child upon creation
    """
    # mplayer command line
    CMD = 'mplayer -monitorpixelaspect 1 -nosound -hardframedrop -vo xv -cache %d %s -slave %s'
    # kb cache for mplayer (max=1GB=1048576) and dd
    CACHE = 1048576

    def __init__(self, disp, track, filename, options='2>/dev/null'):
        """
        options - string with additional options for mplayer
        """
        BasicTrial.__init__(self, disp, track, filename)
        self._options = options
        os.system("dd if='%s' of=/dev/null bs=1k count=%d &" % (filename, self.CACHE))
        self._wid = disp.get_wid()

    def run(self):
        """
        filename - string with the movie to play
         xwininfo -tree -name "python"
        """
        self._track.start_trial()
        self._disp.clear(0)
        self._disp.get_surface().unlock()
        self._disp.finish()
        command = self.CMD % (self.CACHE, self._filename, self._options)
        os.system('killall -KILL dd')
        start = time.time()
        pipe_in, pipe_out = os.popen2(command)
        # wait until caching complete
        while 1:
            r = pipe_out.readline()
            if not r: return
            if r[:3] == 'VO:':
                break
        if self._track:
            self._track.sendMessage("SYNCTIME %d" % (1000*(time.time()-start)))
        # wait until playback complete
        while pipe_out.read(): pass
        self._disp.doinit()
        self._track.end_trial()


