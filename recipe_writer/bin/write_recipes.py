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
	# argd = processArgs(argv)

	results = runModule(argv)

	fullJsonString = None
	with open(allRecipesFullFilePath, "r") as f:
		fullJsonString = f.read()



# ##
# # Function: processArgs
# # ---------------------
# # Pretty self-explanatory.
# #
# # Possible options include:
# #    --module=
# ##
# def processArgs(argv):
# 	argd = {}
# 	realArgs = argv[1:]
# 	for arg in realArgs:
# 		if arg.startswith("--module="):
# 			argd["module"] = arg.replace("--module=", "")
# 	return argd

##
# Function: runModule
# -------------------
#
##
def runModule(argv):
	results = None
	moduleName = argv[1]
	moduleArgs = argv[1:]
	if moduleName.endswith("csp"):
		results = csp.run(moduleArgs)
	elif moduleName.endswith("kmeans"):
		results = kmeans.run(moduleArgs)
	elif moduleName.endswith("search"):
		results = search.run(moduleArgs)
	else:
		results = [kmeans.run(moduleArgs), 
			search.run(moduleArgs), 
			csp.run(moduleArgs)]
	return results


# If called from command line, call the main() function
if __name__ == "__main__":
	main(sys.argv)