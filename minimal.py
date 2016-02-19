#!/usr/bin/env python

'''
minimal test
'''

from psychopy import visual,  core, logging, event
from faketrack import tracker
import trials
import numpy as np
import time
import random
import os, sys
from multiprocessing import Process, Queue

track = tracker.Tracker(None, 'test.edf')

# Set up logging of ET data and trigger detection.
# Starts a new process that does this in the background, communicates pulse
# times through a queue.

def logetandtrigger(pipe, tracker, trigger):
    '''
    Checks for triggers and eye tracking data and dumps it into a pipe.
    '''
    try:
        os.remove(pipe)
    except OSError:
        pass
    os.mkfifo(pipe)
    pipe = open(pipe, 'w')
    def run(q, qin, stdout):
        x,y,p = tracker()
        stdout.write('Inside run!\n')
        stdout.flush()
        while True:
            x,y,p = tracker()
            pipe.write('%f, %f, %f\n'%(x,y,p))
            t = trigger()
            if t < 0.01:
                pipe.write('trigger\n')
                q.put(time.time())
            core.wait(1/100., 1/110.)
            if not qin.empty():
                return
    return run, pipe

def trigger():
    return np.mod(time.time(), 2)

try:
    qin, qout = Queue(), Queue()
    logging, pipe = logetandtrigger('/tmp/DBS.pipe', track.getFloatData().getAverageGaze, trigger)
    p = Process(target=logging, args=(qin, qout, sys.stdout))
    p.start()
    print 'Waiting for first trigger to sync.'
    pulse_time = qin.get(block=True)

    for i in range(200):
        pulse_time = qin.get(block=True)

except Exception as e:
    print e
finally:
    qout.put('end')
    print 'Terminated'
    p.join()
    p.terminate()
    pipe.close()
