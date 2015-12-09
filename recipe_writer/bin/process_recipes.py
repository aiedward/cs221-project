import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
import thread

from lib import constants as c
c.init(os.path.dirname(os.path.dirname(__file__)))


##
# Function: main
# --------------
#
##
def main(argv):
	allRecipes = []

	# Each alias has 3 main fields:
	#   "count"
	#   "aliasBuddies"
	#   "lines"
	aliasData = {}

	# Read in and parse recipe data structures (dictionaries) from a json file.
	extractRecipesFromJSON(allRecipes)

	# Convert all string data to lowercase.
	lowerAllStrings(allRecipes)

	# Get the counts of ingredient short names.
	# Create a dictionary storing relationships between the various aliases.
	# Create a dictionary with aliases as keys and lists of lines they've been
	#    associated with as values.
	fillAliasData(allRecipes, aliasData)

	dumpDictToJsonFile(aliasData, "aliasData")

	printAliasData(aliasData, 5, True)
	


##
# Function: extractRecipesFromJSON
# --------------------------------
# Reads in all data from the json file containing all recipe data.
##
def extractRecipesFromJSON(allRecipes):
	# print "c.PATH_TO_RESOURCES: ", c.PATH_TO_RESOURCES
	# print "c.FILENAME_JSON_RECIPES", c.FILENAME_JSON_RECIPES
	# Read in the JSON file containing recipe data
	jsonFileName = os.path.join(c.PATH_TO_RESOURCES, c.FILENAME_JSON_RECIPES);
	fullJsonString = None
	with open(jsonFileName, 'r') as f:
		fullJsonString = f.read()

	# This is dead code I was trying to use to remove all escaped unicode
	# characters (e.g. \u00bd) or convert them to ascii
	#noUnicodeJsonString = fullJsonString.decode('unicode_escape').encode('ascii','ignore')
	#asciiJsonString = fullJsonString.decode('unicode-escape')

	# Read the JSON file in as a dictionary
	d = json.JSONDecoder()
	myDict = d.decode(fullJsonString)

	# Fill allRecipes with just the values for each JSON member,
	# as the values actually contain the keys as a member
	for _, val in myDict.items():
		allRecipes.append(val)

##
# Function: lowerAllStrings
# -------------------------
# Converts all string data to lowercase.
##
def lowerAllStrings(allRecipes):
	for recipe in allRecipes:
		for key in ["course", "ingredientLines", "ingredients"]:
			recipe[key] = [s.lower() for s in recipe[key]]
		recipe["recipeName"] = recipe["recipeName"].lower()

##
# Function: fillAliasData
# -----------------------
# Example Aliases:
#    An alias for "1 pound dried pasta" might be "dried pasta"
#    An alias for "4 cloves garlic, minced" might be "garlic"
##
def fillAliasData(allRecipes, aliasData):
	initializeAliasData(allRecipes, aliasData)

	fillAliasCounts(allRecipes, aliasData)
	fillAliasRelations(allRecipes, aliasData)
	fillAliasLineRelations(allRecipes, aliasData)

	convertBuddyListToNormalDict(aliasData)

##
# Function: initializeAliasData
# ----------------------------
# Make the various field's for each alias's dict easier to add things to.
##
def initializeAliasData(allRecipes, aliasData):
	for recipe in allRecipes:
		for alias in recipe["ingredients"]:
			if alias not in aliasData:
				aliasData[alias] = \
					{"count": 0, 
					"aliasBuddies": collections.defaultdict(int), 
					"lines": []}

##
# Function: fillAliasCounts
# ------------------------------
# Get the counts of total number of appearances of all
# short-names (aliases) in all recipes.
#
# Example aliasCounts:
# {
#   "garlic": 8,
#   "oregano": 18
# }
##
def fillAliasCounts(allRecipes, aliasData):
	for recipe in allRecipes:
		for alias in recipe["ingredients"]:
			aliasData[alias]["count"] += 1

##
# Function: fillAliasRelations
# ----------------------------
# Fill relations from ingredient short-names (aliases) to other
# aliases they've been seen with in the same recipe. Counts of how
# many times they've been seen with each ingredient are included.
#
# Example aliasRelations:
# {
#   "garlic": {"oregano": 5, "crushed tomatoes": 1, "small yellow onion": 2},
#   "oregano": {"garlic": 5, "crushed tomatoes": 3, "salt": 10}
# }
##
def fillAliasRelations(allRecipes, aliasData):
	for recipe in allRecipes:
		ingredientAliases = recipe["ingredients"]
		for i, alias in enumerate(ingredientAliases):
			# Add the other aliases in this recipe to this alias's
			# buddy alias dict (aliases it's been seen with)
			for j, aliasBuddy in enumerate(ingredientAliases):
				if j == i:
					continue

				# Add 1 to the count for this buddy
				aliasData[alias]["aliasBuddies"][aliasBuddy] +=1

##
# Function: fillAliasLineRelations
# --------------------------------
# Fill relations from ingredient short-names (aliases) to lists of ingredient
# lines that've been written for them.
#
# Example aliasLineRelations:
# {
#    "garlic": ["4 cloves garlic, minced", "garlic to taste, diced"],
#    "oregano": ["1/4 teaspoon dried oregano", "oregano and basil to taste"]
# }
##
def fillAliasLineRelations(allRecipes, aliasData):
	for recipe in allRecipes:
		for alias, aliasLine in zip(recipe["ingredients"], recipe["ingredientLines"]):
			aliasData[alias]["lines"].append(aliasLine)

##
# Function: convertBuddyListToNormalDict
# --------------------------------------
# Default dicts are fine, but I'd rather have the ["aliasBuddies"] field be
# just a normal dict. This doesn't actually change much.
##
def convertBuddyListToNormalDict(aliasData):
	for alias in aliasData:
		aliasData[alias]["aliasBuddies"] = dict(aliasData[alias]["aliasBuddies"])

##
# Function: convertBuddyListToNormalDict
# --------------------------------------
# Print out the 3 fields for each alias.
##
def printAliasData(aliasData, numToPrint, randomize):
	itemsToPrint = None
	if randomize == True:
		itemsToPrint = random.sample(aliasData.items(), numToPrint)
	else:
		itemsToPrint = aliasData.items()[:numToPrint]

	for key, val in itemsToPrint:
		print key
		print "--------"
		for k, v in val.items():
			print k, ": ", v
		print

def dumpDictToJsonFile(dict2dump, fileNamePrefix):
	jsonDatabase = json.dumps(dict2dump, sort_keys=True, indent=4)
	fileName = string_appendDateAndTime(fileNamePrefix)
	fullFileName = os.path.join(c.PATH_TO_ALIASDATA, fileName)
	with open(fullFileName, "w") as f:
		f.write(jsonDatabase)

def string_appendDateAndTime(s):
	return "_".join([s, time.strftime("%m-%d-%Y"), time.strftime("%Hh-%Mm-%Ss")]) + ".json"


# If called from command line, call the main() function
if __name__ == "__main__":
	main(sys.argv)

# Otherwise, this file is being imported as a module
else:
	pass



















