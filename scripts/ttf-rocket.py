#!/usr/bin/env python
# generate time till failure plot
import os
import sys
import inspect

from openfdm_root import root

import pyopenfdm
from OMPython import OMShell, get
from DyMat import DyMatFile
import multiprocessing
import time
import math

# plotting
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import numpy as np

# input data setup
n = 4
motorXVals = np.linspace(-1,1,n)
motorAngleVals = np.linspace(0,1,n)
timeTillFailure = np.zeros((n,n))
val_dict = {
  'motorX': 0,
  'motorAngle': 0,
}

# modelica setup
options_dict = {
  'cpus' : multiprocessing.cpu_count()
}

# plot setup
formatter_m = EngFormatter(unit='m', places=1)
formatter_deg = EngFormatter(unit='deg', places=1)
if not os.path.isdir('fig'):
  os.mkdir('fig')

# initialize modelica
shell = OMShell(root, echo=True)
for item in shell.executeMultiLine(
"""
  setCommandLineOptions({{"+preOptModules=inlineArrayEqn,partitionIndependentBlocks",
    "+postOptModules=inlineArrayEqn,constantLinearSystem,removeSimpleEquations,generateSymbolicLinearization","+d=linearization,gendebugsymbols","+numProcs={cpus}"}});
  loadModel(Modelica);
  loadModel(OpenFDM);
  loadModel(test);
""".format(**options_dict)):
    print " ", item

# main loop
for motorXIndex in xrange(len(motorXVals)):

  val_dict['motorX'] = motorXVals[motorXIndex]

  for motorAngleIndex in xrange(len(motorAngleVals)):

    val_dict['motorAngle'] = motorAngleVals[motorAngleIndex]

    print shell.execute("""loadString("
      model Rocket
        import OpenFDM.*;
        inner World world;
        Parts.RigidReferencePoint p(
          wrapEuler=false,
          r_r(start={{0,0,-1}},fixed=true),
          euler(start={{0,1,0}},fixed=true));
        Parts.RigidBody structure(I_b=identity(3),m=0.1);
        Propulsion.SolidRocketMotor motor(
          mInert=0.1,
          mFuel=0.2,
          Ve=1000,
          mDot=1.0);
        Parts.RigidLink_B321 t(
          angles={{ {motorAngle}, {motorAngle}, {motorAngle} }},
          r_a={{ {motorX}, {motorX}, {motorX} }});
      equation
        connect(p.fA,structure.fA);
        connect(structure.fA,t.fA);
        connect(t.fB,motor.fA);
      end Rocket;
    ")""".format(**val_dict) )

    result = shell.execute("simulate(Rocket,stopTime=1,numberOfIntervals=1000)")
    resultFile = get(result, "SimulationResults.resultFile")[1:-1]
    resultFile = os.path.splitext(resultFile)[0]

    matFile = DyMatFile(resultFile)
    timeTillFailure[motorXIndex][motorAngleIndex] = matFile.abscissa('p.r_r[1]', valuesOnly=True)[-1]
    x = matFile.data('p.r_r[1]')
    y = matFile.data('p.r_r[2]')
    agl = matFile.data('p.agl')

    fig1 = plt.figure()
    a1 = fig1.add_subplot(111)
    a1.set_title('x: {motorX}, angle: {motorAngle}'.format(**val_dict))
    a1.set_xlabel('x')
    a1.set_ylabel('agl')
    a1.xaxis.set_major_formatter(formatter_m)
    a1.yaxis.set_major_formatter(formatter_m)
    a1.plot(x, agl)
    a1.grid()
    plt.savefig('fig/rocket-2d-{motorAngle}-{motorX}.pdf'.format(**val_dict))
    plt.close(fig1)


    fig2 = plt.figure()
    a2 = fig2.add_subplot(111, projection='3d')
    a2.set_title('x: {motorX}, angle: {motorAngle}'.format(**val_dict))
    a2.set_xlabel('x')
    a2.set_ylabel('y')
    a2.set_zlabel('agl')
    a2.xaxis.set_major_formatter(formatter_m)
    a2.yaxis.set_major_formatter(formatter_m)
    a2.zaxis.set_major_formatter(formatter_m)
    a2.plot(x, y, agl)
    a2.grid()
    plt.savefig('fig/rocket-3d-{motorAngle}-{motorX}.pdf'.format(**val_dict))
    plt.close(fig2)


fig3 = plt.figure()
a3 = fig3.add_subplot(111)
a3.set_title('time till failure')
a3.set_xlabel('motor x')
a3.set_ylabel('motor angle')
a3.xaxis.set_major_formatter(formatter_m)
a3.yaxis.set_major_formatter(formatter_deg)
plt.contourf(motorXVals,motorAngleVals*180/math.pi,timeTillFailure)
print "timeTillFailure:", timeTillFailure
a3.grid()
plt.savefig('fig/time-till-failure-{motorAngle}-{motorX}.pdf'.format(**val_dict))

plt.show()
plt.close(fig3)

# vim:ts=2:sw=2:expandtab:
