import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
import thread

from lib import util, kmeans, search, csp
from lib import constants as c
# c.init(os.path.dirname(os.path.dirname(__file__)))



##
# Function: main
# --------------
# Second argument expected to be alias data file that we will import from.
##
def main(argv):
	print "In write_recipes.py, c.PATH_TO_ROOT: ", c.PATH_TO_ROOT
	argd = processArgs(argv)

	results = runModule(argd)

	if argd["verbose"]:
		print results

##
# Function: processArgs
# ---------------------
# Pretty self-explanatory.
#
# Possible options include:
#    --module=
#    --verbose=
#
# By default, the module is set to None, verbose is set to True, and
# args is set to an empty list. Module being None actually means all
# modules' run() functions will be called. Verbose being True means
# status updates will be printed. Verbose is included as the first
# arguments in the args list to any module's run() function.
##
def processArgs(argv):
	argd = {"module": None, "verbose": True, "args": []}
	realArgs = argv[1:]

	for arg in realArgs:
		if "module=" in arg:
			argd["module"] = arg.split("=")[-1]
		elif "verbose=" in arg:
			argd["verbose"] = (arg.split("=")[-1].lower() == "true")
		else:
			argd["args"].append(arg)

	return argd

##
# Function: runModule
# -------------------
# Calls the run(args) function for the specified module. The module's run(..)
# function is like a main() function but it receives somewhat cleaned-up
# command-line arguments and is expected to return a value. The first
# argument to a run() function will always be verbose, which will be True
# or False to indicate whether progress updates should be printed as the
# module chugs along.
##
def runModule(argd):
	results = None
	moduleName = argd["module"]
	moduleArgs = tuple([argd["verbose"]] + argd["args"])

	if argd["verbose"]:
		print "\nExecuting %s.run%r\n" % (moduleName, moduleArgs)

	if moduleName == "csp":
		results = csp.run(*moduleArgs)
	elif moduleName == "kmeans":
		results = kmeans.run(*moduleArgs)
	elif moduleName == "search":
		results = search.run(*moduleArgs)
	elif moduleName == None:
		results = [kmeans.run(*moduleArgs), 
			search.run(*moduleArgs), 
			csp.run(*moduleArgs)]
	return results


# If called from command line, call the main() function
if __name__ == "__main__":
	main(sys.argv)