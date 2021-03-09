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
            speed=1,
            refresh_rate=60,
            flash_frames=5,
            name=None,
    ):

        self.win = win
        self.pos = pos
        self.size = size
        self.ori = ori
        self.path_length = path_length
        self.refresh_rate = refresh_rate
        self.flash_frames = flash_frames
        self.name = name
        self._speed = speed

        # we want the flashes inside the frame
        if self.path_length >= self.size:
            raise ValueError("Path length should be smaller than frame length.")
        
        self.contrast = 1.0
        self.opacity = 1.0
        self.color = (-1, -1, -1)

        self._fixation = None
        self._probes = None
        self._frame = None
        self._motion_seq = None

        self.move_dur = self.path_length * (1/self.speed) * self.refresh_rate
        self.total_cycle_frames = (self.move_dur + self.flash_frames) * 2
        self.init_pos = (-self.path_length/2, self.pos[1])

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, val):
        self._speed = val

    @property
    def fixation(self):
        """
        Makes the fixation dot. 
        """
        if self._fixation is None:

            self._fixation = visual.Circle(
                win=self.win,
                size=self.size/20,
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

    def move_frame(self, scr_frame, sequence):
        """
        Oscillates the frame

        Parameters
        ----------
        scr_frame : int

        sequence : dict

        Returns
        -------
        None
        """
        # assuming the position of the frame is always directly above fixation
        if scr_frame in sequence["right"]:
            self.frame.pos += (self.speed, 0)
            self.frame.draw()
        elif scr_frame in sequence["left"]:
            self.frame.pos -= (self.speed, 0)
            self.frame.draw()
        elif scr_frame in sequence["flash"]:
            self.probes["top"].draw()
            self.probes["bot"].draw()

# =================================================================
#                   Some utility functions
# =================================================================
def make_motion_seq(path_dur, flash_dur, n_repeat, total_cycle):
    """
    Makes a sequence of indexes for different stages of the frame motion

    Parameters
    ----------
    path_dur
    flash_dur
    n_repeat
    total_cycle

    Returns
    -------

    """

    # sections
    move_right_frames = [i for i in range(path_dur)]
    flash_right_frames = [i for i in range(path_dur, path_dur + flash_dur)]
    move_left_frames = [i for i in range(flash_right_frames[-1] + 1, flash_right_frames[-1] + path_dur)]
    flash_left_frames = [i for i in range(move_left_frames[-1] + 1, move_right_frames[-1] + flash_dur)]

    def get_all_frames(frames):
        return [fr + (tr * total_cycle) for fr in frames for tr in range(n_repeat)]

    all_right_frames = get_all_frames(move_right_frames)
    all_left_frames = get_all_frames(move_left_frames)
    all_flash_frames = get_all_frames((flash_left_frames + flash_right_frames))

    motion_seq = {"right": all_right_frames, "left": all_left_frames, "flash": all_flash_frames}

    return motion_seq
