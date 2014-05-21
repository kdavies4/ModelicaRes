#!/usr/bin/python

from modelicares import util

ax = fig.add_subplot(111, autoscale_on=False)
t = [-1,2]
s = [0,-1]
line = util.ArrowLine(t, s, color='b', ls='-', lw=2, arrow='>',
                      arrowsize=20)
ax.add_line(line)
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
