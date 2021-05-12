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
ROOTDIR = Path('.').resolve()  # find the current file
DATADIR = ROOTDIR.parent / "data" / "psycphys"
if not DATADIR.exists():
    print("Making the data directory...")
    DATADIR.mkdir()

sub_id = f"{sub_id:02d}"
SUBDIR = DATADIR / F"sub-{sub_id}"
if not SUBDIR.exists():
    print("Making the subject directory...")
    SUBDIR.mkdir()

TASK = "FIPSPerceptual"

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

mon_name = 'razerblade'
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
frame_size = 2.6
frame_coords = [
    [-frame_size/2, frame_size/2], [frame_size/2, frame_size/2],
    [frame_size/2, -frame_size/2], [-frame_size/2, -frame_size/2]
]
frame_pos = [0, 0]
frame_opac = 1
frame_stim = visual.ShapeStim(
    win=exp_win,
    pos=frame_pos,
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
top_pos = [0, frame_size/2 - probe_margin]
bot_pos = [0, -frame_size/2 + probe_margin]
probe_size = .9
probe_color = .1
top_probe = visual.Circle(
    win=exp_win,
    size=probe_size,
    pos=top_pos,
    fillColor=[-1, probe_color, -1],
    lineColor=[-1, -1, -1],
    contrast=1,
    lineWidth=3,
    autoLog=False
)
bot_probe = visual.Circle(
    win=exp_win,
    size=probe_size,
    pos=bot_pos,
    fillColor=[-1, probe_color, -1],
    lineColor=[-1, -1, -1],
    contrast=1,
    lineWidth=3,
    autoLog=False
)

# Concentric fixation circles
fix_pos = [-6, 0]
inner_fix = visual.Circle(win=exp_win, radius=0.1, pos=fix_pos, lineColor='black', autoLog=False)
outer_fix = visual.Circle(win=exp_win, radius=0.25, pos=fix_pos, lineColor='black', autoLog=False)

# Instructions
instr_stim = visual.TextStim(win=exp_win, pos=fix_pos, autoLog=False)
ph1_msg = "Match the orientation of the line on the left to the orientation of the SQUARE on the right.\n\nPress the spacebar to confirm your choice and continue."
ph2_msg = "Match the orientation of the line on the left to the orientation of the RED TARGET on the right.\n\nPress the spacebar to confirm your choice and continue."

# =========================================================================== #
# --------------------------------------------------------------------------- #
# ------------------------------ ! PROCEDURE -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Conditions
# Make a list of all condition permutations
bsl_stim = []  # baseline
rsp_stim = []  # IM response
# bsl_conds = ['dd-right']
bsl_conds = ['dd-right', 'control-right']  # for the baseline
rsp_conds = ['dd-right', 'no-drift', 'control-right']  # for the IM response
for bcond in bsl_conds:
    bsl_stim.append({"condition": bcond})
for rcond in rsp_conds:
    rsp_stim.append({'condition': rcond})

# Blocks and trials
# DD baseline 
bsl_nblocks = 1
bsl_ntrials = 12

# Im response
rsp_nblocks = 1
rsp_ntrials = 20

bsl_trials = data.TrialHandler(
            trialList=bsl_stim,
            nReps=bsl_ntrials,
            method='fullRandom',
            extraInfo={'sub': sub_id, 'ses': ses, "stage": "baselineDD"}
)
rsp_trials = data.TrialHandler(
            trialList=rsp_conds,
            nReps=rsp_ntrials,
            method='fullRandom',
            extraInfo={'sub': sub_id, 'ses': ses, "stage": "responseIM"}
)

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! RUN ------------------------------------ #
# --------------------------------------------------------------------------- #
# =========================================================================== #

# Initialize run params
v_env = .03  # envelope speed
v_tex = .02 # texture speed
n_frames = 180  # number of frames to move
n_reps = 3  # number of repetitions up and down the path
exp_win.refreshThreshold = (1/test_monitors[mon_name]["refresh_rate"]) + 0.003
bsl_dd_angles = []  # baseline reports for DD
bsl_control_angles = []  # baseline reports for control

exp_clock = core.Clock()
t_start = exp_clock.getTime()

# 1) DD Baseline stage
for block in range(bsl_nblocks):

    # make handler
    trials = data.TrialHandler(
            trialList=bsl_stim,
            nReps=bsl_ntrials,
            method='fullRandom',
            extraInfo={'sub': sub_id, 'ses': ses, "stage": "baselineDD"}
            )
    
    # show instruction
    instr_stim.text = ph1_msg
    instr_stim.draw()
    exp_win.flip()
    event.waitKeys(keyList="space")  # wait for response

    for trial in trials:

        # set the double-drift parameters according to the trial condition
        if trial["condition"] == 'dd-right':
            tex_motion = [v_tex, 0]
            env_motion = [0, v_env]
        elif trial["condition"] == 'control-right':
            tex_motion = [0, 0]
            env_motion = [v_env, v_env]

        # Start drawing
        exp_win.recordFrameIntervals = True
        inner_fix.autoDraw = True
        outer_fix.autoDraw = True

        # loop over repetitions
        for rep in range(n_reps):

            # control drawing every frame
            for frame in range(n_frames):

                for gabor in gabors:
                    # move up
                    if frame < n_frames / 2:
                        gabor.pos += env_motion
                        gabor.phase += tex_motion
                        # target.pos += [0, v_env]

                    # move down
                    else:
                        gabor.pos -= env_motion
                        gabor.phase -= tex_motion
                        # target.pos -= [0, v_env]

                    gabor.draw()
                # if not block:  # no target in practice block
                #     target.draw()
                exp_win.flip()

        # Clear the screen
        inner_fix.autoDraw = False
        outer_fix.autoDraw = False
        exp_win.recordFrameIntervals = False

        # Get the response
        event.clearEvents()
        resp = True
        while resp:

            # mouse wheel for controlling the orientation of the line
            ans_mouse = event.Mouse()
            wheel_dX, wheel_dY = ans_mouse.getWheelRel()
            adjust_line.setOri(wheel_dY * 5, '-')
            adjust_line.draw()
            exp_win.flip()

            # key press to signal the end of reporting
            all_keys = event.getKeys()
            if 'space' in all_keys:
                trial_ori = adjust_line.ori
                trials.data.add('angle', trial_ori)
                if trial["condition"] == "dd-right":
                    bsl_dd_angles.append(trial_ori)
                else:
                    bsl_control_angles.append(trial_ori)
                adjust_line.ori = 0
                exp_win.flip()
                resp = False
            elif 'escape' in all_keys:
                exp_win.close()
                core.quit()

        event.clearEvents()

    # save
    TASK = "baseline"
    run_file = SUBDIR / f"sub-{sub_id}_ses-{ses}_run-{block+1}_task-{TASK}_psychophysics"
    trials.saveAsWideText(fileName=str(run_file), delim=',')

# calculate the mean of baseline reports
bsl_dd = np.median(bsl_dd_angles)
bsl_control = np.median(bsl_control_angles)

# use the reported angles to adjust control condition to the same angle. It should be something like this:
#   1. Find out how off the reports are by comparing the actual (45 deg) and reported angles in the control condition
#   2. Add that to the double-drift reports to find out how much the new control condition should deviate from vertical 
#   3. Get the tan() of the new control angle and multiply it by v_env to get the vector in x direction

# find the disparity in report
report_disparity = bsl_control - 45

# find the desired deviation from vertical
# ctrl_angle = bsl_dd + report_disparity
ctrl_angle = bsl_dd

# set the new vectors
ctrl_vects = [np.tan(np.deg2rad(ctrl_angle)) * v_env, v_env]

# modulate target speed
target_mod = .6

# 2) IM response stage
for block in range(rsp_nblocks):

    # make handler
    trials = data.TrialHandler(
            trialList=rsp_stim,
            nReps=rsp_ntrials,
            method='fullRandom',
            extraInfo={'sub': sub_id, 'ses': ses, "stage": "reponseIM"}
            )
    
    # show instruction
    instr_stim.text = ph2_msg
    instr_stim.draw()
    exp_win.flip()
    event.waitKeys(keyList="space")  # wait for response

    for trial in trials:

        # set the double-drift parameters according to the trial condition
        if trial["condition"] == 'dd-right':
            tex_motion = [v_tex, 0]
            env_motion = [0, v_env]
        elif trial["condition"] == 'control-right':
            tex_motion = [0, 0]
            env_motion = ctrl_vects
        elif trial["condition"] == 'no-drift':
            tex_motion = [0, 0]
            env_motion = [0, v_env]

        # Start drawing
        exp_win.recordFrameIntervals = True
        inner_fix.autoDraw = True
        outer_fix.autoDraw = True

        # loop over repetitions
        for rep in range(n_reps):

            # control drawing every frame
            for frame in range(n_frames):

                for gabor in gabors:
                    # move up
                    if frame < n_frames / 2:
                        gabor.pos += env_motion
                        gabor.phase += tex_motion
                        target.pos += [0, v_env * target_mod]

                    # move down
                    else:
                        gabor.pos -= env_motion
                        gabor.phase -= tex_motion
                        target.pos -= [0, v_env * target_mod]

                    gabor.draw()
                target.draw()
                exp_win.flip()

        # Clear the screen
        inner_fix.autoDraw = False
        outer_fix.autoDraw = False
        exp_win.recordFrameIntervals = False

        # Get the response
        event.clearEvents()
        resp = True
        while resp:

            # mouse wheel for controlling the orientation of the line
            ans_mouse = event.Mouse()
            wheel_dX, wheel_dY = ans_mouse.getWheelRel()
            adjust_line.setOri(wheel_dY * 5, '-')
            adjust_line.draw()
            exp_win.flip()

            # key press to signal the end of reporting
            all_keys = event.getKeys()
            if 'space' in all_keys:
                trial_ori = adjust_line.ori
                trials.data.add('angle', trial_ori)
                adjust_line.ori = 0
                exp_win.flip()
                resp = False
            elif 'escape' in all_keys:
                exp_win.close()
                core.quit()

        event.clearEvents()

    # save
    TASK = "illusoryframe"
    run_file = SUBDIR / f"sub-{sub_id}_ses-{ses}_run-{block + 1 + bsl_nblocks}_task-{TASK}_psychophysics"
    trials.saveAsWideText(fileName=str(run_file), delim=',')

# =========================================================================== #
# --------------------------------------------------------------------------- #
# -------------------------------- ! WRAP UP -------------------------------- #
# --------------------------------------------------------------------------- #
# =========================================================================== #
t_end = exp_clock.getTime()
print(f"The experiment took {np.round((t_end - t_start), 2)}s")
# exp_win.saveFrameIntervals(fileName=frames_file)
exp_win.close()
core.quit()
