#!usr/bin/env python
"""
Created at 2/6/21
@author: devxl

Testing script for saccade task
"""
from psychopy import visual, gui, data, monitors, core, logging
from psychopy.iohub.client import yload, yLoader
from psychopy.iohub import launchHubServer
from fips import FIPS
from psycphys import *
from pathlib import Path
from uuid import UUID
import pandas as pd
import sys

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
run_file = str(run_dir / f"sub-{sub_id}_ses-{ses}_task-{task}.csv")

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
    units='deg',
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
tracker_config = yload(open(str(config_dir / 'tracker_config.yaml'),'r'), Loader=yLoader)
hub = launchHubServer(**tracker_config)
tracker = hub.devices.tracker

# ============================================================
#                          PROCEDURE
# ============================================================
stim = FIPS(win=win)

probe = stim.generate_probe()