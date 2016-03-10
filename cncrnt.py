'''
Broadcast eye-tracking data and triggers to subscribers.
'''

import sys
sys.path.append('pytrack')  # Dirty dirty hack
from faketrack import tracker
from psychopy import core
import zmq
from multiprocessing import Process
import time

# Set up logging of ET data and trigger detection.
# Starts a new process that does this in the background, communicates pulse
# times through a queue.
track = tracker.Tracker(None, 'test.edf')
context = zmq.Context()

class Watchdog(object):
    '''
    Sets up a function that continuously checks for triggers and ET data and
    dumps it into a pipe.

    Input:
        pipe : filename of the pipe
        tracker : function that returns samples from eye-tracker (x, y, pupil)
        trigger : function that returns a positive number when a trigger occured
    '''

    def __init__(self, port, Hz):
        self.port = port
        self.Hz = Hz


    def run(self, block=True):
        '''
        Input:
        '''
        try:
            self.socket = context.socket(zmq.PUB)
            self.socket.bind("tcp://*:%i"%self.port)
            while True:
                datum = self.message()
                self.socket.send_string(datum)
                print 'send',  datum
                if block:
                    core.wait(1./self.Hz, 1./(self.Hz+2.))
        finally:
            self.socket.close()


    def message(self):
        '''
        Function that returns whatever message should be send.
        '''
        raise NotImplementedError


class ETBroadcast(Watchdog):
    def __init__(self, port, Hz):
        super(self.__class__, self).__init__(port, Hz)

    def message(self):
        x,y,p = track.getFloatData().getAverageGaze()
        return u'ET: %f, %f, %f'%(x,y,p)


class TrigChecker(Watchdog):
    '''
    Dummy class that 'detects' a trigger every IPI seconds.
    '''
    def __init__(self, port, Hz, IPI):
        super(self.__class__, self).__init__(port, Hz)
        self.start = time.time()
        self.IPI = IPI

    def message(self, block=False):
        while True:
            core.wait(self.IPI)
            self.socket.send_string('TRIGGER: %f'%time.time())

if __name__ == '__main__':
    try:
        et = ETBroadcast(5558, 100)
        p = Process(target=et.run)
        p.start()
        trig = TrigChecker(5559, 500, 10)
        p2 = Process(target=trig.run)
        p2.start()
        p2.join()
        p.join()
    except Exception:
        import traceback
        print traceback.format_exc()
        print ''
    finally:
        p.terminate()
        p2.terminate()
