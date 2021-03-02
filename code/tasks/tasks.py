#!usr/bin/env python
"""
Created at 3/1/21
@author: devxl

FIPS saccade experiment task classes
"""
from _base import BaseExperiment
from _fips import FIPS

from psychopy import logging, core, data
from psychopy.tools.monitorunittools import deg2pix
from pygaze import eyetracker, libtime, libscreen


class Saccade(BaseExperiment):

    def __init__(self, title, task, session, subject, debug):
        super().__init__(title, task, session, subject, debug)

    def run(self):

        # Logging
        global_clock = core.Clock()
        logging.setDefaultClock(global_clock)
        logging.console.setLevel(logging.DEBUG)
        run_log = logging.LogFile(self.log_file, level=logging.DEBUG, filemode='w')
        run_log.write("Logging started...")

        logging.info(f"Date: {data.getDateStr()}")
        logging.info(f"Subject: {self.SUBJECT}")
        logging.info(f"Task: {self.TASK}")
        logging.info(f"Session: {self.SESSION}")
        logging.info("==========================================")

        # Eye tracker
        tracker = eyetracker.EyeTracker(self.window)

        # ============================================================
        #                          Stimulus
        # ============================================================
        stim_size = deg2pix(degrees=10, monitor=self.monitor)
        stim = FIPS(win=self.window, size=stim_size, pos=[0, 3], name='ExperimentFrame')

        crit_region_size = deg2pix(degrees=2, monitor=self.monitor)
        crit_region = visual.Circle(win=self.window, lineColor=[0, 0, 0], radius=crit_region_size, autoLog=False)

        # messages
        begin_msg = visual.TextStim(win=win, text="Press any key to start.", autoLog=False)
        between_block_txt = "You just finished block {}. Number of remaining of blocks: {}.\nPress the spacebar to continue."
        between_block_msg = visual.TextStim(win=win, autoLog=False)
        fixation_msg = visual.TextStim(win=win, text="Fixate on the dot.", pos=[0, -200], autoLog=False)
        finish_msg = visual.TextStim(win=win, text="Thank you for participating!", autoLog=False)