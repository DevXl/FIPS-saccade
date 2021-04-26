#!usr/bin/env python
"""
Created at 2/6/21
@author: devxl

Testing script for saccade task
"""
from pathlib import Path
import sys
import numpy as np

from psychopy import visual, data, monitors, core, logging, info, event
from psychopy.tools.monitorunittools import deg2pix
from pygaze import eyetracker, libscreen
import pygaze

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! SETUP ---------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Paths
TASK = "FIPSSaccade"
PATH = Path('.').resolve() 
sub_id = int(sys.argv[1])
ses = int(sys.argv[2])

# Directories
DATA_DIR = PATH.parent / "data" / f"sub-{sub_id:02d}"
if not DATA_DIR.exists():
    DATA_DIR.mkdir()

# Display
my_monitors = {
    "oled": {
        "size_cm": (73, 33),
        "size_px": (1920, 1080)
    },
    "razer": {
        "size_cm": (39, 20),
        "size_px": [2560, 1440]
    }
}
# mon_name = "oled"
mon_name = "razer"
refresh_rate = 60
mon = monitors.Monitor(name=mon_name, width=my_monitors[mon_name]["size_cm"][0], distance=20)
mon.setSizePix(my_monitors[mon_name]["size_px"])
mon.save()

# Window
disp = libscreen.Display(moniotr=mon)
win = pygaze.expdisplay

# Eye-tracker
tracker = eyetracker.EyeTracker(disp)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! STIMULUS --------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Frame
frame_size = 3.2
frame_size_px = deg2pix(degrees=frame_size, monitor=mon)
frame_coords = [
    [-frame_size_px/2, frame_size_px/2], [frame_size_px/2, frame_size_px/2],
    [frame_size_px/2, -frame_size_px/2], [-frame_size_px/2, -frame_size_px/2]
]
path_len = 10  # degrees
path_len_px = deg2pix(path_len, monitor=mon)
frame_yshift = 10
frame_start_pos = [-path_len_px/2, deg2pix(frame_yshift, mon)]
frame_stim = visual.ShapeStim(
    win=win,
    pos=frame_start_pos,
    lineWidth=8,
    lineColor=[-1, -1, -1],
    fillColor=None,
    vertices=frame_coords,
    closeShape=True,
    size=frame_size,
    autoLog=False,
    autoDraw=False
)

fix_size = 1
fix_size_px = deg2pix(fix_size, mon)
fix = visual.GratingStim(win=win, mask="cross", size=fix_size_px, sf=0, color=[-1, -1, -1])

probe_size = 1
probe_xshift = deg2pix(1.5, mon)
probe_yshift = deg2pix(1.5, mon)
probe_size_px = deg2pix(probe_size, mon)
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

motion_cycles = np.array([.2])
motion_cycles_fr = motion_cycles * refresh_rate

speeds = path_len / motion_cycles_fr  # deg/fr
speeds_px = path_len_px / motion_cycles_fr  # px/fr

quadrants = [1, 2]
quad_shift = deg2pix(11, mon)

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
total_trials = 1

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
flash_frames = 5  # frames
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
            frame_stim.pos[0] -= quad_shift
            probe_top.pos[0] -= quad_shift
            probe_bot.pos[0] -= quad_shift
        else:
            frame_stim.pos[0] += quad_shift
            probe_top.pos[0] += quad_shift
            probe_bot.pos[0] += quad_shift

        # start eye tracking
        tracker.start_recording()
        tracker.status_msg(f"trial {n}")
        tracker.log("start_trial {} quadrant {}".format(n, trial["quadrant"]))

        # fixation period
        fix.autoDraw = True
        core.wait(delay/1000)

        move_frames = (trial["motion_cycle"]/1000) * refresh_rate

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
        t2, endpos = tracker.wait_for_fixation_start()

        # stop tracking
        tracker.stop_recording()

        # save the data
        block.data.add("n_cue", n_cue)
        block.data.add("saccade_delay", delay)  
        block.data.add("sub", sub_id)
        block.data.add("ses", ses)
        block.data.add("run", block_idx)
        if target == "top":
            block.data.add("target_pos_x", np.round((my_monitors[mon_name]["size_px"][0]/2 + probe_top.pos[0]), 2))
            block.data.add("target_pos_y", np.round((my_monitors[mon_name]["size_px"][1]/2 - probe_top.pos[1]), 2))
        else:
            block.data.add("target_pos_x", np.round((my_monitors[mon_name]["size_px"][0]/2 + probe_bot.pos[0]), 2))
            block.data.add("target_pos_y", np.round((my_monitors[mon_name]["size_px"][1]/2 - probe_bot.pos[1]), 2))
        block.data.add("saccade_spos_x", np.round(startpos[0], 2))
        block.data.add("saccade_spos_y", np.round(startpos[1], 2))
        block.data.add("saccade_epos_x", np.round(endpos[0], 2))
        block.data.add("saccade_epos_y", np.round(endpos[1], 2))
        block.data.add("saccade_dur", np.round(t2 - t1, 2))
    win.recordFrameIntervals = False

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! WRAP UP -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

for block, handler in enumerate(block_handlers):
    run_file = DATA_DIR / f"sub-{sub_id}_ses-{ses}_run-{block+1}_task-{TASK}_eyetracking"
    handler.saveAsWideText(fileName=str(run_file), delim=',')

tracker.close()
win.close()
core.quit()
