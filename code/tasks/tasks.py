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
        logging.info(f"Date: \t{data.getDateStr()}")
        logging.info(f"Subject: \t{self.SUBJECT}")
        logging.info(f"Task: \t{self.TASK}")
        logging.info(f"Session: \t{self.SESSION}")
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

        between_block_txt = "Number of remaining of blocks: {}.\n" \
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

        # all trials dataframe
        df = self.exp_dataframe()

        # ============================================================
        #                          Run
        # ============================================================
        # draw beginning message
        begin_msg.draw()
        self.window.mouseVisible = False
        self.window.flip()
        event.waitKeys(keyList=["space"])
        logging.info(f"EXPERIMENT STARTED AT: \t{self.global_clock.getTime()}")

        # loop blocks
        for block in df.block.unique():

            # show block message
            between_block_msg.text = between_block_txt.format(5 - block)  # TODO: set in init
            between_block_msg.draw()
            self.window.flip()
            event.waitKeys(keyList=["space"])

            # calibrate the eye tracker
            tracker.calibrate()

            # log beginning of the block
            block_clock.reset()
            logging.info(f"BLOCK {block} STARTED AT: \t{self.global_clock.getTime()}")

            # loop trials
            for idx, trial in df[df["block"] == block].iterrows():

                bad_trial = False  # quit the trial if this is set to True anywhere
                trial_frames = self.make_trial_frames(trial)  # get frame sequence
                self.window.recordFrameIntervals = True  # start recording flips

                # drift correction
                checked = False
                while not checked:
                    fips_frame.fixation.draw()
                    self.window.flip()
                    checked = tracker.drift_correction()

                # start eye tracking
                tracker.start_recording()
                tracker.status_msg(f"block {block} trial {trial['trial_n']}")
                tracker.log(f"start_trial {trial['trial_n']} task {trial['task']} frame_speed {trial['frame_speed']} target_pos {trial['target_pos']}")

                # start the trial
                for fr in range(int(trial_frames["total"])):

                    # 1) FIXATION PERIOD: fixation appears
                    if fr in trial_frames["fixation"]:

                        # log on one of the frames
                        if fr == trial_frames["fixation"][1]:
                            tracker.log("fixation")
                        fips_frame.fixation.draw()
                        , tracker.wait_for_fixation_start()

                    # 2) STABILIZATION PERIOD
                    elif fr in trial_frames["stabilize"]:

                        fips_frame.move_frame(fr, trial_frames["stabilize"])

                        stim.fixation.draw()
                        if stim.fixation.contains(gaze_pos):
                            fix_ok = True
                        else:
                            bad_trials.append(trial)
                            try:
                                block.next()
                            except StopIteration:
                                print("End of Block")

                    # 3) CUE PERIOD
                    elif fr in trial_frames["cue"]:
                        if crit_region.contains(gaze_pos):
                            stim.move_frame(fr, saccade_seq)

                    # 4) SACCADE PERIOD
                    elif fr in trial_frames["saccade"]:


            self.window.recordFrameIntervals = False

        tracker.setConnectionState(False)
        df.to_csv(str(self.run_file))
        self.window.close()
        core.quit()

    def exp_dataframe(self):
        """

        Returns
        -------

        """
        columns = [
            "sub", "block", "task", "frame_speed", "target_pos", "cue_delay", "saccade_pos", "saccade_latency",
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
        trial_idx = np.tile(list(range(1, n_trials + 1)), reps=4)

        # going over blocks
        for block in range(n_blocks):

            block_df = pd.DataFrame(columns=columns)  # so we can shuffle the trials at the end

            # making trials inside the block
            for trial in range(trials_per_cond):
                for speed in speeds:
                    for target in target_pos:
                        row = [
                            self.SUBJECT, block + 1, "saccade", speed, target, np.random.choice(cue_oscs), np.nan,
                            np.nan, np.nan
                        ]
                        block_df = block_df.append(pd.DataFrame([row], columns=columns), ignore_index=True)

            block_df = block_df.iloc[np.random.permutation(len(block_df))].reset_index(drop=True)
            block_df["trial_n"] = list(range(1, n_trials + 1))

            df = df.append(block_df, ignore_index=True)

        return df

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
        v_frame = deg2pix(degrees=trial["frame_speed"], monitor=self.monitor) / self.refresh_rate

        # convert timing from ms to number of frames
        flash_dur = self.ms2frame(self.flash_dur)
        saccade_dur = self.ms2frame(self.saccade_dur)

        # velocity of the frame is in pixel/frame
        # since the motion cycle is for a full path + 2 flashes at the end points, the velocity of the frame will be
        # for half a path - one flash duration
        path_duration = path_length * (1/v_frame)
        motion_cycle = (path_duration + flash_dur) * 2
        fix_dur = np.random.uniform(400, 600)

        # durations of a given trial in frames
        trial_durs = np.asarray([
            fix_dur,  # fixation period is a variable duration to establish fixation
            self.n_stabilize * motion_cycle,  # stabilization period is a number of oscillation to stabilize
            self.ms2frame(trial["cue_delay"]) * motion_cycle,  # number of oscillations before color change
            saccade_dur  # the maximum amount of time for executing a saccade and finishing the trial
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

            # check cue period
            elif trial_durs[1] <= n_frame < trial_durs[2]:
                cue_frames.append(n_frame)

            # check saccade period
            else:
                saccade_frames.append(n_frame)

            # go to next frame
            n_frame += 1

        trial_frames = {
            'fixation': fixation_frames, 'stabilize': stabilization_frames, 'cue': cue_frames,
            'saccade': saccade_frames, 'total': n_total_frames
        }

        return trial_frames

    def ms2frame(self, duration):
        return self.refresh_rate * duration / 1000
