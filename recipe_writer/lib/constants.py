import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
import thread

PATH_TO_ROOT = None
PATH_TO_RESOURCES = None
PATH_TO_EXECUTABLES = None
PATH_TO_LIBRARIES = None
FILENAME_JSON_RECIPES = None
PATH_TO_ALIASDATA = None
EXECUTABLES = None
EXE_ARG_POS = None

##
# Function: configure
# -------------------
# Because of some weird bug with __file and absolute vs. relative paths,
# constants.py must have a separate function to actually configure the
# global constants, using a path_to_root variable fed to it by __main__.py.
#
# Example path_to_root on my computer:
#   "/Users/austin_ray/GitHub/cs221-project/recipe_writer"
##
def configure(path_to_root):
	# This is the absolute path of the recipe_writer folder on your computer.
	PATH_TO_ROOT = path_to_root

	# The full paths of the folders holding various important things
	PATH_TO_RESOURCES = os.path.join(PATH_TO_ROOT, "res")
	PATH_TO_EXECUTABLES = os.path.join(PATH_TO_ROOT, "bin")
	PATH_TO_LIBRARIES = os.path.join(PATH_TO_ROOT, "lib")

	# Used by:
	#  - bin/query_online_db.py (using lib/database.py functions) to write recipe 
	#    data to a JSON file.
	#  - bin/process_recipes.py to read recipe data from that very same file.
	FILENAME_JSON_RECIPES = "allRecipes.json"

	# Used by:
	#  - bin/process_recipes.py to write alias data to a JSON file.
	#  - bin/write_recipes.py to extract that very same data.
	PATH_TO_ALIASDATA = os.path.join(PATH_TO_RESOURCES, "aliasdata")

	# Used by:
	#  - main.py to direct execution to the proper executable in bin/
	EXECUTABLES = ["process_recipes", "query_online_db", "write_recipes"]
	EXE_ARG_POS = 1