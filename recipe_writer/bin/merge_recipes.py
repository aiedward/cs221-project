##
# File: /bin/merge_recipes.py
# -----------------------------
# Merge JSON recipe data into one file.
##

import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
import thread

from lib import util
from lib import constants as c

def main(argv):
	pathToRecipes = os.path.join(c.PATH_TO_RESOURCES, "jsontests")

	# Get the full absolute file paths of all files in /res/jsonrecipes/
	# that end in ".json"
	jsonRecipes = util.listFilesWithSuffix(pathToRecipes, ".json")

	# Load all of these ".json" files into dictionaries and put all
	# these dictionaries in a list
	listOfJSONDicts = util.loadJSONDicts(jsonRecipes)

	# Merge recipes into one dictionary, deleting duplicates
	mergedDict = util.naivelyMergeDicts(listOfJSONDicts)

	# Write the merged recipe dictionary to a file
	allRecipesFilePath = os.path.join(c.PATH_TO_RESOURCES, "testRecipes.json")
	util.dumpJSONDict(allRecipesFilePath, mergedDict)

if __name__ == "__main__":
	main(sys.argv)

else:
	pass