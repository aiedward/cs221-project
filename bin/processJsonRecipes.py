import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys
import tokenize, re, string
import json, unicodedata

##
# Global Variables
##
PATH_TO_RESOURCES = "../res"
PATH_TO_EXECUTABLES = "../bin"
PATH_TO_LIBRARIES = "../lib"
FILENAME_JSON_RECIPES = "allRecipes.json"

##
# Function: main
# --------------
#
##
def main(argv):
	allRecipes = []
	ingredientAliases = set()

	# Read in and parse recipe data structures (dictionaries) from a json file.
	extractRecipesFromJSON(allRecipes)

	# Convert all string data to lowercase.
	formatStrings(allRecipes)

	# Fill a set with all short names for ingredients seen in the recipes.
	getIngredientAliases(allRecipes, ingredientAliases)

	print list(ingredientAliases)[:5]


##
# Function: extractRecipesFromJSON
# --------------------------------
# Reads in all data from the json file containing all recipe data.
##
def extractRecipesFromJSON(allRecipes):
	jsonFileName = os.path.join(PATH_TO_RESOURCES, FILENAME_JSON_RECIPES);
	fullJsonString = open(jsonFileName, 'r').read()
	#noUnicodeJsonString = fullJsonString.decode('unicode_escape').encode('ascii','ignore')
	#asciiJsonString = fullJsonString.decode('unicode-escape')

	d = json.JSONDecoder()
	myDict = d.decode(fullJsonString)

	for _, val in myDict.items():
		allRecipes.append(val)

##
# Function: formatStrings
# -----------------------
# Converts all string data to lowercase.
##
def formatStrings(allRecipes):
	for recipe in allRecipes:
		for key in ["course", "ingredientLines", "ingredients"]:
			recipe[key] = [s.lower() for s in recipe[key]]
		recipe["recipeName"] = recipe["recipeName"].lower()

##
# Function: getIngredientAliases
# ------------------------------
# Fill a set with every ingredient alias (short name for ingredient)
# seen in the "ingredients" entry for all recipes.
#
# Example:
#    An alias for "1 pound dried pasta" might be "dried pasta"
#    An alias for "4 cloves garlic, minced" might be "garlic"
##
def getIngredientAliases(allRecipes, ingredientAliases):
	for recipe in allRecipes:
		for alias in recipe["ingredients"]:
			ingredientAliases.add(alias)


# If called from command line, call the main() function
if __name__ == "__main__":
    main(sys.argv)




















