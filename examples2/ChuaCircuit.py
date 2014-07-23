#!/usr/bin/python
"""Example of SimRes.plot()
"""

# pylint: disable=I0011, C0103

from modelicares import SimRes

sim = SimRes('ChuaCircuit.mat')
sim.plot(ynames1='L.i', ylabel1="Current",
         ynames2='L.der(i)', ylabel2="Derivative of current",
         title="Chua circuit")
