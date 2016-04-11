'''
Broadcast eye-tracking data and triggers to subscribers.

Contains one class for Broadcasting of eye tracking data (ETBroadcast) and one
for EMG data.

Both are started in parallel and continuously detect / transmit data. Done in a
CPU hogging way.
'''

import sys
sys.path.append('pytrack')  # Dirty dirty hack
from faketrack import tracker
from psychopy import core
import zmq
from multiprocessing import Process
import time
import RDA
import numpy as np
import cPickle

# Set up logging of ET data and trigger detection.
# Starts a new process that does this in the background, communicates pulse
# times through a queue.
track = tracker.Tracker(None, 'test.edf')
context = zmq.Context()


class ETBroadcast(object):
    def __init__(self, port, Hz):
        self.port = port
        self.Hz = Hz

    def run(self, block=False):
        '''
        Input:
        '''
        try:
            self.socket = context.socket(zmq.PUB)
            self.socket.bind("tcp://*:%i"%self.port)
            print 'Configured 0MQ socket on port', self.port
            # ET samples at 1000Hz, so collect 1s of samples and send them over
            data = []
            while True:
                data.append(self.message())
                if data[-1][0]-data[0][0]>0.05:
                    data = np.array(data)
                    msg = 'ET ' + cPickle.dumps(data, protocol=0)
                    self.socket.send_string(msg)
                    data = []
                #if block:
                #    core.wait(1./self.Hz)
        finally:
            self.socket.close()

    def message(self):
        return track.getFloatData().getCurentGaze()


class TrigChecker(object):
    '''
    Dummy class that 'detects' a trigger every IPI seconds.
    '''
    def __init__(self, port, Hz, IPI):
        self.port = port
        self.Hz = Hz
        self.start = time.time()
        self.IPI = IPI

    def run(self, block=True):
        try:
            self.socket = context.socket(zmq.PUB)
            self.socket.bind("tcp://*:%i"%self.port)
            with RDA.EEGTrigger(fake=self.IPI) as et:
                while True:
                    datum = et.trigger()
                    if datum:
                        self.socket.send_string(u'Trigger %f'%time.time())
                        print 'Trigger!'
                    core.wait(1./50, 1./(50.+2.))
        finally:
            self.socket.close()

if __name__ == '__main__':
    try:
        et = ETBroadcast(5558, 250)
        p = Process(target=et.run)
        p.start()
        trig = TrigChecker(5559, 500, 15.)
        p2 = Process(target=trig.run)
        p2.start()
        p2.join()
        p.join()
    except Exception:
        import traceback
        print traceback.format_exc()
        print ''
        p.terminate()
        p2.terminate()
    finally:
        p.terminate()
        p2.terminate()
