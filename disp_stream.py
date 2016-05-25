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
et = context.socket(zmq.SUB)
et.connect("tcp://localhost:5559")
et.setsockopt_string(zmq.SUBSCRIBE, u'')
et2 = context.socket(zmq.SUB)
et2.connect("tcp://localhost:5560")
et2.setsockopt_string(zmq.SUBSCRIBE, u'')
while True:
    try:
        trigger = et.recv_multipart(zmq.DONTWAIT)
        print trigger
    except zmq.error.Again:
        pass
    try:
        trigger = et2.recv_multipart(zmq.DONTWAIT)
        print trigger
    except zmq.error.Again:
        pass
