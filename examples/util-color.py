#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

from modelicares import util

x, y = np.meshgrid(np.arange(0, 2*np.pi, 0.2), np.arange(0, 2*np.pi, 0.2))
c = np.cos(x) + np.sin(y)

fig = plt.figure()
ax = fig.add_subplot(111)
util.color(ax, c)
