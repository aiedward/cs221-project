##
# File: /bin/process_recipes.py
# -----------------------------
# Process raw recipe JSON data and output that processed data to JSON files.
##

import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
import thread

from lib import util
from lib import constants as c
from lib import nutrientdatabase as ndb

validAliasDict = {}
nutDB = ndb.NutrientDatabase()

##
# Function: main
# --------------
#
##
def main(argv):
	global validAliasDict
	validIngredientsFilePath = os.path.join(c.PATH_TO_RESOURCES, "validIngredients.json")
	validAliasDict = util.loadJSONDict(validIngredientsFilePath)


	allRecipes = []

	# Each alias has 3 main fields:
	#   "count"
	#   "aliasBuddies"
	#   "lines"
	aliasData = {}
	ingredientLineDict = {}

	# Read in and parse recipe data structures (dictionaries) from a json file.
	extractRecipesFromJSON(allRecipes)

	# Convert all string data to lowercase.
	lowerAllStrings(allRecipes)

	#nutDB = ndb.NutrientDatabase()
	
	#Let's fuck around.
	for recipe in allRecipes:
		print "Ingredient Lines: " + str(len(recipe['ingredientLines']))
		print recipe['ingredientLines']
		print "\nIngredients: " + str(len(recipe['ingredients']))
		print recipe['ingredients']

		for ingredientLineIndex in range(0, len(recipe['ingredientLines'])):
			if ingredientLineIndex == len(recipe['ingredients']):
				break
		 	ingredientLine = recipe['ingredientLines'][ingredientLineIndex].encode('ascii', errors='ignore')
		 	ingredient = recipe['ingredients'][ingredientLineIndex].encode('ascii', errors='ignore')
		 	if ingredient not in validAliasDict:
		 		continue
		 	if ingredient not in ingredientLineDict:
		 		ingredientLineDict[ingredient] = []
		 	ingredientLineDict[ingredient].append(ingredientLine)

	#print ingredientLineDict

	for ingredient in ingredientLineDict:
		for ingredientLine in ingredientLineDict[ingredient]:
			#TIME TO PARSE.
			words = ingredientLine.split()
			potentialStart = removeHyphen(words[0])

			#If the first token is a number, try the next few.
			if isPossibleAmount(words[0]):
				if '/' in potentialStart:
					tokens = potentialStart.split('/')
					first = float(tokens[0])
					second = float(tokens[1])
					potentialStart = first/second
				amount = float(potentialStart)
				potentialUnit = extractUnit(words, ingredient)
				#print "Amount: " + str(amount)
				if potentialUnit != None:
					pass
					#print "Amount: " + str(amount) + " Unit: " + potentialUnit
				else:
					print "Couldn't match unit for ingredient: " + ingredient
					print words
			
			#Need to figure out what unit. It is.
			#print words[0]
			#print ingredientLine

	# 	for i in range(0, len(ingredient)):
	# 		print ingredientLineDict[ingredient]
	
	# Get the counts of ingredient short names.
	# Create a dictionary storing relationships between the various aliases.
	# Create a dictionary with aliases as keys and lists of lines they've been
	# associated with as values.
	fillAliasData(allRecipes, aliasData)



	for key in aliasData:
		if key not in validAliasDict:
			print "Ya fucked up with the ingredient: " + key

	#Temporarily removed to test.
	#dumpAliasDataToJSONFiles(aliasData)

	# #Now create small files
	# smallAliasData = {}
	# for _ in range(250):
	# 	item = aliasData.popitem()
	# 	smallAliasData[item[0]] = item[1]

	# smallFilePath = os.path.join(c.PATH_TO_RESOURCES, "aliasData_small.json")
	# util.dumpJSONDict(smallFilePath, smallAliasData)

	# for _ in range(250):
	# 	item = aliasData.popitem()
	# 	smallAliasData[item[0]] = item[1]

	# mediumFilePath = os.path.join(c.PATH_TO_RESOURCES, "aliasData_medium.json")
	# util.dumpJSONDict(mediumFilePath, smallAliasData)

	# for _ in range(500):
	# 	item = aliasData.popitem()
	# 	smallAliasData[item[0]] = item[1]

	# largeFilePath = os.path.join(c.PATH_TO_RESOURCES, "aliasData_large.json")
	# util.dumpJSONDict(largeFilePath, smallAliasData)

# Loop throuh each of the tokens of the ingredient line, looking for a match
# with the units given for that particular ingredient.
def extractUnit(tokens, ingredient):
	#print tokens
	for potentialUnit in tokens:
		potentialUnit = translatePotentialUnit(potentialUnit)
		#print "Potential unit: " + potentialUnit
		#print "Testing if " + potentialUnit + " is a possible unit for " + ingredient
		if nutDB.isValidConversionUnit(ingredient, potentialUnit):
			return potentialUnit
		#Check plurals by removing the last letter
		if nutDB.isValidConversionUnit(ingredient, potentialUnit[:-1]):
			return potentialUnit
	return None



def translatePotentialUnit(unit):
	unit = unit.replace('.', '')
	if unit == 'cups':
		return 'cup'
	if unit == 'pounds' or unit == 'pound':
		return 'lb'
	if unit == 'teaspoons' or unit == 'teaspoon':
		return 'tsp'
	if unit == 'tablespoons' or unit == 'tablespoon':
		return 'tbsp'
	if unit == 'ounce' or unit == 'ounces':
		return 'oz'
	return unit


def removeHyphen(inputString):
	if '-' in inputString:
		return inputString[inputString.rfind('-'):]
	return inputString

def isPossibleAmount(inputString):
	for char in inputString:
		if not char.isdigit() or char == '/' or char == '-':
			return False
	return True
    #return any(char.isdigit() for char in inputString)

##
# Function: extractRecipesFromJSON
# --------------------------------
# Reads in all data from the json file containing all recipe data.
##
def extractRecipesFromJSON(allRecipes):
	#jsonFilePath = os.path.join(c.PATH_TO_RESOURCES, c.FILENAME_JSON_RECIPES)
	jsonFilePath = os.path.join(c.PATH_TO_RESOURCES, "tempAllRecipes.json")	
	myDict = util.loadJSONDict(jsonFilePath)

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
			if alias not in validAliasDict:
				continue
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
			if alias not in validAliasDict:
				continue
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
			if alias not in validAliasDict:
				continue
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
			if alias not in validAliasDict:
				continue
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

##
# Function: dumpAliasToJSONFiles
# ------------------------------
# Dumps data to a file with name aliasData + date + time in /res/aliasdata/
##
def dumpAliasDataToJSONFiles(aliasData):
	dataFileName = util.string_appendDateAndTime("aliasData")
	dataFilePath = os.path.join(c.PATH_TO_RESOURCES, "aliasdata", dataFileName)
	util.dumpJSONDict(dataFilePath, aliasData)


# If called from command line, call the main() function
if __name__ == "__main__":
	main(sys.argv)

# Otherwise, this file is being imported as a module
else:
	pass



















