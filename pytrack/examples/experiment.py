#!/usr/bin/python

from pytrack import *
import pytrack

# Import randomization from matlab data file
rand = Matlab("randorders.mat")

# Ask user for index of current subject
sel = Dialog.Int("Subject Index (0 to %d):" % len(rand))

# And use the selected randomization
trials = rand[sel]

# Example: start from a later trial (e.g. 10):
#trials = trials[10:]

# Ask for the filename of the EDF
filename = Dialog.Str("EDF File:", "SUB%03d.EDF" % sel)

# Setup the system and screen resolution
disp = Display((2560, 1600))
track = Tracker(disp, filename)

# Send subject index as metadata to EDF
track.metadata("SUBJECTINDEX", sel)

# Example: Use special calibration layouts
#from calibration import calib_small_apple
#calib_small_apple(track)

# Calibration
track.setup()

try:
    # enumerate all trials:
    # i runs from 0 to number of trials-1
    # t is the trial description from the matlab file
    for i, t in enumerate(trials):
        # announce the trial to the tracker
        track.trial(i, t)
        # for every possible trial type we do:
        # 1 initialize by pre-loading stimulus data
        # 2 run the drift correction
        # 3 execute the actual trial
        T = Trial.Image(disp, track, "images/221.bmp")
        # send SYNC commands to other devices via parallel port on host:
        # track.sendCommand('!write_ioport 0x378 1')
        track.drift()
        T.run(1000)
finally:
    # whatever happens:
    # we shutdown the display
    disp.finish()
    # and save the EDF
    track.finish()
