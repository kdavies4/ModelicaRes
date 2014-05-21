#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

from modelicares import util
from modelicares.texunit import number_label

# Generate some random data.
x = np.linspace(55478, 55486, 100) # Small range and large offset
xlabel = number_label('Time', 's')
y = np.cumsum(np.random.random(100) - 0.5)

# Plot the data.
ax = util.setup_subplots(2, 2)[0]
for a in ax:
    a.plot(x, y)
    a.set_xlabel(xlabel)

# Shift and scale the axes.
ax[0].set_title('Original plot')
ax[1].set_title('After applying offset and factor')
util.shift_scale_x(ax[1])
