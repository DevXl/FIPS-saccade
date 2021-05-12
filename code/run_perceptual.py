#!usr/bin/env python
"""
Created at 2/22/21
@author: devxl

Perceptual task to get FIPS measurements to use for the saccade task
"""
from psychopy import visual, data, monitors, event, core
import numpy as np
import sys
from pathlib import Path
from helpers import move_frame

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! SETUP ---------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Get the args from commandline
# First one is subject number and second one is session
sub_id = int(sys.argv[1])
ses = sys.argv[2]

# Directories and files
# The structure loosely follows BIDS conventions
ROOTDIR = Path(__file__).resolve().parent.parent  # find the current file and go up too root dir
DATADIR = ROOTDIR / "data"
if not DATADIR.exists():
    print("Making the data directory...")
    DATADIR.mkdir()

sub_id = f"{sub_id:02d}"
SUBDIR = DATADIR / f"sub-{sub_id}"
if not SUBDIR.exists():
    print("Making the subject directory...")
    SUBDIR.mkdir()

TASK = "FIPSPerceptual"
run = 1
run_file = DATADIR / "psycphy" / f"sub-{sub_id}_ses-{ses}_run-{run}_task-{TASK}_psychophysics"

# Monitor
test_monitors = {
    "lab": {
        "size_cm": (54, 0),
        "size_px": (1280, 720),
        "dist": 57,
        "refresh_rate": 120
    },
    "razerblade": {
        "size_cm": (38, 20),
        "size_px": (2560, 1440),
        "dist": 60,
        "refresh_rate": 165
    },
    "ryan": {
        "size_cm": (0, 0),
        "size_px": (0, 0),
        "dist": 60,
        "refresh_rate": 60
    }
}

mon_name = 'lab'
exp_mon = monitors.Monitor(name=mon_name, width=test_monitors[mon_name]["size_cm"][0], distance=test_monitors["dist"])
exp_mon.setSizePix(test_monitors[mon_name]["size_px"])
exp_mon.save()

# Window
mon_size = [1024, 768]  # for testing
# mon_size = test_monitors[mon_name]["size_px"]
exp_win = visual.Window(monitor=exp_mon, fullscr=False, units='deg', size=mon_size)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! STIMULUS --------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Frame
frame_size = 3
frame_coords = [
    [-frame_size/2, frame_size/2], [frame_size/2, frame_size/2],
    [frame_size/2, -frame_size/2], [-frame_size/2, -frame_size/2]
]
frame_pos = [0, 0]
frame_stim = visual.ShapeStim(
    win=exp_win,
    lineWidth=5,
    lineColor=[-1, -1, -1],
    fillColor=None,
    vertices=frame_coords,
    closeShape=True,
    size=frame_size,
    autoLog=False,
    autoDraw=False
)

# Target
probe_margin = -1
probe_size = .9
probe_color = .1
top_probe = visual.Circle(
    win=exp_win,
    size=probe_size,
    fillColor=1,
    lineColor=0,
    contrast=1,
    lineWidth=3,
    autoLog=False
)
bot_probe = visual.Circle(
    win=exp_win,
    size=probe_size,
    fillColor=1,
    lineColor=0,
    contrast=1,
    lineWidth=3,
    autoLog=False
)


# Concentric fixation circles
fix_pos = [0, 0]
inner_fix = visual.Circle(win=exp_win, radius=0.1, pos=fix_pos, lineColor='black', autoLog=False)
outer_fix = visual.Circle(win=exp_win, radius=0.25, pos=fix_pos, lineColor='black', autoLog=False)

# Vertical circles to compare the probes' position to
match_pos_shift = frame_size/2  # so the distance between them is as tall as the frame
top_match = visual.Circle(
    win=exp_win,
    size=probe_size,
    pos=[fix_pos[0], fix_pos[1] + match_pos_shift],
    fillColor=-1,
    lineColor=0,
    contrast=1,
    lineWidth=3,
    autoLog=False
)
bot_match = visual.Circle(
    win=exp_win,
    size=probe_size,
    pos=[fix_pos[0], fix_pos[1] - match_pos_shift],
    fillColor=-1,
    lineColor=0,
    contrast=1,
    lineWidth=3,
    autoLog=False
)

# Instructions
inst_stim = visual.TextStim(win=exp_win, pos=fix_pos, autoLog=False)
inst_msg = "Compare the position of WHITE CIRCLES to BLACK CIRCLES.\n\n" \
      "If they are MATCH, press the 'M' key on the keyboard.\n\n" \
      "If they are DIFFERENT, press the 'D' key.\n\n" \
      "Press the SPACEBAR to start the experiment."
out_stim = visual.TextStim(win=exp_win, pos=fix_pos, autoLog=False)
out_msg = "Thank you for participating!"

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! PROCEDURE -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Conditions
frame_sides = ['L', 'R']
n_trials = 10

# QUEST staircase
stairs = data.QuestHandler(
    startVal=1,
    startValSd=.5,
    pThreshold=.82,
    nTrials=n_trials,
    gamma=.01,
    minVal=0,
    maxVal=frame_size/2
)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! RUN ------------------------------------ #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Initialize run params
motion_cycle_dur = 700  # ms
motion_cycle = int(motion_cycle_dur * test_monitors[mon_name]["refresh_rate"]/1000)  # in frames
motion_len = 10  # length of the path that the frame moves in degrees
frame_speed = motion_len / motion_cycle  # deg/f
n_stabilize = 2  # number of transitions needed to stabilize the effect
flash_frames = 4  # number of frames to show the probe
frame_pos_shift = 8  # how many degrees in both x and y the initial position of frame shifts from fixation

# clock it
exp_clock = core.Clock()
t_start = exp_clock.getTime()

# start the staircase
for offset in stairs:

    # randomly select which side the frame will appear at
    side = np.random.choice(frame_sides)

    # set the positions of frame and probes based on side and offset
    if side == 'L':
        fpos = [-frame_pos_shift, frame_pos_shift]  # frame is at the first quadrant
        tpos = [-frame_pos_shift - offset, frame_pos_shift + match_pos_shift]  # offset on x coords and shift on y
        bpos = [-frame_pos_shift + offset, frame_pos_shift - match_pos_shift]
    else:
        fpos = [frame_pos_shift, frame_pos_shift]  # frame is at the first quadrant
        tpos = [frame_pos_shift - offset, frame_pos_shift + match_pos_shift]  # offset on x coords and shift on y
        bpos = [frame_pos_shift + offset, frame_pos_shift - match_pos_shift]

    # set the positions
    frame_stim.pos = fpos
    top_probe.pos = tpos
    bot_probe.pos = bpos

    core.wait(.2)  # 200ms delay between trials

    # draw fixation and frame
    inner_fix.autoDraw = True
    outer_fix.autoDraw = True
    frame_stim.autoDraw = True

    # start recording frame intervals
    exp_win.recordFrameIntervals = True

    # Stabilization period: here the comparison stimuli are not present and the subject cannot make a response
    for stab in range(n_stabilize):
        move_frame([top_probe, bot_probe], frame_stim, motion_cycle, frame_speed, flash_frames, exp_win)

    # Discrimination period: now show the match stimuli and wait for an answer
    resp = False
    while not resp:

        # show the comparison circles
        top_match.autoDraw = True
        bot_match.autoDraw = True

        # show motion
        move_frame([top_probe, bot_probe], frame_stim, motion_cycle, frame_speed, flash_frames, exp_win)

        # get response
        keys = event.getKeys()
        for key in keys:
            if key == 'd':  # a different response is a "missed" trial
                stairs.addResponse(0)
                resp = True
            elif key == 'M':  # a match response is a "detected" trial
                stairs.addResponse(1)
                resp = True

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! WRAP UP -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# clock it
t_end = exp_clock.getTime()
print(f"The experiment took {np.round((t_end - t_start), 2)}s")

# save
stairs.saveAsText(run_file, delim=',')

# end
exp_win.close()
core.quit()
