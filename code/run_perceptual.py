#!usr/bin/env python
"""
Created at 2/22/21
@author: devxl

Perceptual task to get FIPS measurements to use for the saccade task
"""
from psychopy import visual, data, monitors, event, core
from fips_helpers import move_frame, setup_path, get_monitors

import numpy as np
import pandas as pd
import sys
from pathlib import Path

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! SETUP ---------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Get the args from commandline
# First one is subject number and second one is session
sub_id = int(sys.argv[1])
ses = sys.argv[2]
run = sys.argv[3]

# Directories and files
# The structure loosely follows BIDS conventions
EXP = "FIPSPerceptual"
TASK = "psycphys"
ROOTDIR = Path(__file__).resolve().parent.parent  # find the current file and go up too root dir
TASKDIR = setup_path(sub_id, ROOTDIR, TASK)
run_file = TASKDIR / f"sub-{sub_id:02d}_ses-{ses}_run-{run}_task-{TASK}_exp-{EXP}_staircase"
frames_file = str(run_file) + "FrameIntervals.log"
log_file = str(run_file) + "RuntimeLog.log"

# Monitor
mon_name = 'RaZerBlade'
mon_specs = get_monitors(mon_name)
exp_mon = monitors.Monitor(name=mon_name, width=mon_specs["size_cm"][0], distance=mon_specs["dist"])
exp_mon.setSizePix(mon_specs["size_px"])
# exp_mon.save()

# Window
mon_size = [1024, 768]  # for testing
# mon_size = mon_specs["size_px"]
exp_win = visual.Window(monitor=exp_mon, fullscr=False, units='deg', size=mon_size)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! STIMULUS --------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Frame
frame_size = 2.4
frame_coords = [
    [-frame_size/2, frame_size/2], [frame_size/2, frame_size/2],
    [frame_size/2, -frame_size/2], [-frame_size/2, -frame_size/2]
]
frame_stim = visual.ShapeStim(
    win=exp_win,
    lineWidth=10,
    lineColor=-1,
    fillColor=None,
    vertices=frame_coords,
    closeShape=True,
    size=frame_size,
    autoLog=False
    )

# Target
top_probe = visual.Circle(
    win=exp_win,
    lineColor=0,
    contrast=1,
    lineWidth=3,
    autoLog=False
)
bot_probe = visual.Circle(
    win=exp_win,
    lineColor=0,
    contrast=1,
    lineWidth=3,
    autoLog=False
)

# Concentric fixation circles
inner_fix = visual.Circle(win=exp_win, radius=0.1, lineColor='black', autoLog=False)
outer_fix = visual.Circle(win=exp_win, radius=0.25, lineColor='black', autoLog=False)

# Vertical circles to compare the probes' position to
top_match = visual.Circle(
    win=exp_win,
    fillColor=-1,
    lineColor=0,
    contrast=1,
    lineWidth=3,
    autoLog=False
)
bot_match = visual.Circle(
    win=exp_win,
    fillColor=-1,
    lineColor=0,
    contrast=1,
    lineWidth=3,
    autoLog=False
)

# Instructions
msg_stim = visual.TextStim(win=exp_win, wrapWidth=30, height=.8, autoLog=False)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! PROCEDURE -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Instructions
inst_msg = "Compare the position of RED CIRCLES to BLACK CIRCLES.\n\n" \
      "If they MATCH, press the 'M' key on the keyboard.\n\n" \
      "If they are DIFFERENT, press the 'D' key.\n\n" \
      "Press the SPACEBAR to start the experiment."
out_msg = "Thank you for participating!"

# Blocks and trials
n_trials = 50

# QUEST staircase
stairs = data.QuestHandler(
    startVal=.1,
    startValSd=.5,
    pThreshold=.63,
    nTrials=n_trials,
    gamma=.02,
    minVal=-frame_size/2,
    maxVal=frame_size/2
)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! RUN ------------------------------------ #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Initialize parameter

# Stimulus
probe_size = 1.2
probe_color = [.1, -1, -1]
fix_pos = [0, 0]
probe_pos_shift = frame_size - probe_size / 2  # so the distance between them is as tall as the frame
match_pos_size = probe_size / 2
match_pos_shift = probe_pos_shift / 2

top_probe.size = probe_size
top_probe.fillColor = probe_color

bot_probe.size = probe_size
bot_probe.fillColor = probe_color

top_match.size = match_pos_size
top_match.pos = [fix_pos[0], fix_pos[1] + match_pos_shift]

bot_match.size = match_pos_size
bot_match.pos = [fix_pos[0], fix_pos[1] - match_pos_shift]

msg_stim.pos = fix_pos
inner_fix.pos = fix_pos
outer_fix.pos = fix_pos

# Runtime
frame_sides = ['L', 'R']  # 1st and 2nd quadrants
frame_pos_shift = 5  # how many degrees in both x and y the initial position of frame shifts from fixation

motion_cycle_dur = 1000  # seconds
motion_cycle = int(motion_cycle_dur * mon_specs["refresh_rate"]/1000)  # in frames

motion_len = 8  # length of the path that the frame moves in degrees
frame_speed = motion_len / motion_cycle  # deg/f

n_stabilize = 4  # number of transitions needed to stabilize the effect

flash_frames = 5  # number of frames to show the probe

# clock it
exp_clock = core.Clock()
t_start = exp_clock.getTime()

# show instruction message
msg_stim.text = inst_msg
msg_stim.draw()
exp_win.flip()
event.waitKeys(keyList=['space'])

# start the staircase
for offset in stairs:

    print(f"Offset: {np.round(offset, 2)}")

    # select a random side
    side = np.random.choice(frame_sides)
    stairs.addOtherData("side", side)

    # set the positions of frame and probes based on side and offset
    if side == 'L':
        fpos = [-frame_pos_shift, frame_pos_shift]  # frame is at the first quadrant
        tpos = [-frame_pos_shift - offset, frame_pos_shift + probe_pos_shift] # offset on x coords and shift on y
        bpos = [-frame_pos_shift + offset, frame_pos_shift - probe_pos_shift]
    else:
        fpos = [frame_pos_shift, frame_pos_shift]  # frame is at the first quadrant
        tpos = [frame_pos_shift - offset, frame_pos_shift + probe_pos_shift]  # offset on x coords and shift on y
        bpos = [frame_pos_shift + offset, frame_pos_shift - probe_pos_shift]

    # set the positions
    frame_stim.pos = fpos
    top_probe.pos = tpos
    bot_probe.pos = bpos

    core.wait(.2)  # 200ms delay between trials

    # draw fixation and frame
    inner_fix.autoDraw = True
    outer_fix.autoDraw = True
    frame_stim.autoDraw = True
    # turn off the comparison circles if they were being drawn before
    top_match.autoDraw = False
    bot_match.autoDraw = False

    # start recording frame intervals
    exp_win.recordFrameIntervals = True

    # Stabilization period: here the comparison stimuli are not present and the subject cannot make a response
    for stab in range(n_stabilize):
        frame_stim.pos = fpos
        move_frame([top_probe, bot_probe], frame_stim, motion_cycle, frame_speed, flash_frames, exp_win)

    # Discrimination period: now show the match stimuli and wait for an answer
    resp = False
    event.clearEvents()
    while not resp:

        # show the comparison circles
        top_match.autoDraw = True
        bot_match.autoDraw = True

        # show motion
        frame_stim.pos = fpos
        move_frame([top_probe, bot_probe], frame_stim, motion_cycle, frame_speed, flash_frames, exp_win)

        # get response
        keys = event.getKeys()
        for key in keys:
            if key == 'd':  # a different response is a "missed" trial
                stairs.addResponse(1)
                resp = True
            elif key == 'm':  # a match response is a "detected" trial
                stairs.addResponse(0)
                resp = True
            elif key == 'escape':
                exp_win.close()
                core.quit()

    event.clearEvents()

exp_win.flip()
core.wait(1)
msg_stim.text = out_msg
msg_stim.draw()
exp_win.flip()
core.wait(1)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! WRAP UP -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# clock it
t_end = exp_clock.getTime()
print(f"The experiment took {np.round((t_end - t_start)/60, 2)}m and {np.round((t_end - t_start)%60), 0} seconds")

# save to csv
exp_data = {
    "side": stairs.otherData["side"],
    "intensity": stairs.intensities,
    "resp": stairs.data
}
df = pd.DataFrame(exp_data)
df.to_csv(str(run_file) + ".csv", index=False)

# save to pickle
stairs.saveAsPickle(str(run_file))

# save numpy
np_data = np.array([stairs.intensities, stairs.data]).T  # first column is intensities and second column is responses
np.save(str(run_file) + ".npy", np_data)

# end
exp_win.close()
core.quit()
