#!usr/bin/env python
"""
Helper functions for FIPS experiments
"""


def move_frame(probes, frame, cycle_dur, speed, flash_dur, window):
    """
    Moves a frame for one motion cycle and flashes probes at the reversal points

    Parameters
    ----------
    probes : list
        containing two visual.Circle objects
    frame : visual.ShapeStim
    cycle_dur : int
        duration of motion cycle in frames
    speed : flaot
    flash_dur : int
        duration to show the probes
    window : visual.Window object

    """
    # check for only two probes (pointless!)
    assert len(probes) == 2

    # Move the stimulus
    for frameN in range(cycle_dur):

        # move right
        if frameN < cycle_dur / 4:
            frame.pos += [speed, 0]
            # flash
            if (cycle_dur/4) - flash_dur < frameN < cycle_dur:
                probes[0].draw()
                probes[1].draw()

        # move left
        elif cycle_dur/4 < frameN < cycle_dur * 3 / 4:
            frame.pos -= [speed, 0]
            # flash
            if (cycle_dur * 3/4) - flash_dur < frameN < (cycle_dur * 3/4):
                probes[0].draw()
                probes[1].draw()

        # move right again
        else:
            frame.pos += [speed, 0]

        # show everything
        window.flip()