import gc
import time
import pygame
import random

class EyeLinkError(Exception): pass


class Tracker(object):
    """
    Encapsultes calls to the Eyelink II Host
    """
    def __init__(self, display, filename="TEST.EDF"):
        pass
        #try:
            #self._disp = display

            #self._surfs = self._disp.get_surface().get_rect()
            #col = display._default_color
        #except AttributeError:
        #    self._surfs = display.get_rect()

    def set_calibration(self, points):
        pass

    def setup(self):
        pass

    def recording(self):
        return True

	def inSetup(self, val=False):
		return val

    def sendMessage(self, arg):
        print "Message:", arg


    def sendCommand(self, cmd):
        print "Command:", cmd


    def drift(self, x=None, y=None):
        """
        Start Drift Correction
        """
        print "Drift Correction @ ", x, y

    def metadata(self, key, value):
        """
        Send per-experiment Metadata
        """
        print "Meta per Experiment:", key, value


    def trialmetadata(self, key, value):
        """
        Send per-trial metadata
        """
        print "Meta per Trial:", key, value


    def trial(self, id, trial={}):
        """
        Announce a new trial with index 'id' and metadata 'trial'
        """
        print "Starting trial", id, trial

    def start_trial(self):
        """
        Start recording eyetraces
        """
        print "Start recording"

    def end_trial(self):
        """
        Stop recording eyetraces
        """
        print "Stop recording"

    def finish(self):
        """
        Finalize the experiment
        """
        print "Finalizing"

    def eyeAvailable(self):
        return 2 # binocular

    def getNextData(self):
        return 8 # fixation data

    def getFloatData(self):
        return FloatData()


class PsychoTracker(Tracker):
    """
    Encapsulates calls to the Eyelink II Host
    """
    def __init__(self, win, filename="TEST.EDF"):
        self.win = win
        self._surfs = pygame.display.get_surface()


class FloatData:
    def getAverageGaze(self):
        return (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
    def getEye(self):
        return 0 # left eye
