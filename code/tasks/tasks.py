#!usr/bin/env python
"""
Created at 3/1/21
@author: devxl

FIPS saccade experiment task classes
"""
from _base import BaseExperiment
from fips import *

from psychopy import logging, core, data, visual, info, event
from psychopy.tools.monitorunittools import deg2pix
from pygaze import eyetracker, libtime, libscreen

import numpy as np
import pandas as pd


class Saccade(BaseExperiment):

    def __init__(self, title, task, session, subject, debug,
                 n_stabilize=4, path_length=8, refresh_rate=60, flash_dur=250, saccade_dur=600, frame_size=10):

        super().__init__(title, task, session, subject, debug)

        self.n_stabilize = n_stabilize
        self.path_length = path_length
        self.refresh_rate = refresh_rate
        self.flash_dur = flash_dur
        self.saccade_dur = saccade_dur
        self.frame_size = frame_size

        self.global_clock = core.Clock()

    def init_logging(self):
        logging.setDefaultClock(self.global_clock)
        logging.console.setLevel(logging.DEBUG)
        run_log = logging.LogFile(self.log_file, level=logging.DEBUG, filemode='w')
        run_log.write("Logging started...")

    def run(self):

        # Logging
        self.init_logging()
        logging.info(f"Date: {data.getDateStr()}")
        logging.info(f"Subject: {self.SUBJECT}")
        logging.info(f"Task: {self.TASK}")
        logging.info(f"Session: {self.SESSION}")
        logging.info("==================================================================")

        # Subject
        sub_params = self.get_sub_info()

        # Monitor
        exp_mon = self.make_monitor(name="OLED", scr_num=0, width=52, dist=60)

        # Eye tracker
        tracker = eyetracker.EyeTracker(self.window)

        # ============================================================
        #                          Stimuli
        # ============================================================

        # convert FIPS frame size to pixels
        frame_size = deg2pix(degrees=self.frame_size, monitor=self.monitor)

        # get the FIPS frame
        fips_frame = FIPS(win=self.window, size=frame_size, pos=[-3, 3], name='FIPSFrame')

        # define the critical region
        # when gaze leaves this region (after cue) the target will disappear
        reg_size = deg2pix(degrees=2, monitor=self.monitor)
        critical_region = visual.Circle(win=self.window, lineColor=[0, 0, 0], radius=reg_size, autoLog=False)

        # messages
        begin_msg = visual.TextStim(win=self.window, text="Press any key to start.", autoLog=False)

        between_block_txt = "You just finished block {}. Number of remaining of blocks: {}.\n" \
                            "Press the spacebar to continue."
        between_block_msg = visual.TextStim(win=self.window, autoLog=False)

        fixation_msg = visual.TextStim(win=self.window, text="Fixate on the dot.", pos=[0, -200], autoLog=False)

        finish_msg = visual.TextStim(win=self.window, text="Thank you for participating!", autoLog=False)

        # ============================================================
        #                          Procedure
        # ============================================================
        # clocks for block an trial
        block_clock = core.Clock()
        trial_clock = core.Clock()

        # conditions
        cue_oscs = list(range(2, 5))  # number of oscillations before target color change
        speeds = [1, 1.5, 2]
        target_pos = ["top", "bot"]
        conditions = []

        for speed in speeds:
            for target in ["top", "bot"]:
                conditions.append(
                    {
                        "delay": np.random.choice(cue_oscs),
                        "target": target,
                        "frame_speed": speed
                    }
                )

        # number of blocks and trials
        n_blocks = 12
        total_trials = 384

        # experiment handler
        runtime_info = info.RunTimeInfo(
            win=self.window,
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
            dataFileName=str(self.run_file)
        )

        block_handlers = []
        for block in range(n_blocks):
            this_block = data.TrialHandler(
                name=f"Block_{block}",
                trialList=conditions,
                nReps=total_trials / n_blocks,
                method="fullRandom",
                originPath=-1
            )
            block_handlers.append(this_block)
            exp_handler.addLoop(this_block)

        # ============================================================
        #                          Run
        # ============================================================
        # draw beginning message
        begin_msg.draw()
        begin_time = self.window.flip()

        event.waitKeys(keyList=["space"])
        self.window.mouseVisible = False

        # loop blocks
        for idx, block in enumerate(block_handlers):

            # calibrate the eye tracker
            tracker.calibrate()

            # block setup
            if idx > 0:
                between_block_msg.draw()
                event.waitKeys(keyList=["space"])

            block_clock.reset()

            # loop trials
            for trial in block:

                self.window.recordFrameIntervals = True

                # quit the trial if this is set to True anywhere
                bad_trial = False

                # drift correction
                checked = False
                fips_stim.fixation.autoDraw = True
                while not checked:
                    self.window.flip()
                    checked = tracker.drift_correction()

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

    def trial_dataframe(self, subject):
        """

        Returns
        -------

        """
        columns = [
            "sub", "block", "trial", "task", "frame_speed", "target_pos", "cue_delay", "saccade_pos", "saccade_latency",
            "saccade_offset"
        ]

        df = pd.DataFrame(columns=columns)

        # conditions
        cue_oscs = list(range(2, 5))  # number of oscillations before target color change
        speeds = [1, 1.5, 2]
        target_pos = ["top", "bot"]

        # number of blocks and trials
        trials_per_cond = 16
        n_blocks = 4
        n_trials = trials_per_cond * len(speeds) * len(target_pos)

        for block in range(n_blocks):
            trial_n = 1

            for trial in range(trials_per_cond):
                for speed in speeds:
                    for target in target_pos:
                        row = [
                            subject, block, trial_n, "saccade", speed, target, np.random.choice(cue_oscs), np.nan,
                            np.nan, np.nan
                        ]
                        trial_n += 1







    def make_motion_seq(self):
        pass

    def make_trial_frames(self, trial):
        """

        Parameters
        ----------
        trial

        Returns
        -------

        """

        # convert path length to pixels
        path_length = deg2pix(degrees=self.path_length, monitor=self.monitor)

        # convert velocity from deg/s to pixel/frame
        v_frame = deg2pix(degrees=trial["velocity"], monitor=self.monitor) / self.refresh_rate

        # convert timing from ms to number of frames
        flash_dur = self.ms2frame(self.flash_dur)
        saccade_dur = self.ms2frame(self.saccade_dur)

        # velocity of the frame is in pixel/frame
        # since the motion cycle is for a full path + 2 flashes at the end points, the velocity of the frame will be
        # for half a path - one flash duration
        path_duration = path_length * (1/v_frame)
        motion_cycle = (path_duration + flash_dur) * 2

        # durations of a given trial in frames
        trial_durs = np.asarray([
            self.ms2frame(trial["delay"]),  # fixation period is a variable duration to establish fixation
            self.n_stabilize * motion_cycle,  # stabilization period is a number of oscillation to stabilize
            self.ms2frame(trial["n_cue"]) * motion_cycle,  # cue period is number of oscillations before color change
            saccade_dur  # Saccade period is the maximum amount of time for executing a saccade and finishing the trial
        ])

        # arrays to get the frame numbers for each part of the trial
        n_total_frames = trial_durs.sum()
        fixation_frames = []
        stabilization_frames = []
        cue_frames = []
        saccade_frames = []

        # add frame numbers for each part
        n_frame = 0
        while n_frame < n_total_frames:

            # check if in fixation period
            if n_frame < trial_durs[0]:
                fixation_frames.append(n_frame)

            # check stabilization period
            elif trial_durs[0] <= n_frame < trial_durs[1]:
                stabilization_frames.append(n_frame)

            # check if in cue period
            elif trial_durs[1] <= n_frame < trial_durs[2]:
                cue_frames.append(n_frame)

            # for saccade period
            else:
                saccade_frames.append(n_frame)

            # go to next frame
            n_frame += 1

        trial_frames = {
            'fix': fixation_frames, 'stabilize': stabilization_frames, 'cue': cue_frames, 'saccade': saccade_frames
        }

        return trial_frames

    def ms2frame(self, duration):
        return self.refresh_rate * duration / 1000
