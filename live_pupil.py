import matplotlib
# matplotlib.use(u'Qt4Agg')
import numpy as np
import time
from collections import deque
from multiprocessing import Process
from psychopy import core
import zmq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cPickle
import seaborn as sns
import json
import configure
sns.set_style('ticks')
#  Socket to talk to server

# Keep values in a deck to always have a fixed number of samples to display.
maxlen = 1000
dx, dy, dp1, dp2 = deque(maxlen=maxlen), deque(maxlen=maxlen), deque(maxlen=maxlen), deque(maxlen=maxlen)
dp = [dp1, dp2]
dt = deque(maxlen=maxlen)
dtp1 = deque(maxlen=maxlen)
dtp2 = deque(maxlen=maxlen)
dtp = [dtp1, dtp2]

tstart = time.time()

class GetET(object):
    def __init__(self):
        context = zmq.Context()
        self.et = context.socket(zmq.SUB)
        self.trig = context.socket(zmq.SUB)
        self.et.set_hwm(1)
        #self.et.connect("tcp://172.18.100.19:%i"%5000)
        #self.trig.connect("tcp://localhost:5559")
        self.et.connect("tcp://%s"%(configure.eyetracking_ip))
        self.trig.connect("tcp://%s:5559"%(configure.concurrent_ip))
        self.et.setsockopt_string(zmq.SUBSCRIBE, u'gaze_positions')
        self.trig.setsockopt_string(zmq.SUBSCRIBE, u'Trigger')

        self.tstart = time.time()

    def run(self):
        '''
        Read values from pipe.
        '''
        topic, msg = '', ''
        ls = time.time()
        while (time.time()-ls)<(1/60.):
            try:
                topic, msg =  self.et.recv_multipart(zmq.DONTWAIT)
                msg = json.loads(msg)
                if len(msg)>0:
                    try:
                        x,y = msg[-1]['norm_pos']
                        if 'diameter_3d' in msg[-1]['base'][0].keys():
                            pupil = msg[-1]['base'][0]['diameter_3d']
                        else:
                            for m in msg:
                                pupil = m['base'][0]['diameter']
                                id = m['base'][0]['id']
                                dp[id].append(pupil)
                                dtp[id].append(time.time()-self.tstart)
                        dt.append(time.time()-self.tstart)

                    except ValueError:
                        print "Can't parse", line
            except zmq.error.Again:
                break
        try:
            topic, msg =  self.trig.recv_multipart(zmq.DONTWAIT)
            print 'Trigger!'
            t = time.time()
            return t-self.tstart #ax.axvline(t-self.tstart)

        except zmq.error.Again:
            pass




et = GetET()
et.run()

fig, ax = plt.subplots()

linep, = ax.plot([0, 1], [0, 0], 'g-')
linep2, = ax.plot([0, 1], [0, 0], 'r-')
ax.set_ylim(2, 120)

trigger_list = deque(maxlen=5)
class foo(object):
    def __init__(self, et=False):
        self.tstart = np.nan
        self.frame_cnt = 0
        self.pupil_mean = 0
        self.pupil_std = 1

    def __call__(self, data):
        if np.isnan(self.tstart):
            self.tstart = time.time()
        trigger = et.run()
        lines = []
        if trigger is not None:
            vl = ax.axvline(trigger)
            trigger_list.append(vl)
        dtt = list(dt)

        linep.set_data(list(dtp[0]), list(dp[0]))
        linep2.set_data(list(dtp[1]), list(dp[1]))
        t = time.time()-self.tstart
        ax.set_xlim([t-20, t+5])
        self.frame_cnt += 1
        if np.mod(self.frame_cnt, 100) == 0:
            print "FPS:", self.frame_cnt / (t)
        return list(trigger_list)+[linep]

ani = animation.FuncAnimation(fig, foo(), interval=1, blit=False)
plt.show()
