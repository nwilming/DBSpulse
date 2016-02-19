# Example code for special calibration layouts
#
# Don't read/copy/include/use this when you are fine with the available
# default layouts.
#
# Please: if you add a calibration type useful for other experiments:
# give it a descriptive name, add it to this file and commit to svn!


def calib_small_apple(track):
    """13 point calibration for a subwindow of 1280x1024 on a
    2560x1600 display"""

    # Calibration
    # overwrite tracker config
    track.set_calibration(13)

    # Set custom calibration options
    # layout on screen for 9 points:
    # 5 1 6
    # 3 0 4
    # 7 2 8
    # in 13 point, intermediate points are added between 5/0 0/6 7/0 0/8

    # overwrite tracker targets
    track.sendCommand('generate_default_targets = NO')
    # the pixel coordinates
    # left, middle, right
    l, m, r = 660, 1280, 1900
    # top, center, bottom
    t, c, b = 100, 800, 1500
    # half top, half bottom
    st, sb = 450, 1150
    # half left, half right
    sl, sr = 845, 1715
    # set coordinates for calibration
    # these are x, y pairs
    track.sendCommand('calibration_targets = %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d' % 
        (m,c, m,t, m,b, l,c, r,c, l,t, r,t, l,b, r,b, sl,st, sr,st, sl,sb, sr,sb) )
    # set coordinates for validation
    track.sendCommand('validation_targets = %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d' % 
        (m,c, m,t, m,b, l,c, r,c, l,t, r,t, l,b, r,b, sl,st, sr,st, sl,sb, sr,sb) )


