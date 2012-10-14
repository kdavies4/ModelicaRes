#!/usr/bin/env python
"""Demo of ArrowLine: a matplotlib subclass to draw an arrowhead on a line
"""
__copyright__ = "Copyright (C) 2008 Jason Grout <jason-sage@...>"
__license__ = "modified BSD License"
# From http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html,
# accessed 2010/11/12

from arrow_line import ArrowLine
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111, autoscale_on=False)
t = [-1,2]
s = [0,-1]
line = ArrowLine(t, s, color='b', ls='-', lw=2, arrow='>', arrowsize=20)
ax.add_line(line)
ax.set_xlim(-3,3)
ax.set_ylim(-3,3)
plt.show()
