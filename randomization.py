#!/usr/bin/env python

'''
Create randomization sequence

The time course of a trial is:
    Relax - Fixation - Relax
    ------------|-----------
    >---<   >--> <-<
     >5s     4s   4s

IPI > (2*4+5 = 13s)

'''

import numpy as np
import time
from random import uniform



def get_sequence(N, IPI=15., pulse_guard=3.5, jitter=1/4.):
    '''
    Make a sequence:
    '''
    jitter = (IPI-2*pulse_guard) * jitter
    print 'Minimum fix time:', 2*pulse_guard
    print 'Minimum relax time:', IPI-(2*pulse_guard+2*jitter)
    print 'Jitter time:', jitter
    pulse_times = np.arange(N)*IPI
    fix_times = []
    cdiff = []
    for pt in pulse_times:
        total_jitter = uniform(0, jitter*2)
        cur_jitter = uniform(0, total_jitter)
        pre = pt-pulse_guard - (total_jitter-cur_jitter)
        post = pt+pulse_guard + (cur_jitter)
        fix_times.append((pre, post))
        cdiff.append(cur_jitter/(total_jitter))

    relax_times = []
    for (_, prev), (nxt, _) in zip(fix_times[:-1], fix_times[1:]):
        relax_times.append((prev, nxt))
    return fix_times, relax_times, pulse_times, np.array(cdiff)

def viz(jtr=1/4.):
    from pylab import *
    f, r, pt, c = get_sequence(5, jitter=jtr)
    for fs, fe in r:
        plot([fs, fe], [.9,0.9], 'g', lw=2)
    for fs, fe in f:
        plot([fs, fe], [1, 1], lw=2)
    plot(arange(0, 70, 15), arange(0, 70, 15)*0+1, 'k|')
    ylim([0, 1.5])
