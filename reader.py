#!/usr/bin/env python
'''
Receive eye tracking data from experiment and display the data in a scrolling
window as it comes in.

Use ``bokeh serve --show reader.py`` to open the plot in your browser.
'''
import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.models import Range1d
import os, sys
from psychopy import core
import time
from collections import deque


# Open pipe for reading
import zmq
#  Socket to talk to server


# Set up things for the bokeh plot
start = time.time()
xr = Range1d(0, 20)
pfig = figure(x_range=xr, y_range=(0, 150), width=1300)

rx = pfig.line(x=[], y=[], color='#BE1687')
ry = pfig.line(x=[], y=[], color='#00F536')
rp = pfig.line(x=[], y=[], color='#F9E51D')
dss = [rx.data_source, ry.data_source, rp.data_source]

# Keep values in a deck to always have a fixed number of samples to display.
maxlen = 1000
dx, dy, dp = deque(maxlen=maxlen), deque(maxlen=maxlen), deque(maxlen=maxlen)
dt = deque(maxlen=maxlen)

class GetET(object):
    def __init__(self):
        context = zmq.Context()
        self.et = context.socket(zmq.SUB)
        print("Collecting updates ETBroadcast")
        self.et.connect("tcp://localhost:5558")
        self.et.setsockopt_string(zmq.SUBSCRIBE, u'ET')

    def __call__(self):
        '''
        Read values from pipe.
        '''
        line = self.et.recv_string()
        if line.startswith('t'):
           return 'trigger'
        elif line.startswith('ET:'):
            line = line.replace('ET:','')
            try:
                x,y,p = line.split(',')
                return float(x), float(y), float(p)
            except ValueError:
                pass
        return None


def get_callback(et):
    def callback():
        '''
        Updates figure
        '''
        t = time.time() - start
        v = et()
        print v
        if v == 'trigger':
            # Draw line for trigger
            pfig.line(x=[t, t], y=[0, 150], color="#F0027F", line_width=2)
        elif v is not None:
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
    return callback


curdoc().add_periodic_callback(get_callback(GetET()), 1/200.)
