#!usr/bin/env python
"""
Created at 2/6/21
@author: devxl

Testing script for saccade task
"""
from psychopy import visual, gui, data, monitors, core, logging, info, event
from psychopy.tools.monitorunittools import deg2pix
from psychopy.iohub.client import yload, yLoader
from psychopy.iohub import launchHubServer
from fips import FIPS
from psycphys import *
from pathlib import Path
from uuid import UUID
import pandas as pd
import sys
import numpy as np


# ============================================================
#                          SETUP
# ============================================================

# Experiment 
# names 
NAME = "FIPSSaccade"
SESSIONS = 4
PATH = Path('.').resolve() 
sub_id = int(sys.argv[1])
ses = sys.argv[2]

# task
if ses == "0":
    task = "train"
elif ses in ["1", "2"]:
    task = "percept"
elif ses in ["3", "4"]:
    task = "saccade"
else:
    raise ValueError("Session number out of range.")

# directories
config_dir = PATH / "config"
data_dir = PATH.parent / "data" 
sub_id = f"{sub_id:02d}"
sub_dir = data_dir / f"sub-{sub_id}"
ses_dir = sub_dir / f"ses-{ses}"
log_dir = ses_dir / "log"
run_dir = ses_dir / "run"

if not sub_dir.is_dir():
    sub_dir.mkdir()
ses_dir.mkdir()
log_dir.mkdir()
run_dir.mkdir()

# files
log_file = str(log_dir / f"sub-{sub_id}_ses-{ses}_task-{task}.log")
run_file = str(run_dir / f"sub-{sub_id}_ses-{ses}_task-{task}")

# Info
sub_dlg = gui.Dlg(title="Participant Information", labelButtonOK="Register", labelButtonCancel="Quit")

# experiment
sub_dlg.addText(text="Experiment", color="blue")
sub_dlg.addFixedField("Title:", NAME)
sub_dlg.addFixedField("Date:", str(data.getDateStr()))
sub_dlg.addFixedField("Session:", ses)
sub_dlg.addFixedField("Task:", task)

# subject
sub_dlg.addText(text="Participant info", color="blue")
sub_dlg.addFixedField("ID:", sub_id)
sub_dlg.addField("NetID:", tip="Leave blank if you do not have one")
sub_dlg.addField("Initials:", tip="Lowercase letters separated by dots (e.g. g.o.d)")
sub_dlg.addField("Age:", choices=list(range(18, 81)))
sub_dlg.addField("Gender:", choices=["Male", "Female"])
sub_dlg.addField("Handedness:", choices=["Right", "Left"])
sub_dlg.addField("Vision:", choices=["Normal", "Corrected", "Other"])

sub_params = {}
sub_info = sub_dlg.show()
if sub_dlg.OK:
    sub_params["date"] = sub_info[1]
    sub_params["netid"] = sub_info[5]
    sub_params["initials"] = sub_info[6]
    sub_params["age"] = int(sub_info[7])
    sub_params["sex"] = sub_info[8]
    sub_params["handedness"] = sub_info[9]
    sub_params["vision"] = sub_info[10]
else:
    core.quit()

# Display
disp = make_test_monitor()

# Window
win = visual.Window(
    size=[1024, 768],
    fullscr=False,
    allowGUI=False,
    monitor=disp,
    screen=0,
    units='pix',
    gamma=None,
    name='SaccadeWindow'
)

# Logging
global_clock = core.Clock()
logging.setDefaultClock(global_clock)
logging.console.setLevel(logging.DEBUG)
run_log = logging.LogFile(log_file, level=logging.DEBUG, filemode='w')
logging.info(data.getDateStr())

# Eye-tracker
tracker_config = yload(open(str(config_dir / 'tracker_config.yaml'), 'r'), Loader=yLoader)
hub = launchHubServer(**tracker_config)
tracker = hub.devices.tracker

# ============================================================
#                          Stimulus
# ============================================================
stim_size = deg2pix(degrees=10, monitor=disp)
stim = FIPS(win=win, size=stim_size, pos=[0, 3], name='ExperimentFrame')

removal_region_size = deg2pix(degrees=2, monitor=disp)
removal_region = visual.Circle(win=win, lineColor=[0, 0, 0], radius=removal_region_size)

# messages
begin_msg = visual.TextStim(win=win, text="Press any key to start.")
between_block_msg = visual.TextStim(
    win=win,
    text="You just finished block {}. Number of remaining of blocks: {}.\nPress the spacebar to continue."
)
fixation_msg = visual.TextStim(win=win, text="Fixate on the dot.", pos=[0, -200])
finish_msg = visual.TextStim(win=win, text="Thank you for participating!")

# ============================================================
#                          Procedure
# ============================================================
# timing
trial_clock = core.Clock()
motion_cycle = 1500  # in ms for a cycle of frame motion
saccade_times = np.linspace(start=0, stop=1500, num=6)

# experiment
n_blocks = 12
total_trials = 384
block_clock = core.Clock()

runtime_info = info.RunTimeInfo(
    win=win,
    refreshTest="grating",
    verbose=True,
    userProcsDetailed=True,
)
exp_handler = data.ExperimentHandler(
    name="SaccadeExperiment",
    version=0.1,
    extraInfo=sub_params,
    runtimeInfo=runtime_info,
    savePickle=False,
    saveWideText=True,
    dataFileName=str(run_file)
)

# Blocks
conditions = []
velocities = [1, 1.5, 2]
for target in ["top", "bot"]:
    for velocity in velocities:
        conditions.append(
            {
                "target": target,
                "velocity": velocity,
                "delay": np.round(np.random.uniform(400, 600)),
                "t_cue": np.random.choice(saccade_times)
            }
        )
block_handlers = []

for block in range(n_blocks):
    this_block = data.TrialHandler(
        name=f"Block_{block}",
        trialList=conditions,
        nReps=total_trials/n_blocks,
        method="fullRandom",
        # seed=block,
        originPath=-1
        )
    block_handlers.append(this_block)
    exp_handler.addLoop(block)

# ============================================================
#                          Run
# ============================================================
n_stabilize = 4  # number of transitions needed to stabilize the effect
path_length = deg2pix(degrees=8, monitor=disp)  # the length of the path that frame moves
v_frame = deg2pix(degrees=1, monitor=disp)  # how fast the frame moves
display_rf = 60
flash_frames = 5
saccade_dur = 600

# draw beginning message
begin_msg.draw()
begin_time = win.flip()
hub.sendMessageEvent(text="EXPERIMENT_START", sec_time=begin_time)
event.waitKeys(keyList=["space"])

# loop blocks
for idx, block in enumerate(block_handlers):

    # calibrate the eye tracker
    tracker.runSetupProcedure()

    # initiate eye tracker
    tracker.setRecordingState(True)

    # block setup
    if idx > 0:
        between_block_msg.draw()
        event.waitKeys(keyList=["space"])
    
    hub.clearEvents()
    win.recordFrameIntervals = True
    block_clock.reset()

    # loop trials
    for trial in block:

        trial_durs = np.asarray([
            trial["delay"],  # fixation period
            (n_stabilize * path_length / v_frame) * 2,  # stabilization period
            flash_frames * 2,  # stabilization period
            trial["t_cue"],  # cue period
            saccade_dur,  # saccade
        ])

        n_frames = trial_durs.sum() * display_rf

        # detect fixation
        fixate = detect_fixation(tracker, stim.fixation)

        if fixate:
            for fr in range(n_frames):
                
                # get eye position
                gaze_pos = tracker.getLastGazePosition()

                # check if it's valid
                valid_gaze_pos = isinstance(gaze_pos, (tuple, list))

                # run the procedure while fixating
                if valid_gaze_pos:
                    if self.fixation.contains(gaze_pos):