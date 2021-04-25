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

# ============================================================
#                          SETUP
# ============================================================

# Experiment 
# names 
NAME = "FIPSSaccade"
TASK = "saccade"
PATH = Path('.').resolve() 
sub_id = int(sys.argv[1])
ses = sys.argv[2]

# directories
DATA_DIR = PATH.parent / "data" / "eye"
LOG_DIR = PATH.parent / "data" / "log"
sub_id = f"{sub_id:02d}"

# Display
my_monitors = {
    "oled": {
        "size_cm": (73, 33),
        "size_px": (1920, 1080)
    },
    "razer": {
        "size_cm": (38, 20),
        "size_px": (2560, 1440)
    }
}
# mon_name = "oled"
mon_name = "razer"
refresh_rate = 60
mon = monitors.Monitor(name=mon_name, width=my_monitors[mon_name]["size_cm"][0], distance=60)
mon.setSizePix(my_monitors[mon_name]["size_px"])
mon.save()

# Window
disp = libscreen.Display(moniotr=mon)
win = pygaze.expdisplay

# Eye-tracker
tracker = eyetracker.EyeTracker(disp)

# ============================================================
#                          Stimulus
# ============================================================
frame_size = 3
frame_size_px = deg2pix(degrees=frame_size, monitor=mon)
frame_coords = [
    [-frame_size_px/2, frame_size_px/2], [frame_size_px/2, frame_size_px/2],
    [frame_size_px/2, -frame_size_px/2], [-frame_size_px/2, -frame_size_px/2]
]
frame_stim = visual.ShapeStim(
    win=win,
    lineWidth=5,
    lineColor=[-1, -1, -1],
    fillColor=None,
    vertices=frame_coords,
    closeShape=True,
    size=frame_size,
    autoLog=False,
    autoDraw=False
)

region_size = 2
region_size_px = deg2pix(degrees=2, monitor=mon)
region = visual.Circle(win=win, lineColor=[0, 0, 0], radius=region_size_px, autoLog=False)

fix_size = 1
fix_size_px = deg2pix(fix_size, mon)
fix = visual.GratingStim(win=win, mask="cross", size=fix_size_px, sf=0, color=[-1, -1, -1])

probe_size = .7
probe_size_px = deg2pix(probe_size, mon)
probe_top = visual.Circle(win=win, radius=probe_size_px, fillColor='red', contrast=.6)
probe_bot = visual.Circle(win=win, radius=probe_size_px, fillColor='red', contrast=.6)

# ============================================================
#                          Procedure
# ============================================================
# timing
trial_clock = core.Clock()
block_clock = core.Clock()

# Blocks
conditions = []
path_len = 10  # degrees
path_len_px = deg2pix(path_len, monitor=mon)

# motion_cycles = np.array([1.5, 2, 2.5])  # seconds
motion_cycles = np.array([.5])
motion_cycles_fr = motion_cycles * refresh_rate

speeds = path_len / motion_cycles_fr  # deg/fr
speeds_px = path_len_px / motion_cycles_fr  # px/fr

cues_cycles = [i for i in range(4, 9)]  # how many half cycles before cuing

for target in ["top", "bot"]:
    for i, speed in enumerate(speeds):
        conditions.append(
            {
                "target": target,
                "speed": np.round(speed, 2),
                "speed_px": np.round(speeds_px[i], 2),
                "motion_cycle": motion_cycles[i],  # in seconds
                "delay": np.round(np.random.uniform(400, 600)),  # delay before start in ms
                "t_cue": np.random.choice(cues_cycles)
            }
        )

block_handlers = []
# n_blocks = 12
n_blocks = 1
# total_trials = 384
total_trials = 2

for block in range(n_blocks):
    b = data.TrialHandler(
        name=f"Block_N{block}",
        trialList=conditions,
        nReps=total_trials/n_blocks,
        method="fullRandom",
        originPath=-1
        )
    block_handlers.append(b)

# ============================================================
#                          Run
# ============================================================
# Runtime parameters
n_stabilize = 5  # number of transitions needed to stabilize the effect
flash_frames = 3  # frames
frame_shift = 10
frame_start_pos = [-path_len_px/2, deg2pix(frame_shift, mon)]
probe_shift = deg2pix(2, mon)
win.mouseVisible = False

# loop blocks
for idx, block in enumerate(block_handlers):

    print(f"============> Block number {idx + 1}")

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

        # start eye tracking
        tracker.start_recording()
        tracker.status_msg(f"trial {n}")
        tracker.log("start_trial {} target {}".format(n, trial["target"]))

        # fixation period
        fix.autoDraw = True
        core.wait(trial["delay"]/1000)

        frame_stim.pos = frame_start_pos
        move_frames = trial["motion_cycle"] * refresh_rate

        probe_top.pos = [60, frame_stim.pos[1] + probe_shift]
        probe_bot.pos = [-60, frame_stim.pos[1] - probe_shift]

        # move frame for stabilization period
        for s in range(n_stabilize):
            for fr in range(int(move_frames)):
                frame_stim.pos += [trial["speed_px"], 0]
                frame_stim.draw()
                win.flip()

            # probe_top.pos = [frame_stim.pos[0], frame_stim.pos[1] + probe_shift]
            for fr in range(flash_frames):
                probe_top.draw()
                # frame_stim.draw()
                win.flip()
            
            for fr in range(int(move_frames)):
                frame_stim.pos -= [trial["speed_px"], 0]
                frame_stim.draw()
                win.flip()

            for fr in range(flash_frames):
                probe_bot.draw()
                # frame_stim.draw()
                win.flip()

        # pre-cue motion and cue
        print(trial["t_cue"]-1)
        for c in range(int(trial["t_cue"])):

            if c == trial["t_cue"] - 1:
                if trial["target"] == "top":
                    probe_top.color = 'blue'
                else:
                    probe_bot.color = 'blue'
            
            for fr in range(int(move_frames)):
                if c % 2:
                    frame_stim.pos -= [trial["speed_px"], 0]
                else:
                    frame_stim.pos += [trial["speed_px"], 0]
                frame_stim.draw()
                win.flip()

            for fr in range(flash_frames):
                if c % 2:
                    # probe_top.pos = [frame_stim.pos[0], frame_stim.pos[1] - probe_shift]
                    probe_bot.draw()
                else:
                    # probe_bot.pos = [frame_stim.pos[0], frame_stim.pos[1] + probe_shift]
                    probe_top.draw()
                t0 = win.flip()
            
            win.flip()
            probe_top.color = 'red'
            probe_bot.color = 'red'
            
        # wait for saccade
        t1, startpos = tracker.wait_for_fixation_end()
        t2, endpos = tracker.wait_for_fixation_start()

        # stop tracking
        tracker.stop_recording()

        # save the data
        if trial["target"] == "top":
            block.data.add("target_pos_x", np.round((probe_top.pos[0] + my_monitors[mon_name]["size_px"][0]/2), 2))
            block.data.add("target_pos_y", np.round((my_monitors[mon_name]["size_px"][1]/2 - probe_top.pos[1]), 2))
        else:
            block.data.add("target_pos_x", np.round((probe_bot.pos[0] + my_monitors[mon_name]["size_px"][0]/2), 2))
            block.data.add("target_pos_y", np.round((my_monitors[mon_name]["size_px"][1]/2 - probe_bot.pos[1]), 2))
        # block.data.add("saccade_delay", t1 - t0)
        block.data.add("saccade_spos_x", np.round(startpos[0], 2))
        block.data.add("saccade_spos_y", np.round(startpos[1], 2))
        block.data.add("saccade_epos_x", np.round(endpos[0], 2))
        block.data.add("saccade_epos_y", np.round(endpos[1], 2))
        block.data.add("saccade_dur", np.round(t2 - t1, 2))
    win.recordFrameIntervals = False

for block, handler in enumerate(block_handlers):
    run_file = DATA_DIR / f"sub-{sub_id}_ses-{ses}_run-{block+1}_task-{TASK}_eyetracking"
    handler.saveAsWideText(fileName=str(run_file), delim=',')

tracker.close()
win.close()
core.quit()
