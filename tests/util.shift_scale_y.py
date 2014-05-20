#!/usr/bin/python

import numpy as np

from modelicares import util
from modelicares.texunit import number_label

# Generate some random data.
x = range(100)
y = np.cumsum(np.random.random(100) - 0.5)
y -= y.min()
y *= 1e-3
y += 1e3 # Small magnitude and large offset
ylabel = number_label('Velocity', 'mm/s')

# Plot the data.
ax = util.setup_subplots(2, 2, label='examples/shift_scale_y')[0]
for a in ax:
    a.plot(x, y)
    a.set_ylabel(ylabel)

# Shift and scale the axes.
ax[0].set_title('Original plot')
ax[1].set_title('After applying offset and factor')
util.shift_scale_y(ax[1])
