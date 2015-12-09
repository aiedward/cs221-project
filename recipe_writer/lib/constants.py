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
DEFAULT_EXE_CHOICE = None

##
# Function: init
# -------------------
# Because of some weird bug with __file and absolute vs. relative paths,
# constants.py must have a separate function to actually configure the
# global constants, using a path_to_root variable fed to it by __main__.py.
#
# Example path_to_root on my computer:
#   "/Users/austin_ray/GitHub/cs221-project/recipe_writer"
##
def init(pathToRoot):
	constantsModule = sys.modules[__name__]

	# This is the absolute path of the recipe_writer folder on your computer.
	constantsModule.PATH_TO_ROOT = pathToRoot

	# The full paths of the folders holding various important things
	constantsModule.PATH_TO_RESOURCES = os.path.join(PATH_TO_ROOT, "res")
	constantsModule.PATH_TO_EXECUTABLES = os.path.join(PATH_TO_ROOT, "bin")
	constantsModule.PATH_TO_LIBRARIES = os.path.join(PATH_TO_ROOT, "lib")

	# Used by:
	#  - bin/query_online_db.py (using lib/database.py functions) to write recipe 
	#    data to a JSON file.
	#  - bin/process_recipes.py to read recipe data from that very same file.
	constantsModule.FILENAME_JSON_RECIPES = "allRecipes.json"

	# Used by:
	#  - bin/process_recipes.py to write alias data to a JSON file.
	#  - bin/write_recipes.py to extract that very same data.
	constantsModule.PATH_TO_ALIASDATA = os.path.join(PATH_TO_RESOURCES, "aliasdata")

	# Used by:
	#  - main.py to direct execution to the proper executable in bin/
	constantsModule.EXECUTABLES = ["process_recipes", "query_online_db", "write_recipes"]
	constantsModule.EXE_ARG_POS = 1