#!usr/bin/env python
"""
Created at 2/6/21
@author: DevXI

Testing script for saccade task
"""
from pathlib import Path
import sys
import numpy as np

from psychopy import visual, data, monitors, core, logging, info, event
from psychopy.tools.monitorunittools import deg2pix, pix2deg
from pygaze import eyetracker, libscreen
import pygaze

from fips_helpers import move_frame, setup_path, get_monitors

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
EXP = "FIPSSaccade"
TASK = "iTrack"
ROOTDIR = Path(__file__).resolve().parent.parent  # find the current file and go up too root dir
TASKDIR = setup_path(sub_id, ROOTDIR, TASK)
run_file = TASKDIR / f"sub-{sub_id:02d}_ses-{ses}_run-{run}_task-{TASK}_exp-{EXP}"
frames_file = str(run_file) + "FrameIntervals.log"
log_file = str(run_file) + "RuntimeLog.log"

# Display
mon_name = "lab"
mon_specs = get_monitors(mon_name)
exp_mon = monitors.Monitor(name=mon_name, width=mon_specs["size_cm"][0], distance=mon_specs["dist"])
exp_mon.setSizePix(mon_specs["size_px"])
exp_mon.save()

# Window
disp = libscreen.Display(moniotr=exp_mon)
exp_win = pygaze.expdisplay

# Eye-tracker
tracker = eyetracker.EyeTracker(disp)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! STIMULUS --------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Frame
frame_size = 2.4
frame_size_px = deg2pix(degrees=frame_size, monitor=exp_mon)
frame_coords = [
    [-frame_size_px/2, frame_size_px/2], [frame_size_px/2, frame_size_px/2],
    [frame_size_px/2, -frame_size_px/2], [-frame_size_px/2, -frame_size_px/2]
]
frame_stim = visual.ShapeStim(
    win=exp_win,
    lineWidth=deg2pix(10, exp_mon),
    lineColor=-1,
    fillColor=None,
    vertices=frame_coords,
    closeShape=True,
    size=frame_size,
    autoLog=False,
    autoDraw=False
)

# Target
top_probe = visual.Circle(
    win=exp_win,
    lineColor=-1,
    lineWidth=deg2pix(5, exp_mon),
    autoLog=False
)
bot_probe = visual.Circle(
    win=exp_win,
    lineColor=-1,
    lineWidth=deg2pix(5, exp_mon),
    autoLog=False
)

# Concentric fixation circles
inner_fix = visual.Circle(win=exp_win, radius=deg2pix(.1, exp_mon), lineColor=-1, autoLog=False)
outer_fix = visual.Circle(win=exp_win, radius=deg2pix(0.25, exp_mon), lineColor=-1, autoLog=False)

# Text message
msg_stim = visual.TextStim(win=exp_win, wrapWidth=deg2pix(30, exp_mon), height=deg2pix(.8, exp_mon), autoLog=False)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! PROCEDURE -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Instructions
inst_msg = "Maintain fixation during each trial.\n\n" \
      "Wait for a \033[94mBLUE target to flash on the screen.\n\n" \
      "Make a saccade to where you saw the \033[94mBLUE target.\n\n" \
      "Do it all over again.\n\n" \
      "Press the spacebar to start the experiment..."
end_msg = "Thank you for participating!"


# Conditions
frame_stay = ['on', 'off']  # whether the frame stays on the screen during the flash
flash_durs = [2, 4, 6, 8, 10]  # duration of probes flashing

n_blocks = 4
n_trials_per_cond = 12
n_trials = n_trials_per_cond * (len(frame_stay) * len(flash_durs))  # total number of trials in a block
total_trials = n_trials * n_blocks  # number of all trials in one experiment session

# Data handler
# columns of experiment dataframe
cols = [
    "trial_type", "stay_status", "flash_dur", "stim_side", "block", "trial", "success",
    "target_x", "target_y", "sacc_start_x", "sacc_start_y", "sacc_end_x", "sacc_end_y",
    "sacc_dur", "sacc_delay", "target_ud", "n_cue", "sub", "ses", "run", "task", "exp"
]

# loop through conditions, make every permutation, and save it to a numpy array
rows = None
for st in frame_stay:
    for dur in flash_durs:
        row = np.array([
            np.NaN, st, dur, np.NaN, np.NaN, np.NaN, np.NaN,
            np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
            np.NaN, np.NaN, np.NaN, np.NaN, sub_id, ses, run, TASK, EXP
            ])
        if rows is None:
            rows = row
        else:
            rows = np.vstack((rows, row))

# blocks and trials
blocks = None
for b in range(1, n_blocks + 1):

    # repeat conditions for however many trials
    block = np.repeat(rows, n_trials_per_cond, axis=0)

    # shuffle them
    np.random.shuffle(block)  # this preserves the order within row and just shuffles the rows

    # sanity check
    assert block.shape == (len(frame_stay) * len(flash_durs) * n_trials_per_cond, len(cols))

    # add the block and trial labels
    block[:, 4] = b
    block[:, 5] = np.arange(1, n_trials + 1)  # set trials to a list of ordered numbers

    if blocks is None:
        blocks = block
    else:
        blocks = np.vstack((blocks, block))

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! RUN ------------------------------------ #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Initialize parameter

# Stimulus
probe_size = 1.2
probe_size_px = deg2pix(probe_size, exp_mon)
probe_color = .1
probe_pos_shift = frame_size_px - probe_size_px / 2  # so the distance between them is as tall as the frame

frame_pos_shift = deg2pix(5, exp_mon)  # how many degrees in both x and y the initial position of frame shifts from fixation

fix_pos = [0, 0]

top_probe.size = probe_size_px
top_probe.fillColor = [probe_color, -1, -1]

bot_probe.size = probe_size_px
bot_probe.fillColor = [probe_color, -1, -1]

msg_stim.pos = fix_pos
inner_fix.pos = fix_pos
outer_fix.pos = fix_pos

# Runtime
sides = ['L', 'R']  # 1st and 2nd quadrants

motion_cycle_dur = 1000  # seconds
motion_cycle = int(motion_cycle_dur * mon_specs["refresh_rate"]/1000)  # in frames

motion_len = 8  # length of the path that the frame moves in degrees
motion_len_px = deg2pix(motion_len, monitor=exp_mon)  # in pixels
frame_speed = motion_len_px / motion_cycle  # pixel/frame

n_stabilize = 4  # number of transitions needed to stabilize the effect

# Run
# clock it
block_clock = core.Clock()
exp_clock = core.Clock()
t_start = exp_clock.getTime()
block_dur = 0  # just initializing

# show instruction message
msg_stim.text = inst_msg
msg_stim.draw()
exp_win.flip()
event.waitKeys(keyList=['space'])
exp_win.mouseVisible = False

# loop blocks
for block in range(n_blocks):

    print(f"============> Block number {block + 1}")

    # time it
    ts_block = block_clock.getTime()

    # text message
    remain_blocks = n_blocks - block
    if block:  # no need to show it on the first block
        btw_blocks_msg = f"You finished block number {block}.\n\n" \
                         f"{remain_blocks} more block(s) (~{block_dur * remain_blocks} mins) to go!\n\n" \
                         "When you are ready, press the SPACEBAR to continue..."
        msg_stim.text = btw_blocks_msg
        msg_stim.draw()
        exp_win.flip()
        event.waitKeys(keyList=['space'])

    # calibrate the eye tracker
    tracker.calibrate()

    exp_win.recordFrameIntervals = True
    block_clock.reset()

    for trial in range(n_trials):

        # # drift correction
        # drift = True
        # while drift:
        #     fix.draw()
        #     win.flip()
        #     drift = tracker.drift_correction()

        # get trial index
        trial_row = (block * n_trials) + trial

        # set trial conditions
        frame_side = np.random.choice(sides)
        if frame_side == "L":
            fpos = [-frame_pos_shift, frame_pos_shift]  # frame is at the first quadrant
            tpos = [-frame_pos_shift - offset, frame_pos_shift + probe_pos_shift] # offset on x coords and shift on y
            bpos = [-frame_pos_shift + offset, frame_pos_shift - probe_pos_shift]
        else:
            fpos = [frame_pos_shift, frame_pos_shift]  # frame is at the first quadrant
            tpos = [frame_pos_shift - offset, frame_pos_shift + probe_pos_shift]  # offset on x coords and shift on y
            bpos = [frame_pos_shift + offset, frame_pos_shift - probe_pos_shift]

        block[trial_row, 3] = frame_side

        n_cue = np.random.randint(4, 10)  # between 4 and 9
        delay = np.round(np.random.uniform(400, 600))

        probe_top.pos = probe_top_pos
        probe_bot.pos = probe_bot_pos
        catch = np.random.random() < .1  # 10% catch trials
        
        if trial["quadrant"] == 1:
            frame_stim.pos -= [quad_shift, 0]
            probe_top.pos -= [quad_shift, 0]
            probe_bot.pos -= [quad_shift, 0]
        else:
            frame_stim.pos += [quad_shift, 0]
            probe_top.pos += [quad_shift, 0]
            probe_bot.pos += [quad_shift, 0]

        # start eye tracking
        tracker.start_recording()
        tracker.status_msg(f"trial {n}")
        tracker.log("start_trial {} quadrant {}".format(n, trial["quadrant"]))

        # fixation period
        fix.autoDraw = True
        core.wait(delay/1000)

        move_frames = (trial["motion_cycle"]/1000) * mon_specs["refresh_rate"]

        # move frame for stabilization period
        for s in range(n_stabilize):
            for fr in range(int(move_frames)):
                frame_stim.pos += [trial["speed_px"], 0]
                if not catch:
                    frame_stim.draw() 
                win.flip()
            for fr in range(flash_frames):
                probe_top.draw()
                win.flip()
            for fr in range(int(move_frames)):
                frame_stim.pos -= [trial["speed_px"], 0]
                if not catch:
                    frame_stim.draw()
                win.flip()
            for fr in range(flash_frames):
                probe_bot.draw()
                win.flip()

        # pre-cue motion and cue
        for c in range(n_cue):
            if not c % 2:  # even
                if c == n_cue - 1:
                    target = "top"
                    probe_top.color = 'blue'
                for fr in range(int(move_frames)):
                    frame_stim.pos += [trial["speed_px"], 0]
                    if not catch:
                        frame_stim.draw()
                    win.flip()
                for fr in range(int(flash_frames)):
                    probe_top.draw()
                    win.flip()
            else:  # odd
                if c == n_cue - 1:
                    probe_bot.color = 'blue'
                    target = "bot"
                for fr in range(int(move_frames)):
                    frame_stim.pos -= [trial["speed_px"], 0]
                    if not catch:
                        frame_stim.draw()
                    win.flip()
                for fr in range(int(flash_frames)):
                    probe_bot.draw()
                    win.flip()
            
            win.flip()
            probe_top.color = 'red'
            probe_bot.color = 'red'
            
        # wait for saccade
        t1, startpos = tracker.wait_for_fixation_end()
        core.wait(.5)
        t2, endpos = tracker.wait_for_fixation_start()

        # stop tracking
        tracker.stop_recording()

        # save the data
        block.data.add("n_cue", n_cue)
        block.data.add("saccade_delay", delay)  
        block.data.add("sub", sub_id)
        block.data.add("ses", ses)
        block.data.add("run", block_idx)
        block.data.add("target", target)
        if catch:
            block.data.add("trial_type", "catch")
        else:
            block.data.add("trial_type", "test")
        block.data.add("saccade_dur", np.round(t2 - t1, 2))

        # pixels
        if target == "top":
            block.data.add("target_pos_x", np.round((probe_top.pos[0]), 2))
            block.data.add("target_pos_y", np.round((probe_top.pos[1]), 2))
        else:
            block.data.add("target_pos_x", np.round((probe_bot.pos[0]), 2))
            block.data.add("target_pos_y", np.round((probe_bot.pos[1]), 2))
        w = mon_specs["size_px"][0]/2
        h = mon_specs["size_px"][1]/2
        block.data.add("saccade_spos_x", np.round(startpos[0] - w, 2))
        block.data.add("saccade_spos_y", np.round(startpos[1] - h, 2))
        block.data.add("saccade_epos_x", np.round(endpos[0] - w, 2))
        block.data.add("saccade_epos_y", np.round(endpos[1] - h, 2))

        # degrees
        if target == "top":
            block.data.add("target_pos_x_deg", np.round(pix2deg(probe_top.pos[0], exp_mon), 2))
            block.data.add("target_pos_y_deg", np.round(pix2deg(probe_top.pos[1], exp_mon), 2))
        else:
            block.data.add("target_pos_x_deg", np.round(pix2deg(probe_bot.pos[0], exp_mon), 2))
            block.data.add("target_pos_y_deg", np.round(pix2deg(probe_bot.pos[1], exp_mon), 2))
        sac_spos_x_deg = np.round(pix2deg((startpos[0] - w), exp_mon), 2)
        sac_spos_y_deg = np.round(pix2deg((startpos[1] - h), exp_mon), 2)
        sac_epos_x_deg = np.round(pix2deg((endpos[0] - w), exp_mon), 2)
        sac_epos_y_deg = np.round(pix2deg((endpos[1] - h), exp_mon), 2)
        block.data.add("saccade_spos_x_deg", np.round(sac_spos_x_deg, 2))
        block.data.add("saccade_spos_y_deg", np.round(-sac_spos_y_deg, 2))  # pixel coordinates are inverted
        block.data.add("saccade_epos_x_deg", np.round(sac_epos_x_deg, 2))
        block.data.add("saccade_epos_y_deg", np.round(-sac_epos_y_deg, 2))  # pixel coordinates are inverted

    win.recordFrameIntervals = False

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! WRAP UP -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

for block, handler in enumerate(block_handlers):
    run_file = TASKDIR / f"sub-{sub_id}_ses-{ses}_run-{block+1}_task-{EXP}_eyetracki ng"
    handler.saveAsWideText(fileName=str(run_file), delim=',')

tracker.close()
win.close()
core.quit()