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

    def __init__(self, title: str, task: str, session: int, subject: str, monitor: str, debug: bool) -> None:

        self.NAME = title
        self.DEBUG = debug
        self.MONITOR = monitor
        self.TASK = task
        self.SESSION = session
        self.SUBJECT = subject

        # paths
        self.HOME = Path('.').resolve().parent
        self.CONFIG_DIR = self.HOME / "code" / "config"
        self.DATA_DIR = self.HOME / "data"

        # TODO: show a dialogue to select participant
        self._monitor = None
        self._window = None
        self._timing = dict()
        self._handlers = dict()
        self.warnings = {
            "Files": [],
            "System": []
        }

        self.startup()

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

    @staticmethod
    def make_monitor(name: str, scr_num: int, width: float, dist: float) -> monitors.Monitor:
        """
        Creates and saves a monitor with user's initials.

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

        return _monitor

    @property
    def window(self, monitor, scr_num):
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
                monitor=monitor,
                winType="pyglet",
                fullscr=True,
                screen=scr_num,
                checkTiming=True,
                gammaErrorPolicy='ignore',
                allowGUI=False,
                color=[0, 0, 0],
                units='deg',
                autoLog=False
            )

        return self._window

    @property
    def timing(self) -> Dict[str, int]:
        """
        Compiles the timing of different stages (and adds jitter)

        Returns
        -------
        dict :

        """

        if not self._timing:

            self._timing["trial"] = 0
            self._timing["total"] = 0

            # timing values are dicts under 'durations' in the experiment settings
            for key, val in self.settings.get('EXPERIMENT').get('durations').items():

                # the first index is the duration. second one is how much random jitter it should have.
                duration = jitter(val[0], val[1])
                self._timing[key] = duration
                self._timing["trial"] += duration

            self._timing["total"] = int(self._timing["trial"] *
                                        (self.settings["data_points"]["main"] + self.settings["data_points"]["practice"])
                                        / 60 / 1000)

        return self._timing

    @property
    def handlers(self) -> Dict:
        """
        Experiment handler added by default. To add more use add_handler().

        Returns
        -------
        dict
        """
        if not self._handlers:

            # experiment handler
            self._handlers["exp"] = data.ExperimentHandler(
                name=f"{self.NAME}Handler",
                version=self.settings.get("EXPERIMENT")["version"],
                extraInfo=self.parameters,
                savePickle=False,
                saveWideText=False
            )

        return self._handlers

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
                             labelButtonCancel="Quit", screen=self.parameters["screen_number"])

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
        if not self.MODE:
            if not report_gui.OK:
                self.end()

    def add_handler(self, name: str, conditions: List[Dict]) -> None:
        """
        Adds a psychopy TrialHandler to self.handlers.
        Also, adds it as a loop to the experiment handler.

        Parameters
        ----------
        name : str

        conditions : list
            can be generated using psychopy.data.importConditions() or by looping through lists of conditions.
        """

        # trial handler
        self.handlers[name] = data.TrialHandler(
            name=f"{name}Handler",
            trialList=conditions,
            nReps=int(self.settings.get("EXPERIMENT")["data_points"][name]),
            method='random'
        )

        # add it to the high-level experiment handler too
        self.handlers["exp"].addLoop(self.handlers[name])

    def init_logging(self, clock):
        """
        Generates the log file to populate with messages throughout the experiment.

        Parameters
        ----------
        clock : psychopy.clock.Clock
            experiment's global clock that is used to timestamp events.

        Returns
        -------

        """
        logging.setDefaultClock(clock)

        # use ERROR level for the console and DEBUG for the logfile
        logging.console.setLevel(logging.ERROR)
        log_data = logging.LogFile(self.data_paths["log"], filemode='w', level=logging.DEBUG)

        return log_data

    def save(self):
        """
        # TODO: add upload to NAS psychopy.web.requireInternetAccess
        Save the experiment into a file
        """
        for handler in self.handlers:
            handler.saveAsWideText(self.data_paths["session"], delim=',')

        self.window.saveFrameIntervals(self.data_paths["frames"])

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
        data_dir = self.HOME_DIR / "data"
        config_dir = self.HOME_DIR / "config"

        if not config_dir.exists():
            self.warnings["Files"].append("Config directory not found.")
        if not data_dir.exists():
            self.warnings["Files"].append("Data directory not found.")

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


def jitter(time: int, lag) -> float:
    """
    Adds or subtracts some jitter to a time period

    Parameters
    ----------
    time : float
    lag : float
        minimum/maximum amount of jitter

    Returns
    -------
    float
        modified duration
    """
    durations = np.linspace(-lag, lag, num=10)
    time += np.random.choice(durations, 1)

    return time/1000


def get_screens():
    """
    Use pyglet to find screens and their resolution

    Returns
    -------

    """

    pl = pyglet.canvas.get_display()
    screens = pl.get_screens()

    return screens
