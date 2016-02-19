#!/usr/bin/env python

'''
Run a DBS single pulse fixation/relax block.
'''
import sys
sys.path.append('pytrack')

from psychopy import visual,  core, logging, event
from faketrack import tracker
import trials
import numpy as np
import time
import random
import os, sys
from multiprocessing import Process, Queue

# Set inter pulse interval
IPI = 10.

track = tracker.Tracker(None, 'test.edf')

# Set up logging of ET data and trigger detection.
# Starts a new process that does this in the background, communicates pulse
# times through a queue.

def logetandtrigger(pipe, tracker, trigger):
    '''
    Checks for triggers and eye tracking data and dumps it into a pipe.
    '''

    pipe = open(pipe, 'w', 1)
    def run(q, qin, stdout):
        x,y,p = tracker()
        stdout.write('Inside run!\n')
        stdout.flush()
        while True:
            x,y,p = tracker()
            pipe.write('%f, %f, %f\n'%(x,y,p))
            t = trigger()
            if t > 0:
                print 'Trigger'
                pipe.write('trigger\n')
                q.put(time.time())
            core.wait(1/10., 1/9.)
            if not qin.empty():
                return
    return run, pipe

class TrigChecker(object):
    def __init__(self, IPI):
        self.start = time.time()

    def __call__(self):
        if time.time() > (self.start + IPI):
            self.start = time.time()
            return 1
        return 0

#try:
qin, qout = Queue(), Queue()
logging, pipe = logetandtrigger('/tmp/DBS.pipe', track.getFloatData().getAverageGaze, TrigChecker(IPI))
p = Process(target=logging, args=(qin, qout, sys.stdout))
p.start()

win = visual.Window((100,100),
					monitor='mac_default',
                    fullscr = False,
                    allowGUI = False,
                    winType = 'pyglet',
                    waitBlanking = False,
                    units='deg')
# Some stimuli
patch = visual.Circle(win, lineColor=None, fillColor=1, fillColorSpace='rgb', pos=(0, 1.5), radius=1.5, edges=64, interpolate=True)
fixation = visual.GratingStim(win, color=[1,0,0], colorSpace='rgb', tex=None, mask='circle',size=0.2)

print 'Waiting for first trigger to sync.'
while not qin.empty():
    qin.get(block=False)
pulse_time = qin.get(block=True)

buff = IPI - 8 # Total amount of buffer available, this needs to accomodate relax and variable ITI
jitter = random.uniform(0, buff-1)
relaxlength = IPI/2. + buff - jitter - (time.time()-pulse_time)
fixlength = 8 + jitter
for i in range(2):
    t = trials.FixateRelax(win, tracker, fixation, fixlength, relaxlength)
    t.run()
    # Determine next trial length
    pulse_time = qin.get(block=False)
    print 'Pulse Time', pulse_time, time.time()-pulse_time
    # This is the end of the fixation period -> Calculate how much time left till next pulse
    time_left = IPI - (time.time()-pulse_time)
    buff = time_left - 4
    print time_left, buff
    jitter = random.uniform(0, buff-1)
    relaxlength = buff - jitter
    fixlength = 8 + jitter + random.uniform(0, buff-1)

#except Exception as e:
#    print e
#finally:
qout.put('end')
print 'Terminated'
p.join()
p.terminate()
pipe.write('END')
pipe.close()
win.close()
