#!usr/bin/env python
"""
Created at 3/1/21
@author: Sharif Saleki

Base experiment class
"""
from psychopy import gui, data, core, monitors, info, logging, visual, event
from psychopy.iohub.devices import Computer

from pathlib import Path
import sys
import platform
import pyglet
import pandas as pd
import numpy as np

import abc
from typing import Dict, List, Union

from utils import jitter, get_screens


class BaseExperiment:
    """
    Template of experiments with basic functionality.
    Mostly deals with setting up primitive objects and settings like subject info, paths, system checks, etc.

    Basically every experiment needs the following attributes/functionalities:
        - Path to Home and other directories.
        - Settings that are specific to the experiment (metadata, conditions, etc.). An example of this can be found
            in docs/examples. This file should live under config/ directory of the experiment.
        - Parameters are data about the subject and are collected from input gui and/or commandline args.
        - A monitor and a window.
        - Keeping track of timings.
        - Initiate flow via handlers.
        - Feedback, logs, and warnings.

    Parameters
    ----------
    title : str
        Experiment's name.

    debug : bool
        For development use. If set to True bypasses many repetitive stages.
    """

    def __init__(self, title: str, task: str, session: int, subject: str, debug: bool) -> None:

        self.NAME = title
        self.DEBUG = debug
        self.TASK = task
        self.SESSION = session
        self.SUBJECT = subject

        # paths
        self.HOME = Path('.').resolve().parent
        self.CONFIG_DIR = self.HOME / "code" / "config"
        self.DATA_DIR = self.HOME / "data"
        self._check_paths()

        # TODO: show a dialogue to select participant
        self.monitor = None
        self._window = None
        self._handlers = dict()
        self.warnings = {
            "Files": [],
            "System": []
        }

        self.startup()

    @abc.abstractmethod
    def run(self):
        pass

    def get_sub_info(self) -> dict:
        """
        Shows a gui dialog to get subject info.

        Returns
        -------
        dict of subject input.
        """

        # open participants file
        part_file = pd.read_csv(str(self.DATA_DIR / "participants.tsv"), sep="\t", index_col=0)

        # information that's not specific to an experiment
        sub_dlg = gui.Dlg(title="Participant Information", labelButtonOK="Register", labelButtonCancel="Quit")

        # experiment
        sub_dlg.addText(text="Experiment", color="blue")
        sub_dlg.addFixedField("Date:", str(data.getDateStr()))
        sub_dlg.addFixedField("Title:", self.NAME)
        sub_dlg.addFixedField("Task:", self.TASK)
        sub_dlg.addFixedField("Session:", self.SESSION)
        sub_dlg.addFixedField("SubjectID:", self.SUBJECT)

        # subject
        sub_dlg.addText(text="Participant info", color="blue")
        sub_dlg.addField("NetID:", tip="Leave blank if you do not have one")
        sub_dlg.addField("Initials:", tip="Lowercase letters separated by dots (e.g. g.o.d)")
        sub_dlg.addField("Gender:", choices=["Male", "Female"])
        sub_dlg.addField("Age:", choices=list(range(18, 81)))
        sub_dlg.addField("Handedness:", choices=["Right", "Left"])
        sub_dlg.addField("Vision:", choices=["Normal", "Corrected"])

        sub_info = sub_dlg.show()
        if sub_dlg.OK:
            _ok_info = [
                self.SUBJECT, sub_info[5], sub_info[6], sub_info[7][0], sub_info[8], sub_info[9][0], sub_info[10]
            ]
            part_file.loc[len(part_file)] = _ok_info
        else:
            core.quit()

        return sub_info

    def make_monitor(self, name: str, scr_num: int, width: float, dist: float) -> monitors.Monitor:
        """
        Creates and saves a monitor.

        Parameters
        ------
        name : str
        scr_num : int
            0 for internal and 1 for external screen
        width : float
            width of the display in cm
        dist : float
            distance from the display in cm

        Returns
        -------
        psychopy.monitors.Monitor
        """

        all_mons = monitors.getAllMonitors()

        if name in all_mons:
            _monitor = monitors.Monitor(name=name)
        else:
            screen = get_screens()[scr_num]
            _monitor = monitors.Monitor(name=name)
            _monitor.setSizePix((int(screen.width), int(screen.height)))
            _monitor.setWidth(width)
            _monitor.setDistance(dist)
            _monitor.save()

        # TODO: set calibration and Gamma

        self.monitor = _monitor
        return _monitor

    @property
    def window(self):
        """
        Creates a window to display stimuli.

        Returns
        -------
        psychopy.visual.Window
        """
        if self._window is None:

            # generate the window
            self._window = visual.Window(
                name="ExperimentWindow",
                monitor=self.monitor,
                winType="pyglet",
                fullscr=True,
                screen=int(not self.DEBUG),
                checkTiming=True,
                gammaErrorPolicy='ignore',
                allowGUI=False,
                color=[0, 0, 0],
                units='pix',
                autoLog=False
            )

        return self._window

    def timing(self, durations, data_points):
        """
        Compiles the timing of different stages (and adds jitter)

        Returns
        -------
        dict :

        """
        _timing = dict()

        # timing values are dicts under 'durations' in the experiment settings
        for key, val in durations:

            # the first index is the duration. second one is how much random jitter it should have.
            duration = jitter(val[0], val[1])
            _timing[key] = duration
            _timing["trial"] += duration

        _timing["total"] = _timing["trial"] * data_points / 60 / 1000

        return _timing

    def startup(self):
        """
        Check system status and ask which monitor to set up.

        Returns
        -------

        """
        # run checks
        self._check_paths()
        self._system_status()

        # add the check results to a gui
        report_gui = gui.Dlg(title='Report', labelButtonOK='Continue', size=100,
                             labelButtonCancel="Quit", screen=int(not self.DEBUG))

        for key in self.warnings.keys():
            report_gui.addText(text=f"{key}", color="blue")
            vals = self.warnings[key]
            if len(vals):
                for i in vals:
                    report_gui.addText(text=f"{i}", color='red')
            else:
                report_gui.addText(text="All Passed.", color='green')

        # show it
        _resp = report_gui.show()

        # check debug mode
        if not self.DEBUG:
            if not report_gui.OK:
                self.end()

    def end(self):
        """
        Closes the experiment
        """
        self.window.close()
        core.quit()
        sys.exit()

    def force_quit(self, key: str = 'space') -> None:
        """
        Quits the experiment during runtime if a key (default 'space') is pressed.

        Parameters
        ----------
        key : str
            keyboard button to press to quit the experiment.
        """
        pressed = event.getKeys()
        if key in pressed:
            self.window.close()
            core.quit()
            sys.exit()

    def _check_paths(self):
        """
        Finds out if critical paths exist.
        """
        if not self.CONFIG_DIR.exists():
            self.warnings["Files"].append("Config directory not found.")
        if not self.DATA_DIR.exists():
            self.warnings["Files"].append("Data directory not found.")

        sub_dir = self.DATA_DIR / f"sub-{self.SUBJECT}"
        ses_dir = sub_dir / f"{self.TASK}"

        if not sub_dir.is_dir():
            sub_dir.mkdir()
        if not ses_dir.is_dir():
            ses_dir.mkdir()

        self.log_file = str(ses_dir / f"sub-{self.SUBJECT}_ses-{self.SESSION}_task-{self.TASK}.log")
        self.run_file = str(ses_dir / f"sub-{self.SUBJECT}_ses-{self.SESSION}_task-{self.TASK}")

    def _system_status(self):
        """
        Check system status: windowRefreshTimeSD, systemMemFreeFRAM, systemUserProcFlagged, priority
        """

        # TODO: Add comments
        # TODO: Log everything

        # initial system check
        _run_info = info.RunTimeInfo(
            # win=self.window,
            refreshTest='grating',
            userProcsDetailed=True,
            verbose=True
        )
        thresh = 0.20  # refresh rate standard deviation threshold

        # start logging
        logging.info("SYSTEM CHECKS\n======")

        # check internet connection for saving files to server
        if not _run_info["systemHaveInternetAccess"]:
            self.warnings["System"].append("No internet access.")

        # check the monitor refresh time
        refresh_sd = _run_info["windowRefreshTimeSD_ms"]
        if refresh_sd > thresh:
            self.warnings["System"].append(f"Monitor refresh rate is too unreliable: {refresh_sd}")

            # if _run_info["windowIsFullScr"]:
            flagged = _run_info['systemUserProcFlagged']
            if len(flagged):
                s = "Quit and close these programs to fix the refresh rate issue:\n"
                app_set = {}
                for i in range(len(_run_info['systemUserProcFlagged']) - 1):
                    if _run_info['systemUserProcFlagged'][i][0] not in app_set:
                        app_set.update({_run_info['systemUserProcFlagged'][i][0]: 0})
                while len(app_set) != 0:
                    s += f"\t--{app_set.popitem()[0]}\n"
                self.warnings["System"].append(s)

        if _run_info["systemMemFreeRAM"] < 1000:
            self.warnings["System"].append(
                "Not enough available RAM: {round(_run_info['systemMemFreeRAM'] / 1000)} GB is available."
            )

        # if it's Mac OS X (these methods don't run on that platform)
        if platform == "darwin":
            self.warnings["System"].append("Could not raise the priority because you are on Mac OS X.")
        else:
            Computer.setPriority("realtime", disable_gc=True)