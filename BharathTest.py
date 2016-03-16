# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 14:57:57 2016

@author: eeg-lab
"""

from psychopy import visual, core  # import some libraries from PsychoPy

#create a window
mywin = visual.Window([800,600], monitor="Bharath", units="deg")

#create some stimuli
grating = visual.GratingStim(win=mywin, mask="circle", size=3, pos=[-4,0], sf=3)
fixation = visual.GratingStim(win=mywin, size=0.5, pos=[0,0], sf=0, rgb=-1)

#draw the stimuli and update the window
grating.draw()
fixation.draw()
mywin.update()

#pause, so you get a chance to see it!
core.wait(5.0)