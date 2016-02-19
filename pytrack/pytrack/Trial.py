class BasicTrial(object):
	def __init__(self, disp, track, filename):
		self._disp = disp
		self._track = track
		self._filename = filename

import pygame
import pylink

HAS_GCWIN = False
try: 
    from gcwin.gcwin import GC
    HAS_GCWIN = True
except ImportError:
    pass

BINOCULAR = 2
LEFT_EYE = 0
RIGHT_EYE = 1

if HAS_GCWIN:
    class GazeContingent(BasicTrial):
            def __init__(self, disp, track, ring_width, filenames):
                    BasicTrial.__init__(self, disp, track, filenames)
                    self._gc = GC(ring_width, filenames)
            def run(self, duration=10000):
                    self._track.start_trial()
                    # choose which eye to follow
                    eye = self._track.eyeAvailable()
                    if eye == BINOCULAR: eye = LEFT_EYE
                    # render first frame at screen center
                    start = pylink.currentTime()
                    self._gc.render(1024/2, 768/2)
                    target = pylink.currentTime()
                    self._track.sendMessage("SYNCTIME %d" % (target-start))
                    target += duration
                    while self._track.recording() and pylink.currentTime()<target:
                            sample = self._track.getNewestSample()
                            if sample:
                                    if eye == LEFT_EYE and sample.isLeftSample():
                                            x, y = sample.getLeftEye().getGaze()
                                    elif eye == RIGHT_EYE and sample.isRightSample():
                                            x, y = sample.getLeftEye().getGaze()
                                    else:
                                            continue
                                    self._gc.render(x, y)
                    self._track.end_trial()
                    self._gc = None
                    del self._gc




class Image(BasicTrial):
	def __init__(self, disp, track, filename):
		BasicTrial.__init__(self, disp, track, filename)
		self._bmp = pygame.image.load(filename)

	def run(self, duration=10000):
		surf = self._disp.get_surface()
		self._track.start_trial()
		start = pylink.currentTime()
		surf.blit(self._bmp, (0,0))
		pygame.display.flip()
		target = pylink.currentTime()
		self._track.sendMessage("SYNCTIME %d" % (target-start))
		target += duration
		while self._track.recording() and pylink.currentTime()<target:
			pass
		self._track.end_trial()


class Audio(BasicTrial):
	def __init__(self, disp, track, filename, audiofile):
		BasicTrial.__init__(self, disp, track, filename)
		self._bmp, self._aud = None, None
		if filename:
			self._bmp = pygame.image.load(filename)
		if audiofile:
			self._aud = pygame.mixer.Sound(audiofile)

	def run(self, duration=10000):
		surf = self._disp.get_surface()
		self._track.start_trial()
		start = pylink.currentTime()
		if self._bmp:
			surf.blit(self._bmp, (0,0))
			pygame.display.flip()
		self._track.sendMessage("SYNCTIME %d" % (pylink.currentTime()-start))
		start = pylink.currentTime()
		if self._aud:
			self._aud.play()
			self._track.sendMessage("PLAYTIME %d" % (pylink.currentTime()-start))
		while self._track.recording() and pylink.currentTime()-start<duration:
			pass
		self._track.end_trial()
		self._disp.clear()


import os
from time import time

class MPlayer(BasicTrial):
	#TODO try -idle and cmd loadfile for pre-loading
	"""
	Encapsulates a mplayer instance for movie playback
	Spawns a pre-caching child upon creation
	"""
	# mplayer command line
#	CMD = 'mplayer -wid %s -nosound -hardframedrop -vo xv -cache %d %s -slave %s'
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
#		command = self.CMD % (self._wid, self.CACHE, self._filename, self._options)
		command = self.CMD % (self.CACHE, self._filename, self._options)
		os.system('killall -KILL dd')
		start = pylink.currentTime()
		pipe_in, pipe_out = os.popen2(command)
		# wait until caching complete
		while 1:
			r = pipe_out.readline()
			if not r: return
			if r[:3] == 'VO:':
				break
		if self._track:
			self._track.sendMessage("SYNCTIME %d" % (pylink.currentTime()-start))
		# wait until playback complete
		while pipe_out.read(): pass
		self._disp.doinit()
		self._track.end_trial()


if __name__ == "__main__":
	from sys import argv
	for a in argv[1:]:
		if a[-3:]=="avi":
			t = MPlayer(None, None, a)
			t.run()
