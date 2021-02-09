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
            color=(-1, -1, -1),
            contrast=1.0,
            opacity=1.0,
            name=None,
    ):

        self.win = win
        self.pos = pos
        self.size = size
        self.ori = ori
        self.color = color
        self.contrast = contrast
        self.opacity = opacity
        self.name = name

        self._fixation = None
        self._probes = None
        self._frame = None

    @property
    def fixation(self):
        """
        Makes the fixation dot. 
        """
        if self._fixation is None:

            self._fixation = visual.Circle(
                win=self.win,
                size=.4,
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
                mask='circle',(0.0, 0.0, 0.0)
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

    def move_frame(self, path_length, velocity, display_rf, direction):
        """
        Oscillates the frame

        Parameters
        ----------
        scr_frames : int
            Number of screen frames the stimulus should move for
        """
        # we want the flashes inside the frame
        if path_length >= self.size:
            raise ValueError("Path length should be smaller than frame length.")

        # the frame has to turn off at the end points for the transients to flash
        flash_frames = 5

        # assuming the position of the frame is always directly above fixation
        assert direction in ['left', 'right']

        if direction == 'right':
            init_pos = (-path_length/2, self.pos[1])
        else:
            init_pos = (path_length/2, self.pos[1])
        self.frame.pos = init_pos

        # number of frames to draw
        path_frames = path_length * display_rf
        scr_frames = path_frames + flash_frames

        # draw deg/frame motion
        for fr in range(scr_frames):
            if fr < path_frames:

                if direction == 'right':
                    self.frame.pos += (velocity, 0)
                    self.frame.draw()
                else:
                    self.frame.pos -= (velocity, 0)
                    self.frame.draw()
            else:
                self.probes["top"].draw()
                self.probes["bot"].draw()
            
            self.win.flip()
