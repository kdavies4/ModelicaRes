#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

from modelicares import util

# Create a plot.
x = np.arange(100)
p = plt.plot(x, np.sin(x/4.0))

# Add arrows and annotations.
util.add_arrows(p[0], x_locs=x.take(np.arange(20,100,20)),
                label="Incr. time", xstar_offset=-0.15)
