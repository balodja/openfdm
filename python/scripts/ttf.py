#!/usr/bin/env python
# generate time till failure plot
import os
import sys
import inspect
import path_append
import OpenFDM
from OMPython import OMShell, get
from DyMat import DyMatFile

# plotting
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import numpy as np

root_path = os.path.abspath(os.path.join(
  inspect.getfile(inspect.currentframe()),
  os.path.pardir, os.path.pardir))

shell = OMShell(root_path, echo=True)
for item in shell.executeMultiLine(
"""
  loadModel(Modelica);
  loadModel(OpenFDM);
  loadModel(test);
"""):
    print " ", item

result = shell.execute("simulate(test.Rocket,stopTime=100,numberOfIntervals=10000)")
resultFile = get(result, "SimulationResults.resultFile")[1:-1]
resultFile = os.path.splitext(resultFile)[0]

matFile = DyMatFile(resultFile)
time = matFile.abscissa('p.r_r[1]', valuesOnly=True)
print "time end", time[-1]
x = matFile.data('p.r_r[1]')
y = matFile.data('p.r_r[2]')
agl = matFile.data('p.agl')

formatter = EngFormatter(unit='m', places=1)

fig1 = plt.figure()
a1 = fig1.add_subplot(111)
a1.set_title('trajectory of Rocket')
a1.set_xlabel('x')
a1.set_ylabel('agl')
a1.xaxis.set_major_formatter(formatter)
a1.yaxis.set_major_formatter(formatter)
a1.plot(x, agl)
a1.grid()

fig2 = plt.figure()
a2 = fig2.add_subplot(111, projection='3d')
a2.set_title('trajectory of Rocket')
a2.set_xlabel('x')
a2.set_ylabel('y')
a2.set_zlabel('agl')
a2.xaxis.set_major_formatter(formatter)
a2.yaxis.set_major_formatter(formatter)
a2.zaxis.set_major_formatter(formatter)
a2.plot(x, y, agl)
a2.grid()

plt.show()

# vim:ts=2:sw=2:expandtab: