#!/usr/bin/env python


import numpy as np

import os, sys
from psychopy import core
import time

pipe = '/tmp/DBS.pipe'
try:
    os.remove(pipe)
except OSError:
    pass
os.mkfifo(pipe)
pipe = open(pipe, 'r', 1)
start = time.time()
while True:
    line = pipe.readline()
    print time.time() - start, line
