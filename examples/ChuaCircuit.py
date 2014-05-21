#!/usr/bin/python

from modelicares import SimRes

sim = SimRes('ChuaCircuit.mat')
sim.plot(ynames1='L.i', ylabel1="Current",
         ynames2='L.der(i)', ylabel2="Derivative of current",
         title="Chua circuit")
