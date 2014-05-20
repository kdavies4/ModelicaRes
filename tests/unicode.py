#!/usr/bin/python
"""Test that unicode characters are correctly loaded from a simulation results
file and printed in a plot.
"""

import matplotlib.pyplot as plt
from modelicares import SimRes, save

s = SimRes('unicode.mat')
s.plot('a', title="The y axis label should be $\Delta\Theta$", label='unicode')
save(['pdf'])
