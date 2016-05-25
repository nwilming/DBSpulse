"""
Define some classes for specific trials in the DBS pupil experiment.
"""
from psychopy import core, event
import os


class FixateRelax(object):

    def __init__(self, win, tracker, fixation, fixlength, relaxlength, sock):
        self.win = win
        self.one_frame = 1 / 60.0
        self.tracker = tracker
        self.fixation = fixation
        self.fixlength = fixlength
        self.relaxlength = relaxlength
        self.sock = sock

    def run(self):

        self.win.flip()
        self.sock.send_multipart(('Exp_Info', 'Relaxstart ' + str(self.relaxlength)))
        print 'Relax for %f2.2s'%self.relaxlength
        core.wait(self.relaxlength-self.one_frame, 0.25)
        self.fixation.setColor([.75, 0.25, 0])
        self.fixation.draw()
        self.win.flip()
        self.sock.send_multipart(('Exp_Info', 'Fixstart ' + str(self.fixlength)))
        print 'Fix for %f2.2s'%self.fixlength
        core.wait(self.fixlength-self.one_frame, 0.25)
        self.win.flip()
