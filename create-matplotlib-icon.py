#!/usr/bin/env python
"""Make the matplotlib svg minimization icon.
"""
# From http://matplotlib.sourceforge.net/examples/pylab_examples/matplotlib_icon.html
# accessed 2011/10/4

import matplotlib
#matplotlib.use('Svg')
from pylab import rc, figure, plot, axes, axis, setp, gca, savefig, sin, arange, pi

rc('grid', ls='-', lw=2, color='k')
fig = figure(figsize=(1, 1), dpi=72)
axes([0.025, 0.025, 0.95, 0.95], axisbg='#bfd1d4')

t = arange(0, 2, 0.05)
s = sin(2*pi*t)
plot(t,s, linewidth=4, color="#ca7900")
axis([-.2, 2.2, -1.2, 1.2])

# grid(True)
setp(gca(), xticklabels=[], yticklabels=[])
savefig('../../images/matplotlib.svg', facecolor='0.75', format='svg')
