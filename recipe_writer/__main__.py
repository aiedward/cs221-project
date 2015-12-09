import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
import thread

# Import constants defined in "./lib/constants.py"
from lib import constants

## 
# NOTE TO BRUNO/ALEX
# ------------------
# Change this string constant to choose what program to run.
# Try "process_recipes", "query_online_db", or "write_recipes"
##
DEFAULT_EXE_CHOICE = "process_recipes"

##
# main
# ----
# argv = ["main.py", <executable>, <args..>]
# <executable> is one of: "process_recipes", "query_online_db", "write_recipes"
def main(argv):
	exe_name = argv[constants.EXE_ARG_POS]
	exe = importlib.import_module("." + exe_name, "bin")
	new_argv = [exe_name + ".py"] + argv[constants.EXE_ARG_POS+1:]

	exe.main(new_argv)



if __name__ == "__main__":
	path_to_root = os.path.dirname(__file__)
	constants.configure(path_to_root)
	print "In recipe_writer/main.py ..."
	print "   sys.argv: ", sys.argv
	print "   sys.path: ", sys.path
	print "   __file__: ", __file__
	print "   PATH_TO_ROOT: ", constants.PATH_TO_ROOT

	argv = sys.argv

	# If no executable was provided, use the default
	if len(argv) < constants.EXE_ARG_POS+1:
		argv.append(constants.DEFAULT_EXE_CHOICE)

	# If an executable was provided that doesn't exist, use the default
	elif argv[constants.EXE_ARG_POS] not in constants.EXECUTABLES:
		argv[constants.EXE_ARG_POS] = constants.DEFAULT_EXE_CHOICE
	main(argv)
