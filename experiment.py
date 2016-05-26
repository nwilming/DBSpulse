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
IPI = 15.
context = zmq.Context()


meta = context.socket(zmq.PUB)
meta.bind("tcp://*:5560")

et = context.socket(zmq.SUB)
et.connect("tcp://localhost:5559")
et.setsockopt_string(zmq.SUBSCRIBE, u'Trigger')




# Open a window for experiment
mywin = visual.Window((400,400),
                    monitor = 'mac_default',
                    fullscr = False,
                    allowGUI = False,
                    winType = 'pyglet',
                    waitBlanking = True,
                    units='deg')

# Some stimuli
patch = visual.Circle(win = mywin, lineColor=None, fillColor=1, fillColorSpace='rgb', pos=(0, 0), radius=1.5, edges=64, interpolate=True)
fixation = visual.GratingStim(win = mywin, color=[1,0,0], colorSpace='rgb', tex=None, mask='circle',size=0.2)

def get_trigger():
    trigger, msg = et.recv_multipart()
    return float(msg)

# Set up timing
fix_times, relax_times, pulse_times, diffs = randomization.get_sequence(15, IPI=IPI, pulse_guard=3.5, jitter=1/4.)
fix_times = fix_times[1:]
relax_times = relax_times[:-1]
pulse_times = pulse_times[1:]

start = get_trigger()
start = get_trigger()
sync_err = 0

for n, ((fixstart, fixend), (relaxstart, relaxend), pt) in enumerate(zip(fix_times, relax_times, pulse_times)):
    # pt is expected next trigger time.
    meta.send_multipart(('Exp_Info', 'Trial ' + str(n)))

    if n == 0:
        t = trials.FixateRelax(mywin, tracker, fixation, fixend-fixstart, relaxend, meta)
    else:
        print '--> Fixtime: %3.2f'%(fixend-fixstart)
        print '--> Relaxtime: %3.2f'%(relaxend-relaxstart)

        t = trials.FixateRelax(mywin, tracker, fixation, fixend-fixstart, relaxend-relaxstart-sync_err, meta)

    t.run()

    # Measure when the trigger actually occured
    trigger = get_trigger()
    sync_err = (trigger-start)-pt # + if trigger was later than expected, - if it was too early
    print 'Trigger: %3.2f'%(trigger-start), 'Expected: %3.2f'%pt
    print 'Syncerr:', sync_err
    if abs(sync_err) > 1:
        raise RuntimeError('Sync err is larger than 1s: Improve trigger detection')


mywin.close()
