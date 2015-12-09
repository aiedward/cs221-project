import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys
import tokenize, re, string
import json, unicodedata
import thread

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
	aliasCounts = {}
	aliasRelations = {}
	aliasToAliasLines = {}

	# Read in and parse recipe data structures (dictionaries) from a json file.
	extractRecipesFromJSON(allRecipes)

	# Convert all string data to lowercase.
	lowerAllStrings(allRecipes)

	# Get the counts of ingredient short names.
	# Create a dictionary storing relationships between the various aliases.
	# Create a dictionary with aliases as keys and lists of lines they've been
	#    associated with as values.
	fillDataStructures(allRecipes, aliasCounts, aliasRelations, aliasToAliasLines)

	# print sorted(aliasCounts.items(), key=lambda x: -x[1])[:10]

	for item in aliasRelations.items()[:10]:
		print item

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
# Function: lowerAllStrings
# -----------------------
# Converts all string data to lowercase.
##
def lowerAllStrings(allRecipes):
	for recipe in allRecipes:
		for key in ["course", "ingredientLines", "ingredients"]:
			recipe[key] = [s.lower() for s in recipe[key]]
		recipe["recipeName"] = recipe["recipeName"].lower()

##
# Function: fillDataStructures
# ----------------------------
# 
##
def fillDataStructures(allRecipes, aliasCounts, aliasRelations, aliasToAliasLines):
	fillAliasCounts(allRecipes, aliasCounts)
	fillAliasRelations(allRecipes, aliasRelations)
	fillAliasLineRelations(allRecipes, aliasToAliasLines)


##
# Function: fillAliasCounts
# ------------------------------
# Get the counts of ingredient short names and create a dictionary storing
# relationships between the various aliases.
#
# Example Aliases:
#    An alias for "1 pound dried pasta" might be "dried pasta"
#    An alias for "4 cloves garlic, minced" might be "garlic"
##
def fillAliasCounts(allRecipes, aliasCounts):
	for recipe in allRecipes:
		for alias in recipe["ingredients"]:
			aliasCounts[alias] = aliasCounts.get(alias, 0) + 1

def fillAliasRelations(allRecipes, aliasRelations):
	for recipe in allRecipes:
		ingredientAliases = recipe["ingredients"]
		numIngredientAliases = len(ingredientAliases)
		for i in xrange(numIngredientAliases):
			alias = ingredientAliases[i]

			# Add the other aliases in this recipe to this alias's
			# relation list (aliases it's been seen with)
			aliasRelations[alias] = aliasRelations.get(alias, []) + \
				[ingredientAliases[j] for j in xrange(numIngredientAliases) if j != i]

	# Tally up each ingredient in the alias relations list for each alias
	for key in aliasRelations.keys():
		aliasRelations[key] = dict(collections.Counter(aliasRelations[key]))

def fillAliasLineRelations(allRecipes, aliasToAliasLines):
	pass


# If called from command line, call the main() function
if __name__ == "__main__":
    main(sys.argv)




















