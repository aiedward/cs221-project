##
# File: /bin/merge_Nutrients.py
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
	print "Merging nutrient IDs"
	pathToNutrients = os.path.join(c.PATH_TO_RESOURCES, "nutrients", "foundingredients")

	# Get the full absolute file paths of all files in /res/nutrients/foundingredients
	# that end in ".json"
	jsonNutrients = util.listFilesWithSuffix(pathToNutrients, ".json")

	# Load all of these ".json" files into dictionaries and put all
	# these dictionaries in a list
	listOfJSONDicts = util.loadJSONDicts(jsonNutrients)

	# Merge Nutrients into one dictionary, deleting duplicates
	mergedDict = util.naivelyMergeDicts(listOfJSONDicts)

	# Write the merged recipe dictionary to a file
	nutrientIDsFilePath = os.path.join(c.PATH_TO_RESOURCES, "allNutrientIDs.json")
	util.dumpJSONDict(nutrientIDsFilePath, mergedDict)

if __name__ == "__main__":
	main(sys.argv)

else:
	pass