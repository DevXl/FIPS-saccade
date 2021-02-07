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
            size=None,
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

        self.frame = self._generate_frame()

    def _generate_frame(self):
        """
        Generates the square frame

        Returns
        -------

        """

        # corner coordinates
        top_left = (self.pos[0] - self.size/2, self.pos[1] + self.size/2)
        top_right = (self.pos[0] + self.size/2, self.pos[1] + self.size/2)
        bot_left = (self.pos[0] - self.size/2, self.pos[1] - self.size/2)
        bot_right = (self.pos[0] + self.size/2, self.pos[1] - self.size/2)

        frame = visual.ShapeStim(
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

        return frame

    def generate_probe(self, pos, color):
        """
        Makes the probe that is supposed to flash inside the frame

        Returns
        -------
        """
        probe = visual.GratingStim(
            win=self.win,
            mask='circle',
            size=.8,
            phase = 0,
            pos=pos,
            sf=0,
            ori=0,
            contrast=1,
            color=color
        )
        return probe

    def move_frame(self, scr_frames, direction):
        """
        Oscillates the frame

        Parameters
        ----------
        scr_frames : int
            Number of screen frames the stimulus should move for

        direction : str
            "up", "down", "left", or "right"
        """
        # velocity is given degrees/frame
        for sf in range(scr_frames):
            if direction == "left":
                self.frame.pos -= (0, self.velocity)
            elif direction == 'right':
                self.frame.pos += (0, self.velocity)
            elif direction == "up":
                self.frame.pos += (self.velocity, 0)
            elif direction == "down":
                self.frame.pos -= (self.velocity, 0)
            else:
                raise ValueError("Direction should be one of 'up', 'down', 'left', or 'right'.")

            self.frame.draw()
