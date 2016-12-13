'''
Broadcast triggers to subscribers.
'''

import sys
sys.path.append('pytrack')  # Dirty dirty hack
from psychopy import core
import zmq
import time
import RDA
import numpy as np
import cPickle

# Set up logging of ET data and trigger detection.
# Starts a new process that does this in the background, communicates pulse
# times through a queue.
context = zmq.Context()

class TrigChecker(object):
    '''
    Dummy class that 'detects' a trigger every IPI seconds.
    '''
    def __init__(self, port, Hz, IPI):
        self.port = port
        self.Hz = Hz
        self.start = time.time()
        self.IPI = IPI
        self.last_trig = 0

    def run(self, block=True):
        try:
            print 'Setting up trigger detect'
            self.socket = context.socket(zmq.PUB)
            self.socket.bind("tcp://*:%i"%self.port)
            with RDA.EEGTrigger(fake=False) as et:
                while True:
                    datum = et.trigger()
                    if datum and ((time.time()-self.last_trig)>2.):
                        self.socket.send_multipart(('Trigger', '%f'%time.time()))
                        #print 'Trigger!'
                        self.last_trig = time.time()
        finally:
            self.socket.close()

if __name__ == '__main__':
    trig = TrigChecker(5559, np.nan, 15.)
    trig.run()
