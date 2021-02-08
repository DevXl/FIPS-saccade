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
            color=(0.0, 0.0, 0.0),
            contrast=1.0,
            opacity=1.0,
            name=None,
            velocity=1.0
    ):

        self.win = win
        self.pos = pos
        self.size = size
        self.ori = ori
        self.color = color
        self.contrast = contrast
        self.opacity = opacity
        self.name = name
        self.velocity = velocity
        self._probes = None
        self._frame = None

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

            fr = visual.ShapeStim(
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

        return fr

    @property
    def probes(self):
        """
        Makes the probes that are supposed to flash inside the frame

        Returns
        -------
        """
        probes = dict()
        top_pos = self.pos[1] + self.size/6 + self.size/12
        bot_pos = (self.pos[1] - self.size/2) + self.size/6 + self.size/12
        radius = self.size/6

        probes["top"] = visual.GratingStim(
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

        probes["bot"] = visual.GratingStim(
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

        return probes

    def move_frame(self, scr_frames, direction, transitions):
        """
        Oscillates the frame

        Parameters
        ----------
        scr_frames : int
            Number of screen frames the stimulus should move for

        direction : str
            "up", "down", "left", or "right"
        """
        # velocity is given in degrees/frame
        flash_frames = 5
        
        for tr in transitions:
            for sf in range(scr_frames):
                if direction == "left":
                    self.frame.pos -= (self.velocity, 0)
                elif direction == 'right':
                    self.frame.pos += (self.velocity, 0)
                elif direction == "up":
                    self.frame.pos += (0, self.velocity)
                elif direction == "down":
                    self.frame.pos -= (0, self.velocity)
                else:
                    raise ValueError("Direction should be one of 'up', 'down', 'left', or 'right'.")

                self.frame.draw()



    def flash_probe(self):
        pass