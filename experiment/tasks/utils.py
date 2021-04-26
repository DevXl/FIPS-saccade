import numpy as np
import pyglet


def jitter(time: int, lag) -> float:
    """
    Adds or subtracts some jitter to a time period

    Parameters
    ----------
    time : float
    lag : float
        minimum/maximum amount of jitter

    Returns
    -------
    float
        modified duration
    """
    durations = np.linspace(-lag, lag, num=10)
    time += np.random.choice(durations, 1)

    return time/1000


def get_screens():
    """
    Use pyglet to find screens and their resolution

    Returns
    -------

    """

    pl = pyglet.canvas.get_display()
    screens = pl.get_screens()

    return screens
