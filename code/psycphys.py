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


def detect_fixation(tracker, region):
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

    for _ in range(10):

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


def make_motion_seq(path_dur, flash_dur, n_repeat, total_cycle):
    """
    Makes a sequence of indexes for different stages of the frame motion

    Parameters
    ----------
    path_dur
    flash_dur
    n_repeat

    Returns
    -------

    """

    # sections
    move_right_frames = [i for i in range(path_dur)]
    flash_right_frames = [i for i in range(path_dur, path_dur + flash_dur)]
    move_left_frames = [i for i in range(flash_right_frames[-1] + 1, flash_right_frames[-1] + path_dur)]
    flash_left_frames = [i for i in range(move_left_frames[-1] + 1, move_right_frames[-1] + flash_dur)]

    def get_all_frames(frames):
        return [fr + (tr * total_cycle) for fr in frames for tr in range(n_repeat)]

    all_right_frames = get_all_frames(move_right_frames)
    all_left_frames = get_all_frames(move_left_frames)
    all_flash_frames = get_all_frames((flash_left_frames + flash_right_frames))

    motion_seq = {"right": all_right_frames, "left": all_left_frames, "flash": all_flash_frames}

    return motion_seq

