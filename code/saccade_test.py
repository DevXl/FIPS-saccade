#!usr/bin/env python
"""
Created at 2/6/21
@author: devxl

Testing script for saccade task
"""
from psychopy import visual, gui, data, monitors
from fips import FIPS
from psycphys import *

# ===============
# SETUP
# ===============

# Monitor
mon = make_test_monitor()

# Window
win = visual.Window(
    size=[1024, 768],
    fullscr=False,
    allowGUI=False,
    monitor=mon,
    screen=0,
    units='deg',
    gamma=None,
    name='SaccadeWindow'
)

# Eye-tracker


# Logging

