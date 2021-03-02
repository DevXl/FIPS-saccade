#!usr/bin/env python
"""
Created at 3/1/21
@author: devxl

FIPS saccade experiment task classes
"""
from _base import BaseExperiment
from _fips import *

from psychopy import logging, core, data, visual, info, event
from psychopy.tools.monitorunittools import deg2pix
from pygaze import eyetracker, libtime, libscreen

import numpy as np
import pandas as pd


class Saccade(BaseExperiment):

    def __init__(self, title, task, session, subject, debug):
        super().__init__(title, task, session, subject, debug)

    def make_motion_seq(self):
        pass

    def make_trial_frames(self):
        pass

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

        # subject
        sub_params = self.get_sub_info()

        # Monitor and screen
        exp_mon = self.make_monitor(name="OLED", scr_num=0, width=0, dist=57)  # TODO: get the actual numbers

        # Eye tracker
        tracker = eyetracker.EyeTracker(self.window)

        # ============================================================
        #                          Stimulus
        # ============================================================
        stim_size = deg2pix(degrees=10, monitor=self.monitor)
        fips_stim = FIPS(win=self.window, size=stim_size, pos=[0, 3], name='ExperimentFrame')

        crit_region_size = deg2pix(degrees=2, monitor=self.monitor)
        crit_region = visual.Circle(win=self.window, lineColor=[0, 0, 0], radius=crit_region_size, autoLog=False)

        # messages
        begin_msg = visual.TextStim(win=self.window, text="Press any key to start.", autoLog=False)
        between_block_txt = "You just finished block {}. Number of remaining of blocks: {}.\nPress the spacebar to continue."
        between_block_msg = visual.TextStim(win=self.window, autoLog=False)
        fixation_msg = visual.TextStim(win=self.window, text="Fixate on the dot.", pos=[0, -200], autoLog=False)
        finish_msg = visual.TextStim(win=self.window, text="Thank you for participating!", autoLog=False)

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
                nReps=total_trials / n_blocks,
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
        path_length = deg2pix(degrees=8, monitor=self.monitor)  # the length of the path that frame moves
        display_rf = 60
        flash_dur = 250
        v_frame = path_length / (motion_cycle - 2 * flash_dur)
        saccade_dur = 600

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

            self.window.recordFrameIntervals = True
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

                stab_frames = [i for i in range(int(fixation_frames[-1]) + 1, int(trial_frames[1]))]
                stab_seq = make_motion_seq(
                    path_dur=int(path_length * (1 / v_frame) * display_rf / 1000),
                    flash_dur=int(flash_dur * display_rf / 1000),
                    n_repeat=n_stabilize + 1,  # +1 because of the cue period
                    total_cycle=motion_cycle * display_rf / 1000
                )

                cue_frames = [i for i in range(int(stab_frames[-1] + 1), int(trial_frames[2] + stab_frames[-1] + 1))]

                # print((stab_frames[-1]+1), (int(trial_frames[2]+stab_frames[-1]+1)))
                saccade_frames = [i for i in range(int(cue_frames[-1]) + 1, int(trial_frames[3] + cue_frames[-1]) + 1)]
                saccade_seq = make_motion_seq(
                    path_dur=int(path_length * (1 / v_frame) * display_rf / 1000),
                    flash_dur=int(flash_dur * display_rf / 1000),
                    n_repeat=1,
                    total_cycle=motion_cycle * display_rf / 1000
                )

                # detect fixation
                fixate = False
                fips_stim.fixation.autoDraw = True

                self.window.flip()

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
