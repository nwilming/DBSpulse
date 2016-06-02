DBS single pulse pupilometry experiment
=======================================

This module contains the glue to detect triggers from a DBS stimulator via EEG,
use a pupil labs eye tracker and to display the data live. Oh, and of course the
actual experiment.

Trigger detection
-----------------

Triggers are detected by filtering an EEG signal placed on the skin over the
leads for the DBS stimulator. The EEG software broadcasts the signal to the
network and it is read and filtered. The bits and pieces that do this are:
  - RDA.py:
      - Read data from EEG and apply trigger detection to last chunk of data
      - Can also generate fake EEG data for testing
    - cncrnt.py:
      - Run this to have the trigger checker continuously running in the background
      - Will broadcast detected triggers to the network, which allows subscribers
        to act on trigger detection.

Eye tracking
------------

Eye-tracking data comes from a pupil labs eye tracker. Pupil capture should be
configured to stream it's data over the network for live display of the data. A
plugin for pupil capture (pupil_trigg_detect.py) can receive detected triggers
and inserts them into the data stream. There is some delay associated with this
(ca. 50ms EEG -> Network + processing and broadcasting). The scripts 'live_*.py'
can display data from eye tracker and detected triggers.


Experiment
----------

The experiment relies on the trigger detection to sync itself to the pulses.


Order of operations
-------------------

 1. Set up DBS stimulation parameters.
 2. Start trigger detection.
 3. Set up Eye tracker (calibration)
 4. Start recording
 5. Start experiment.
