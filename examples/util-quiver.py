#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

from modelicares import util

x, y = np.meshgrid(np.arange(0, 2*np.pi, 0.2), np.arange(0, 2*np.pi, 0.2))
u = np.cos(x)
v = np.sin(y)
ax = plt.subplot(111)
util.quiver(ax, u, v)
