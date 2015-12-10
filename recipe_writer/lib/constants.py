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
YUM_APP_ID = None
YUM_APP_KEY = None
YUM_STEP = None
YUM_ALLOWED_COURSE = None
PRINT_RECIPE_IN_DATABASE = None
GOV_NUT_API_KEY = None
GOV_NUT_API_KEY_1 = None
GOV_NUT_API_KEY_2 = None
GOV_NUT_API_KEY_3 = None
GOV_NUT_API_KEY_4 = None
SLEEP_THRESHOLD = None
SLEEP_TIME = None
PRINT_REMAINING_CALLS = None
PRINT_MISSED_INGREDIENTS = None


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
	global PATH_TO_ROOT
	global PATH_TO_RESOURCES
	global PATH_TO_EXECUTABLES
	global PATH_TO_LIBRARIES
	global FILENAME_JSON_RECIPES
	global PATH_TO_ALIASDATA
	global EXECUTABLES
	global EXE_ARG_POS
	global DEFAULT_EXE_CHOICE
	global YUM_APP_ID
	global YUM_APP_KEY
	global YUM_STEP
	global YUM_ALLOWED_COURSE
	global PRINT_RECIPE_IN_DATABASE
	global GOV_NUT_API_KEY
	global GOV_NUT_API_KEY_1
	global GOV_NUT_API_KEY_2
	global GOV_NUT_API_KEY_3
	global GOV_NUT_API_KEY_4
	global SLEEP_THRESHOLD
	global SLEEP_TIME
	global PRINT_REMAINING_CALLS
	global PRINT_MISSED_INGREDIENTS

	# This is the absolute path of the recipe_writer folder on your computer.
	PATH_TO_ROOT = pathToRoot

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
	EXECUTABLES = ["process_recipes", "query_online_db", "write_recipes", "sandbox", "merge_recipes"]
	EXE_ARG_POS = 1

	##
	# The below constants are used by database.py.
	##

	# Yummly API constants
	YUM_APP_ID = "4d1d7424"
	YUM_APP_KEY = "419a5ef2649eb3b6e359b7a9de93e905"
	YUM_STEP = 100
	YUM_ALLOWED_COURSE = "course^course-Main Dishes"
	PRINT_RECIPE_IN_DATABASE = False

	# Goverment Nutritional Database API constants
	GOV_NUT_API_KEY = "5YbfzajkZSaGWi7hibcD4Nq1EXSGHRtZP5Pvlkvv"
	GOV_NUT_API_KEY_1 = "svYYehDakYftfY9OsNtQuE30yFNotcWrb2db8MzH"
	GOV_NUT_API_KEY_2 = "e8AUBbuo2cPNt5nXONZ7ZHZrizZsoeLuAxonNA9z"
	GOV_NUT_API_KEY_3 = "IcpbZjpGGe81PQW0ruxgzwWe3lSEuqAKeG1N8UqV"
	GOV_NUT_API_KEY_4 = "6NxAEpCnVr3oCRAffO2DhDpcMrcTmGrBCgdtJX8q"
	SLEEP_THRESHOLD = 1
	SLEEP_TIME = 60*30
	PRINT_REMAINING_CALLS = False
	PRINT_MISSED_INGREDIENTS = False


def setDatabasePrintConstants(recipesInDatabase, remainingCalls, missedIngredients, apiNum):
	global PRINT_RECIPE_IN_DATABASE
	global PRINT_REMAINING_CALLS
	global PRINT_MISSED_INGREDIENTS
	global GOV_NUT_API_KEY
	global startNumber
	PRINT_RECIPE_IN_DATABASE = recipesInDatabase
	PRINT_REMAINING_CALLS = remainingCalls
	PRINT_MISSED_INGREDIENTS = missedIngredients
	GOV_NUT_API_KEY = govAPIArray[apiNum]