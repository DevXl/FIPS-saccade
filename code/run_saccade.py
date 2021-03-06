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
from utils import *
from pathlib import Path
import pandas as pd
import sys
import numpy as np

# ============================================================
#                          SETUP
# ============================================================

# Experiment 
# names 
NAME = "FIPSSaccade"
SESSIONS = 2
TASK = "saccade"
PATH = Path('.').resolve() 
sub_id = int(sys.argv[1])
ses = sys.argv[2]
if ses not in ["1", "2"]:
    raise ValueError("Session is not valid.")

# directories
config_dir = PATH / "config"
data_dir = PATH.parent / "data" 
sub_id = f"{sub_id:02d}"
sub_dir = data_dir / f"sub-{sub_id}"
ses_dir = sub_dir / f"{TASK}"

if not sub_dir.is_dir():
    sub_dir.mkdir()
if not ses_dir.is_dir():
    ses_dir.mkdir()

# files
log_file = str(ses_dir / f"sub-{sub_id}_ses-{ses}_task-{TASK}.log")
run_file = str(ses_dir / f"sub-{sub_id}_ses-{ses}_task-{TASK}.csv")

# Info
sub_dlg = gui.Dlg(title="Participant Information", labelButtonOK="Register", labelButtonCancel="Quit")

# experiment
sub_dlg.addText(text="Experiment", color="blue")
sub_dlg.addFixedField("Title:", NAME)
sub_dlg.addFixedField("Date:", str(data.getDateStr()))
sub_dlg.addFixedField("Session:", ses)
sub_dlg.addFixedField("Task:", TASK)

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
if ses == "1":
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
    screen=1,
    units='pix',
    gamma=None,
    name='SaccadeWindow'
)

# Logging
global_clock = core.Clock()
logging.setDefaultClock(global_clock)
logging.console.setLevel(logging.DEBUG)
run_log = logging.LogFile(log_file, level=logging.DEBUG, filemode='w')
logging.info(f"Date: {data.getDateStr()}")
logging.info(f"Subject: {sub_id}")
logging.info(f"Task: {TASK}")
logging.info(f"Session: {ses}")
logging.info("==========================================")

# Eye-tracker
# try:
#     tracker_config = yload(open(str(config_dir / 'tracker_config.yaml'), 'r'), Loader=yLoader)
#     hub = launchHubServer(**tracker_config)
#     tracker = hub.getDevice('tracker')
#     print(tracker)
# except Exception as e:
#     logging.error(f"Could not initiate eye tracking: {e}")
TRACKER = 'eyelink'
eyetracker_config = dict(name='tracker')
tracker_config = None
eyetracker_config['model_name'] = 'EYELINK 1000 DESKTOP'
eyetracker_config['simulation_mode'] = False
eyetracker_config['runtime_settings'] = dict(sampling_rate=1000, track_eyes='RIGHT')
tracker_config = {'eyetracker.hw.sr_research.eyelink.EyeTracker':eyetracker_config}
hub = launchHubServer(**tracker_config)
tracker = hub.getDevice('tracker')

# ============================================================
#                          Stimulus
# ============================================================
stim_size = deg2pix(degrees=10, monitor=disp)
stim = FIPS(win=win, size=stim_size, pos=[0, 3], name='ExperimentFrame')

crit_region_size = deg2pix(degrees=2, monitor=disp)
crit_region = visual.Circle(win=win, lineColor=[0, 0, 0], radius=crit_region_size, autoLog=False)

# messages
begin_msg = visual.TextStim(win=win, text="Press any key to start.", autoLog=False)
between_block_txt = "You just finished block {}. Number of remaining of blocks: {}.\nPress the spacebar to continue."
between_block_msg = visual.TextStim(win=win, autoLog=False)
fixation_msg = visual.TextStim(win=win, text="Fixate on the dot.", pos=[0, -200], autoLog=False)
finish_msg = visual.TextStim(win=win, text="Thank you for participating!", autoLog=False)

# ============================================================
#                          Procedure
# ============================================================
# timing
trial_clock = core.Clock()
motion_cycle = 1500  # in ms for a cycle of frame motion
saccade_times = np.linspace(start=0, stop=1500, num=6)

# experiment
# n_blocks = 12
n_blocks = 1
# total_trials = 384
total_trials = 10
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
    exp_handler.addLoop(this_block)

# ============================================================
#                          Run
# ============================================================
# Runtime parameters
n_stabilize = 4  # number of transitions needed to stabilize the effect
path_length = deg2pix(degrees=8, monitor=disp)  # the length of the path that frame moves
display_rf = 60
flash_dur = 250
v_frame = path_length / (motion_cycle - 2*flash_dur)
saccade_dur = 600

# draw beginning message
begin_msg.draw()
begin_time = win.flip()
hub.sendMessageEvent(text="EXPERIMENT_START", sec_time=begin_time)
event.waitKeys(keyList=["space"])
win.mouseVisible = False

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

        # quit the trial if this is set to True anywhere
        bad_trials = []

        trial_durs = np.asarray([
            trial["delay"],  # fixation period
            2 * n_stabilize * motion_cycle,  # stabilization period
            trial["t_cue"],  # cue period
            saccade_dur  # Saccade period
        ])

        trial_frames = trial_durs * display_rf / 1000
        print(f"trial frames: {trial_frames}")

        n_total_frames = trial_frames.sum()

        fixation_frames = [i for i in range(int(trial_frames[0]))]

        stab_frames = [i for i in range(int(fixation_frames[-1])+1, int(trial_frames[1]))]
        stab_seq = make_motion_seq(
            path_dur=int(path_length * (1/v_frame) * display_rf / 1000),
            flash_dur=int(flash_dur * display_rf / 1000),
            n_repeat=n_stabilize + 1,  # +1 because of the cue period
            total_cycle=motion_cycle * display_rf / 1000
        )

        cue_frames = [i for i in range(int(stab_frames[-1]+1), int(trial_frames[2]+stab_frames[-1]+1))]

        # print((stab_frames[-1]+1), (int(trial_frames[2]+stab_frames[-1]+1)))
        saccade_frames = [i for i in range(int(cue_frames[-1])+1, int(trial_frames[3]+cue_frames[-1])+1)]
        saccade_seq = make_motion_seq(
            path_dur=int(path_length * (1 / v_frame) * display_rf / 1000),
            flash_dur=int(flash_dur * display_rf / 1000),
            n_repeat=1,
            total_cycle=motion_cycle * display_rf / 1000
        )

        # detect fixation
        fixate = False
        stim.fixation.autoDraw = True
        
        win.flip()

        while not fixate:
            fixate, msg = detect_fixation(tracker, stim.fixation)
            fixation_msg.text = msg
            fixation_msg.draw()
            win.flip()

        fixation_msg.text = ""
        fixation_msg.draw()
        stim.fixation.autoDraw = False
        win.flip()

        for fr in range(int(n_total_frames)):

            # get eye position
            gaze_pos = tracker.getLastGazePosition()

            # check if it's valid
            valid_gaze_pos = isinstance(gaze_pos, (tuple, list))

            if valid_gaze_pos:

                fix_ok = False

                # 1) FIXATION PERIOD
                if fr in fixation_frames:
                    stim.fixation.draw()

                    if stim.fixation.contains(gaze_pos):
                        fix_ok = True
                    else:
                        bad_trials.append(trial)
                        try:
                            block.next()
                        except StopIteration:
                            print("End of Block")

                # 2) STABILIZATION AND CUE PERIOD
                elif fr in (stab_frames + cue_frames):

                    stim.move_frame(fr, stab_seq)

                    stim.fixation.draw()
                    if stim.fixation.contains(gaze_pos):
                        fix_ok = True
                    else:
                        bad_trials.append(trial)
                        try:
                            block.next()
                        except StopIteration:
                            print("End of Block")

                # 3) SACCADE PERIOD
                elif fr in saccade_frames:
                    if crit_region.contains(gaze_pos):
                        stim.move_frame(fr, saccade_seq)

                exp_handler.nextEntry()

    tracker.setRecordingState(False)
    win.recordFrameIntervals = False

tracker.setConnectionState(False)
exp_handler.saveAsWideText(fileName=str(run_file))
hub.quit()
win.close()
core.quit()
