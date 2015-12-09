import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
import thread

# Import Constants class defined in "./lib/constants.py"
# need to create a Constants object with an initialization
# argument that is the path of the folder __main__.py is in
# because of some weird command line thing
from lib import constants as c
c.init(os.path.dirname(__file__))

##
# Note to Bruno/Alex
# ------------------
# Change this variable to change which executable .py file you want to run
# if you do not want to specify that file name from the command line.
# Choices include "process_recipes", "query_online_db", "write_recipes"
##
DEFAULT_EXE_CHOICE = "process_recipes"

##
# Function: main
# --------------
# argv = ["main.py", <executable>, <args..>]
# <executable> is one of: "process_recipes", "query_online_db", "write_recipes"
def main(argv):
	exe_name = argv[c.EXE_ARG_POS]
	exe = importlib.import_module("." + exe_name, "bin")
	new_argv = [exe_name + ".py"] + argv[c.EXE_ARG_POS+1:]

	exe.main(new_argv)


if __name__ == "__main__":

	sys.path.append(c.PATH_TO_ROOT)

	argv = sys.argv

	# If no executable was provided, use the default
	if len(argv) < c.EXE_ARG_POS+1:
		argv.append(DEFAULT_EXE_CHOICE)

	# If an executable was provided that doesn't exist, use the default
	elif argv[c.EXE_ARG_POS] not in c.EXECUTABLES:
		argv[c.EXE_ARG_POS] = DEFAULT_EXE_CHOICE

	main(argv)
