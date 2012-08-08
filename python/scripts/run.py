#!/usr/bin/env python
# helps automate calling scripts via python
import os
import sys
import path_append
import inspect
import OMPython

root_path = os.path.abspath(os.path.join(
  inspect.getfile(inspect.currentframe()),
  os.path.pardir,os.path.pardir))
curdir = os.path.abspath(os.path.curdir)

if len(sys.argv) == 2:
  shell = OMPython.OMShell(root_path,echo=True)
else:
  print "usage", sys.argv[0], "script", 
  sys.exit(1)

print shell.run_script(os.path.abspath(sys.argv[1]));

# vim:ts=2:sw=2:expandtab: