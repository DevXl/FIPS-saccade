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

from .helpers import move_frame, setup_path, get_monitors

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! SETUP ---------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Paths
EXP = "FIPSSaccade"
ROOTDIR = Path(__file__).resolve().parent.parent
sub_id = int(sys.argv[1])
ses = sys.argv[2]
TASKDIR = setup_path(sub_id, ROOTDIR, "itrack")

# Display
mon_name = "oled"
mon_specs = get_monitors(mon_name)
exp_mon = monitors.Monitor(name=mon_name, width=mon_specs["size_cm"][0], distance=mon_specs["dist"])
exp_mon.setSizePix(mon_specs["size_px"])
exp_mon.save()

# Window
disp = libscreen.Display(moniotr=exp_mon)
win = pygaze.expdisplay

# Eye-tracker
tracker = eyetracker.EyeTracker(disp)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! STIMULUS --------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Frame
frame_size = 3
frame_size_px = deg2pix(degrees=frame_size, monitor=exp_mon)
frame_coords = [
    [-frame_size_px/2, frame_size_px/2], [frame_size_px/2, frame_size_px/2],
    [frame_size_px/2, -frame_size_px/2], [-frame_size_px/2, -frame_size_px/2]
]
path_len = 10  # degrees
path_len_px = deg2pix(path_len, monitor=exp_mon)
frame_yshift = 8
frame_start_pos = [-path_len_px/2, deg2pix(frame_yshift, exp_mon)]
frame_stim = visual.ShapeStim(
    win=win,
    pos=frame_start_pos,
    lineWidth=20,
    lineColor=[-1, -1, -1],
    fillColor=None,
    vertices=frame_coords,
    closeShape=True,
    size=frame_size,
    autoLog=False,
    autoDraw=False
)

fix_size = 1
fix_size_px = deg2pix(fix_size, exp_mon)
fix = visual.GratingStim(win=win, mask="cross", size=fix_size_px, sf=0, color=[-1, -1, -1])

probe_size = .8
probe_xshift = deg2pix(2, exp_mon)
probe_yshift = deg2pix(2, exp_mon)
probe_size_px = deg2pix(probe_size, exp_mon)
probe_top_pos = [probe_xshift, frame_stim.pos[1] + probe_yshift]
probe_bot_pos = [-probe_xshift, frame_stim.pos[1] - probe_yshift]
probe_top = visual.Circle(win=win, radius=probe_size_px, fillColor='red', contrast=.6)
probe_bot = visual.Circle(win=win, radius=probe_size_px, fillColor='red', contrast=.6)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! PROCEDURE -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# timing
trial_clock = core.Clock()
block_clock = core.Clock()

# Blocks
conditions = []

motion_cycles = np.array([.7])
motion_cycles_fr = motion_cycles * mon_specs["refresh_rate"]

speeds = path_len / motion_cycles_fr  # deg/fr
speeds_px = path_len_px / motion_cycles_fr  # px/fr

quadrants = [1, 2]
quad_shift = deg2pix(8, exp_mon)

for quad in quadrants:
    for i, speed in enumerate(speeds):
        conditions.append(
            {
                "quadrant": quad,
                "speed": np.round(speed, 2),
                "speed_px": np.round(speeds_px[i], 2),
                "motion_cycle": motion_cycles[i] * 1000
            }
        )

block_handlers = []
# n_blocks = 12
n_blocks = 1
# total_trials = 384
total_trials = 50

for block in range(n_blocks):
    b = data.TrialHandler(
        name=f"Block_N{block}",
        trialList=conditions,
        nReps=total_trials/n_blocks,
        method="fullRandom",
        originPath=-1
        )
    block_handlers.append(b)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! RUN ------------------------------------ #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Runtime parameters
n_stabilize = 5  # number of transitions needed to stabilize the effect
flash_frames = 4  # frames
win.mouseVisible = False

# loop blocks
for block_idx, block in enumerate(block_handlers):

    print(f"============> Block number {block_idx + 1}")

    # calibrate the eye tracker
    tracker.calibrate()

    win.recordFrameIntervals = True
    block_clock.reset()

    for n, trial in enumerate(block):

        # # drift correction
        # drift = True
        # while drift:
        #     fix.draw()
        #     win.flip()
        #     drift = tracker.drift_correction()

        # Trial params
        n_cue = np.random.randint(4, 10)  # between 4 and 9
        delay = np.round(np.random.uniform(400, 600))
        frame_stim.pos = frame_start_pos
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