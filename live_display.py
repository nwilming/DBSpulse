import matplotlib
matplotlib.use(u'Qt4Agg')
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
sns.set_style('ticks')
#  Socket to talk to server

# Keep values in a deck to always have a fixed number of samples to display.
maxlen = 1000
dx, dy, dp = deque(maxlen=maxlen), deque(maxlen=maxlen), deque(maxlen=maxlen)
dt = deque(maxlen=maxlen)
tstart = time.time()

class GetET(object):
    def __init__(self):
        context = zmq.Context()
        self.et = context.socket(zmq.SUB)
        self.et.connect("tcp://localhost:5558")
        self.et.connect("tcp://localhost:5559")
        self.et.setsockopt_string(zmq.SUBSCRIBE, u'ET')
        self.et.setsockopt_string(zmq.SUBSCRIBE, u'Trigger')

        self.tstart = time.time()

    def run(self):
        '''
        Read values from pipe.
        '''
        try:
            line = self.et.recv_string(zmq.DONTWAIT)
        except zmq.error.Again:
            return
        if line.startswith('ET '):
            line = line.replace('ET ','')
            try:
                data = cPickle.loads(str(line))
                dx.append(np.mean(data[:, 1]))
                dy.append(np.mean(data[:, 2]))
                dp.append(np.mean(data[:, 3]))
                dt.append(np.mean(data[:, 0]-self.tstart))

            except ValueError:
                print "Can't parse", line
        if line.startswith('Trigger'):
            time = float(line.split(' ')[1])
            plt.axvline(time-self.tstart)



et = GetET()
et.run()

fig, ax = plt.subplots()
linex, = ax.plot([0, 1], [100, 100], 'r-', alpha=0.5)
liney, = ax.plot([0, 1], [100, 100], 'g-', alpha=0.5)
linep, = ax.plot([0, 1], [100, 100], 'b-')
ax.set_ylim(0, 200)


class foo(object):
    def __init__(self):
        self.tstart = np.nan
        self.frame_cnt = 0

    def __call__(self, data):
        if np.isnan(self.tstart):
            self.tstart = time.time()
        et.run()
        linex.set_data(list(dt), list(dx))
        liney.set_data(list(dt), list(dy))
        linep.set_data(list(dt), list(dp))
        t = time.time()-self.tstart
        ax.set_xlim([t-20, t])
        self.frame_cnt += 1
        if np.mod(self.frame_cnt, 100) == 0:
            print "FPS:", self.frame_cnt / (t)
        return linex, liney, linep

ani = animation.FuncAnimation(fig, foo(), interval=25)
plt.show()
