import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time
import tokenize, re, string
import json, unicodedata
import thread

from lib import constants as c
c.init(os.path.dirname(os.path.dirname(__file__)))

##
# Function: main
# --------------
# Second argument expected to be alias data file that we will import from.
##
def main(argv):
	# Create a dictionary relating to the arguments after parsing them.
	argd = processArgs(argv)

def processArgs(argv):
	argd = {}
	realArgs = argv[1:]
	for arg in realArgs:
		if arg.startswith("--data="):
			argd["data"] = sorted(os.listdir(c.PATH_TO_ALIASDATA))[-1]

# If called from command line, call the main() function
if __name__ == "__main__":
	main(sys.argv)