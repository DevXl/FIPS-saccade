#!usr/bin/env python
"""
Created at 2/6/21
@author: devxl

FIPS saccade task
"""
from psychopy import visual, gui, data, monitors
from fips import FIPS
from psycphys import *

# ===============
# SETUP
# ===============

# Monitor
width_pix = 1920
height_pix = 1080
width_cm = 35
view_dist = 57
mon_name = 'asus'
scrn = 0
exp_mon = monitors.Monitor(mon_name, width=width_cm, distance=view_dist)
exp_mon.setSizePix((width_pix, height_pix))
exp_mon.save()

