#!usr/bin/env python
"""
Created at 1/20/21
@author: devxl

Moving frame and the target(s) inside it
"""
from psychopy import visual


class FIPS:
    """
    Moving frames that induce position shift in the targets they envelope
    """

    def __init__(
            self,
            win,
            pos=(0.0, 0.0),
            size=10,
            ori=0.0,
            path_length=5,
            velocity=1,
            refresh_rate=60,
            flash_frames=5,
            name=None,
    ):

        self.win = win
        self.pos = pos
        self.size = size
        self.ori = ori
        self.path_length = path_length
        self.velocity = velocity
        self.refresh_rate = refresh_rate
        self.flash_frames = flash_frames
        self.name = name

        # we want the flashes inside the frame
        if self.path_length >= self.size:
            raise ValueError("Path length should be smaller than frame length.")
        
        self.contrast = 1.0
        self.opacity = 1.0
        self.color = (-1, -1, -1)

        self._fixation = None
        self._probes = None
        self._frame = None

        self.move_dur = self.path_length * (1/self.velocity) * self.refresh_rate
        self.total_cycle_frames = (self.move_dur + self.flash_frames) * 2
        self.init_pos = (-self.path_length/2, self.pos[1])


    @property
    def fixation(self):
        """
        Makes the fixation dot. 
        """
        if self._fixation is None:

            self._fixation = visual.Circle(
                win=self.win,
                size=self.size/10,
                fillColor=(-1, -1, -1),
                lineColor=(-1, -1, -1),
                pos=(0, 0)
            )
        
        return self._fixation

    @property
    def frame(self):
        """
        Generates the square frame

        Returns
        -------

        """
        if self._frame is None:

            # corner coordinates
            top_left = (self.pos[0] - self.size/2, self.pos[1] + self.size/2)
            top_right = (self.pos[0] + self.size/2, self.pos[1] + self.size/2)
            bot_left = (self.pos[0] - self.size/2, self.pos[1] - self.size/2)
            bot_right = (self.pos[0] + self.size/2, self.pos[1] - self.size/2)

            self._frame = visual.ShapeStim(
                    win=self.win,
                    lineWidth=5,
                    lineColor=self.color,
                    lineColorSpace='rgb',
                    fillColor=None,
                    fillColorSpace='rgb',
                    vertices=[top_left, top_right, bot_left, bot_right],
                    windingRule=None,
                    closeShape=True,
                    pos=self.pos,
                    size=self.size,
                    ori=self.ori,
                    opacity=self.opacity,
                    contrast=self.contrast,
                    depth=0,
                    interpolate=True,
                    name=self.name,
                    autoLog=False,
                    autoDraw=False
            )

        return self._frame

    @property
    def probes(self):
        """
        Makes the probes that are supposed to flash inside the frame

        Returns
        -------
        """
        if self._probes is None:
            self._probes = dict()
            top_pos = self.pos[1] + self.size/6 + self.size/12
            bot_pos = (self.pos[1] - self.size/2) + self.size/6 + self.size/12
            radius = self.size/6

            self._probes["top"] = visual.GratingStim(
                win=self.win,
                mask='circle',
                size=radius,
                phase = 0,
                pos=top_pos,
                sf=0,
                ori=0,
                contrast=self.contrast*.8,  # contrast 80% of the frame
                color='blue'
            )

            self._probes["bot"] = visual.GratingStim(
                win=self.win,
                mask='circle',
                size=radius,
                phase = 0,
                pos=bot_pos,
                sf=0,
                ori=0,
                contrast=self.contrast*.8,  # contrast 80% of the frame
                color='red'
            )

        return self._probes

    def move_frame(self, n_frames, direction):
        """
        Oscillates the frame

        Parameters
        ----------
        mon_rf : int

        direction : str

        Returns
        -------
        None
        """
        # assuming the position of the frame is always directly above fixation
        assert direction in ['left', 'right']

        if direction == 'right':
            init_pos = (-self.path_length/2, self.pos[1])
        else:
            init_pos = (self.path_length/2, self.pos[1])
        self.frame.pos = init_pos

        # draw deg/frame motion
        for _ in range(n_frames):
            if direction == 'right':
                self.frame.pos += (self.velocity, 0)
            else:
                self.frame.pos -= (self.velocity, 0)

            self.frame.draw()
            self.win.flip()

    def flash_probes(self, n_frames):
        """
        """
        for _ in range(n_frames):
            self.probes["top"].draw()
            self.probes["bot"].draw()
            self.win.flip()

    def stabilize_period(self, n_stabilize, tracker):
        """

        Parameters
        ----------
        path_length
        n_frames
        n_stabilize
        mon_rf
        tracker

        Returns
        -------

        """
        bad_trial = False
        feedback = ""

        # starting position
        self.frame.pos = self.init_pos

        # sections in frame durations
        move_right_frames = [i for i in range(self.move_dur)]
        flash_right_frames = [i for i in range(self.move_dur, self.move_dur + self.flash_frames)]
        move_left_frames = [i for i in range(flash_right_frames[-1]+1, flash_right_frames[-1] + self.move_dur)]
        flash_left_frames = [i for i in range(move_left_frames[-1]+1, move_right_frames[-1] + self.flash_frames)]

        def get_all_frames(frames):
            return [fr + (tr * self.total_cycle_frames) for fr in frames for tr in range(n_stabilize)]

        all_right_frames = get_all_frames(move_right_frames)
        all_left_frames = get_all_frames(move_left_frames)
        all_flash_frames = get_all_frames((flash_left_frames + flash_right_frames))

        for scr_frame in range(int(self.total_cycle_frames * n_stabilize)):

            # check fixation every frame
            # get eye position
            gaze_pos = tracker.getLastGazePosition()

            # check if it's valid
            valid_gaze_pos = isinstance(gaze_pos, (tuple, list))

            # run the procedure while fixating
            if valid_gaze_pos:
                if self.fixation.contains(gaze_pos):

                    if scr_frame in all_right_frames:
                        self.frame.pos += (self.velocity, 0)
                        self.frame.draw()
                    elif scr_frame in all_left_frames:
                        self.frame.pos -= (self.velocity, 0)
                        self.frame.draw()
                    elif scr_frame in all_flash_frames:
                        self.probes["top"].draw()
                        self.probes["bot"].draw()
                    
                    self.win.flip()
                else:
                    feedback = "Bad fixation."
                    bad_trial = True
            else:
                feedback = "Run calibration procedure."
                bad_trial = True

        return bad_trial, feedback

    def cue_period(self, duration, tracker):
        """
        
        """
        # starting position
        self.frame.pos = self.init_pos

        n_frames = duration * self.refresh_rate

        if n_frames < self.move_dur:
            self.move_frame(n_frames, "right")
        else:
            left_frames = n_frames - self.move_dur
            self.move_frame(self.move_dur, "right")
            self.move_frame(left_frames, "left")
