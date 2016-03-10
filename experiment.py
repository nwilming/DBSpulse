#!/usr/bin/env python

'''
Run a DBS single pulse fixation/relax block.

This scripts runs a set of trials and reads ET data and dumps it into a pipe.
The ET data can then be read from the pipe by some other program. Importantly
the experiment continues only when the pipe is openend by some other program.

Important:
 -> Start the other end of the pipe before the experiment! <-

Pipe could be made optional in the future.

ET data is read in a different process.

TODO:
    - Timing of the trials not yet correct.
    - Trial onsets should also be pushed into the pipe.
'''
import sys
sys.path.append('pytrack')  # Dirty dirty hack
from psychopy import visual,  core, logging, event
from faketrack import tracker
import trials
import numpy as np
import time
import random
import os, sys
from multiprocessing import Process, Queue
import zmq

# Set inter pulse interval
IPI = 10.



# Queues to allow communication between experiment and data collection
qin, qout = Queue(), Queue()
# Set up and start data collection
logging, pipe = logetandtrigger('/tmp/DBS.pipe', track.getFloatData().getAverageGaze, TrigChecker(IPI))
p = Process(target=logging, args=(qin, qout))
p.start()

# Open a window for experiment
win = visual.Window((500,500),
					monitor='mac_default',
                    fullscr = False,
                    allowGUI = False,
                    winType = 'pyglet',
                    waitBlanking = True,
                    units='deg')

# Some stimuli
patch = visual.Circle(win, lineColor=None, fillColor=1, fillColorSpace='rgb', pos=(0, 1.5), radius=1.5, edges=64, interpolate=True)
fixation = visual.GratingStim(win, color=[1,0,0], colorSpace='rgb', tex=None, mask='circle',size=0.2)

# Need to wait for first trigger to be able to sync trials with triggers.
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
