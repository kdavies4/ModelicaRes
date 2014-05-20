#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

from modelicares import util

# Create a plot.
x = np.arange(100)
y = np.sin(x/4.0)
plt.plot(x, y)
plt.ylim([-1.2, 1.2])

# Add horizontal lines and labels.
util.add_vlines(positions=[25, 50, 75], labels=["A", "B", "C"], color='k',
                ls='--')
