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


def check_fixation(tracker, region, n_frames):
    """
    Checks whether the subject is fixating on a region of the screen or not
    Parameters
    ----------
    tracker
    region
    n_frames

    Returns
    -------

    """
    fixate = False
    msg = ""

    for frame in n_frames:

        # get eye position
        gaze_pos = tracker.getLastGazePosition()

        # check if it's valid
        valid_gaze_pos = isinstance(gaze_pos, (tuple, list))

        # run the procedure while fixating
        if valid_gaze_pos:
            if region.contains(gaze_pos):
                fixate = True
            else:
                msg = "Please fixate"
        else:
            msg = "Run calibration procedure."

    return fixate, msg
