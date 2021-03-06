#!/usr/bin/python
"""Example of util.add_vlines()
"""

# pylint: disable=I0011, C0103, E1101, R0801

import numpy as np
import matplotlib.pyplot as plt

from modelicares import util

# Create a plot.
x = np.arange(100)
y = np.sin(x / 4.0)
plt.plot(x, y)
plt.ylim([-1.2, 1.2])

# Add horizontal lines and labels.
util.add_vlines(positions=[25, 50, 75], labels=["A", "B", "C"], color='k',
                ls='--')
