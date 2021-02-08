#!usr/bin/env python
"""
Created at 1/20/21
@author: devxl

Description
"""
from psychopy import monitors


def make_test_monitor():
    width_pix = 1920
    height_pix = 1080
    width_cm = 35
    view_dist = 57
    mon_name = 'test'
    scrn = 0
    mon = monitors.Monitor(mon_name, width=width_cm, distance=view_dist)
    mon.setSizePix((width_pix, height_pix))

    return mon

