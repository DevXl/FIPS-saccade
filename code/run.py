#!usr/bin/env python
"""
Created at 1/20/21
@author: devxl

Saccade FIPS experiment
"""


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
            color=(-1.0, -1.0, -1.0),
            contrast=1.0,
            opacity=1.0,
            name=None
    ):

        self.win = win
        self.pos = pos
        self.size = size
        self.ori = ori
        self.color=color
        self.contrast = contrast
        self.opacity = opacity
        self.name = name

    def _make_frame(self):
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


