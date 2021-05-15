#!/usr/bin/env python
"""
Script to fit Weibull function to staircase data from perceptual task
"""
from psychopy.data import FitWeibull, FitLogistic
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# file params
sub = 0
ses = 0
run = 1

# load file
data_file = Path(__file__).resolve().parent.parent / "data" / f"sub-{sub:02d}" / "psycphys" / \
            f"sub-{sub}_ses-{ses}_run-{run}_task-FIPSPerceptual_staircase.npy"

stair_data = np.load(data_file).T

# fit
fit = FitLogistic(stair_data[0], stair_data[1])
print(fit.params)

# plot
x = np.linspace(-2, 1, 100)
y = fit.eval(x)
print(y)
plt.plot(x, y)
plt.show()