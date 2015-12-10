import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
import thread

from lib import util, csp, kmeans, search
from lib import constants as c
# c.init(os.path.dirname(os.path.dirname(__file__)))



##
# Function: main
# --------------
# Second argument expected to be alias data file that we will import from.
##
def main(argv):
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
##
def processArgs(argv):
	argd = {"module": None, "verbose": True, "args": []}
	realArgs = argv[1:]

	for arg in realArgs:
		if arg.startswith("--module="):
			argd["module"] = arg.replace("--module=", "")
		elif arg.startswith("--verbose="):
			argd["verbose"] = arg.replace("--verbose=", "")
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
	moduleArgs = tuple([argd["verbose"]] + argd["args"]])
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