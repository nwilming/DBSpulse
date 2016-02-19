#!/usr/bin/env python

''' Present a plot updating according to a set of fixed timeout
intervals.
Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve timeout.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/timeout
in your browser.
'''

import numpy as np

from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc
from bokeh.models import Range1d
import os, sys
from psychopy import core
import time
from collections import deque


pipe = '/tmp/DBS.pipe'
try:
    os.remove(pipe)
except OSError:
    pass
os.mkfifo(pipe)
pipe = open(pipe, 'r', 1)


start = time.time()
xr = Range1d(0, 20)
pfig = figure(x_range=xr, y_range=(0, 150), width=1300)

rx = pfig.line(x=[], y=[], color='#BE1687')
ry = pfig.line(x=[], y=[], color='#00F536')
rp = pfig.line(x=[], y=[], color='#F9E51D')
dss = [rx.data_source, ry.data_source, rp.data_source]

maxlen = 1000
dx, dy, dp = deque(maxlen=maxlen), deque(maxlen=maxlen), deque(maxlen=maxlen)
dt = deque(maxlen=maxlen)
def get_vals():

    line = pipe.readline()
    if line.startswith('t'):
       return 'trigger'
    elif line is not '':
        x,y,p = line.split(',')
        return float(x), float(y), float(p)
    return None



def make_callback():
    def func():
        t = time.time() - start
        v = get_vals()
        if v is None:
            return
        if v == 'trigger':
            pfig.line(x=[t, t], y=[0, 150], color="#F0027F")
        else:
            x,y,p = v
            dx.append(x)
            dy.append(y)
            dp.append(p)
            dt.append(t)
            for ds, d in zip(dss, [dx, dy, dp]):
                ds.data['y'] = list(d)
                ds.data['x'] = list(dt)
                ds.trigger('data', ds.data, ds.data)
            pfig.x_range.start = t-10
            pfig.x_range.end =  t+10

    return func

callback = make_callback()
callback.callback = callback
curdoc().add_periodic_callback(callback, 1/30.)
