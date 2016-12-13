#!/usr/bin/env python

'''
Run a DBS single pulse fixation/relax block.

This scripts runs a set of trials which need to be synchronized with an external
EMG based trigger. This is detected in a different program ('cncrnt.py') which
streams data via a zmq socket. The experiment subscribes to these messages and
starts a trial after a trigger.
'''
from psychopy import visual,  core, logging, event

import sys
sys.path.append('pytrack')  # Dirty dirty hack
from faketrack import tracker
import trials
import numpy as np
import os, sys, random, time
from multiprocessing import Process, Queue
import zmq
import randomization

# Set inter pulse interval
IPI = 10.5
context = zmq.Context()


# This one provides experiment meta data.
meta = context.socket(zmq.PUB)
meta.bind("tcp://172.18.100.65:5560")

# This connects to the EEG amplifier / streaming
et = context.socket(zmq.SUB)
et.connect("tcp://172.18.102.176:5559")
et.setsockopt_string(zmq.SUBSCRIBE, u'Trigger')




# Open a window for experiment
mywin = visual.Window((500, 500),
                    monitor="DBS",
                    fullscr = False,
                    allowGUI = False,
                    winType = 'pyglet',
                    waitBlanking = True,
                    units='deg')

# Some stimuli
patch = visual.Circle(win = mywin, lineColor=None, fillColor=1, fillColorSpace='rgb', pos=(0, 0), radius=1.5, edges=64, interpolate=True)
fixation = visual.GratingStim(win = mywin, color=[1,0,0], colorSpace='rgb', tex=None, mask='circle',size=1.2)

def get_trigger():
    print 'Waiting for trigger!'
    trigger, msg = et.recv_multipart()
    return float(msg)

# Set up timing
fix_times, relax_times, pulse_times, diffs = randomization.get_sequence(45, IPI=IPI, pulse_guard=2.5, jitter=1/4.)
fix_times = fix_times[1:]
relax_times = relax_times[:-1]
pulse_times = pulse_times[1:]

fix_times = np.array(fix_times)
relax_times = np.array(relax_times)
pulse_times = np.array(pulse_times)

#first_start = get_trigger()
start = get_trigger()
#print 'IPI:', start-first_start
sync_err = 0

for trial in range(len(fix_times)-1):
    fix_times += sync_err
    pulse_times += sync_err
    relax_times += sync_err
    (fixstart, fixend), (relaxstart, relaxend), pt = fix_times[trial], relax_times[trial], pulse_times[trial]
    relaxstart -= sync_err

    # pt is expected next trigger time.
    meta.send_multipart(('Exp_Info', 'Trial ' + str(trial)))

    if trial == 0:
        t = trials.FixateRelax(mywin, tracker, fixation, fixend-fixstart, relaxend, meta)
    else:
        print '--> Fixtime: %3.2f'%(fixend-fixstart)
        print '--> Relaxtime: %3.2f'%(relaxend-relaxstart)

        t = trials.FixateRelax(mywin, tracker, fixation, fixend-fixstart, relaxend-relaxstart, meta)

    t.run()

    # Measure when the trigger actually occured
    trigger = get_trigger()
    sync_err = (trigger-start)-pt # + if trigger was later than expected, - if it was too early
    print 'Trigger: %3.2f'%(trigger-start), 'Expected: %3.2f'%pt
    print 'Syncerr:', sync_err
    if abs(sync_err) > 100:
        raise RuntimeError('Sync err is larger than 1s: Improve trigger detection')


mywin.close()
