'''
(*)~----------------------------------------------------------------------------------
 Pupil - eye tracking platform
 Copyright (C) 2012-2015  Pupil Labs

 Distributed under the terms of the CC BY-NC-SA License.
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
'''

import cv2
import numpy as np
from pyglui import ui
from pyglui.cygl.utils import draw_polyline,draw_points,RGBA,draw_gl_texture
from gl_utils import basic_gl_setup,adjust_gl_view,clear_gl_screen,make_coord_system_pixel_based,make_coord_system_norm_based
from glfw import *

from plugin import Plugin
#logging
import logging
logger = logging.getLogger(__name__)

import zmq



class DBSTriggers(Plugin):
    """
    Insert DBS triggers into data stream.

    """
    def __init__(self,g_pool,my_persistent_var=10.0, ):
        super(DBSTriggers, self).__init__(g_pool)
        # order (0-1) determines if your plugin should run before other plugins or after
        self.order = .2

        # all markers that are detected in the most recent frame
        self.my_var = my_persistent_var

        self.window = None
        self.menu = None
        self.img = None

        self.animation_state = 0
        self.events = {}
        context = zmq.Context()
        self.et = context.socket(zmq.SUB)
        self.et.connect("tcp://localhost:5559")
        self.et.setsockopt_string(zmq.SUBSCRIBE, u'Trigger')



    def init_gui(self):

        #lets make a menu entry in the sidebar
        self.menu = ui.Growing_Menu('DBSTriggers')
        self.g_pool.sidebar.append(self.menu)
        #and a slider
        #add a button to close the plugin
        self.menu.append(ui.Button('close DBSTriggers',self.close))


    def deinit_gui(self):
        if self.menu:
            self.g_pool.sidebar.remove(self.menu)
            self.menu= None


    def close(self):
        self.alive = False

    def update(self,frame,events):
        try:
            line = self.et.recv_string(zmq.DONTWAIT)
            print line
        except zmq.error.Again:
            return
        if line.startswith('Trigger'):
            time = float(line.split(' ')[1])
            events['DBSTrigger'] = [self.g_pool.capture.get_timestamp()]


    def cleanup(self):
        """ called when the plugin gets terminated.
        This happens either voluntarily or forced.
        if you have a GUI or glfw window destroy it here.
        """
        self.deinit_gui()