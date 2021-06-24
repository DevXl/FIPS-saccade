#!usr/bin/env python
"""
Helper functions for FIPS experiments
"""


def setup_path(sub, root, task):
    """
    Sets up paths and directories for experiment

    Parameters
    ----------
    sub : int
    root : Pathlib object
        points to the root directory of the experiment
    task : str
    """
    # data directory
    data_dir = root / "data"
    if not data_dir.exists():
        print("Making the data directory...")
        data_dir.mkdir()

    # subject directory
    sub_id = f"{sub:02d}"
    sub_dir = data_dir / f"sub-{sub_id}"
    if not sub_dir.exists():
        print("Making the subject directory...")
        sub_dir.mkdir()

    # task directory
    task_dir = sub_dir / task
    if not task_dir.exists():
        print("Making the task directory...")
        task_dir.mkdir()

    return task_dir


def get_monitors(mon_name):
    """
    Has all the monitors with their specs and returns the one with the specified name.

    Parameters
    ----------
    mon_name : str
        name of the requested monitor

    Returns
    -------
    dict
    """
    test_monitors = {
        "lab": {
            "size_cm": (54, 0),
            "size_px": (1280, 720),
            "dist": 65,
            "refresh_rate": 120
        },
        "OLED": {
            "size_cm": (73, 33),
            "size_px": (1920, 1080),
            "dist": 60,
            "refresh_rate": 60
        },
        "raz3rblade": {
            "size_cm": (38, 20),
            "size_px": (2560, 1440),
            "dist": 30,
            "refresh_rate": 60
        },
        "ryan": {
            "size_cm": (0, 0),
            "size_px": (0, 0),
            "dist": 60,
            "refresh_rate": 60
        }
    }

    return test_monitors[mon_name]


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

        # move left
        elif cycle_dur/4 < frameN < cycle_dur * 3 / 4:
            frame.pos -= [speed, 0]
            # flash
            if (cycle_dur * 3/4) - flash_dur < frameN < (cycle_dur * 3/4):
                probes[1].draw()

        # move right again
        else:
            frame.pos += [speed, 0]

        # show everything
        window.flip()