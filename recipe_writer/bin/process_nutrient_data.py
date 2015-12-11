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
	print "Merging nutrient data"
	pathToNutrients = os.path.join(c.PATH_TO_RESOURCES, "nutrients", "nutrientdata")

	# Get the full absolute file paths of all files in /res/nutrients/foundingredients
	# that end in ".json"
	jsonNutrients = util.listFilesWithSuffix(pathToNutrients, ".json")

	# Load all of these ".json" files into dictionaries and put all
	# these dictionaries in a list
	listOfJSONDicts = util.loadJSONDicts(jsonNutrients)

	# Merge Nutrients into one dictionary, deleting duplicates
	mergedDict = util.naivelyMergeDicts(listOfJSONDicts)

	# Write the merged recipe dictionary to a file
	nutrientIDsFilePath = os.path.join(c.PATH_TO_RESOURCES, "allNutrientData.json")
	util.dumpJSONDict(nutrientIDsFilePath, mergedDict)

	#This will prepare the json file of valid ingredients
	validIngredientDict = {}
	validNutrientDict = {}
	for ingredient in mergedDict:
		#print ingredient.encode('ascii', errors='ignore')
		validIngredientDict[ingredient] = 0
		for nutrient in mergedDict[ingredient]['nutrients']:
			validNutrientDict[nutrient] = 0



	print "There are " + str(len(validIngredientDict)) + " valid ingredients."
	print "There are " + str(len(validNutrientDict)) + " valid nutrients."

	validIngredientsFilePath = os.path.join(c.PATH_TO_RESOURCES, "validIngredients.json")
	validNutrientFilePath = os.path.join(c.PATH_TO_RESOURCES, "validNutrients.json")
	util.dumpJSONDict(validIngredientsFilePath, validIngredientDict)
	util.dumpJSONDict(validNutrientFilePath, validNutrientDict)



if __name__ == "__main__":
	main(sys.argv)

else:
	pass