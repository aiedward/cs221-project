##
# File: /bin/process_recipes.py
# -----------------------------
# Process raw recipe JSON data and output that processed data to JSON files.
##

import collections, itertools, copy, Queue
from collections import Counter
import numpy as np
import scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
import thread

from lib import util
from lib import constants as c
from lib import nutrientdatabase as ndb

validAliasDict = {}
ndb = ndb.NutrientDatabase()
ingredientMassDict = {}
unitCountDict = {}
##
# Function: main
# --------------
#
##
def main(argv):
	global ingredientMassDict
	global validAliasDict
	global unitCountDict
	validIngredientsFilePath = os.path.join(c.PATH_TO_RESOURCES, "validIngredients.json")
	validAliasDict = util.loadJSONDict(validIngredientsFilePath)

	conversionDict = createWaterConversionDict()

	allRecipes = []

	# Each alias has 3 main fields:
	#   "count"
	#   "aliasBuddies"
	#   "lines"
	aliasData = {}
	ingredientLineDict = {}
	#ingredientMassDict = {}
	#unitCountDict = {}

	# Read in and parse recipe data structures (dictionaries) from a json file.
	extractRecipesFromJSON(allRecipes)

	# Convert all string data to lowercase.
	lowerAllStrings(allRecipes)

	#ndb = ndb.NutrientDatabase()
	
	#Let's fuck around.
	unmatched = float(0)
	tried = float(0)
	for recipe in allRecipes:
		# print "Ingredient Lines: " + str(len(recipe['ingredientLines']))
		# print recipe['ingredientLines']
		# print "\nIngredients: " + str(len(recipe['ingredients']))
		# print recipe['ingredients']

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
				potentialUnit, foundUnit = extractUnit(words, ingredient, conversionDict)
				
				if potentialUnit != None:
					#Add both the mass and the unit count
					if foundUnit:
						massInGrams = amount*ndb.getConversionFactor(ingredient, potentialUnit)
					else:
						massInGrams = amount*conversionDict[potentialUnit]
					if ingredient not in ingredientMassDict:
						ingredientMassDict[ingredient] = []
					ingredientMassDict[ingredient].append(massInGrams)
					if ingredient not in unitCountDict:
						unitCountDict[ingredient] = Counter()
					unitCountDict[ingredient][potentialUnit] += 1	
					#print "Amount: " + str(amount) + " Unit: " + potentialUnit
				else:
					unmatched += 1
					#print "Couldn't match unit for ingredient: " + ingredient
					#print words
					#print


			elif not hasAnAmount(words):
				if ingredient not in unitCountDict:
					unitCountDict[ingredient] = Counter()
				unitCountDict[ingredient]['unitless'] += 1
			tried += 1
	print "Missed amounts for " + str(unmatched) + " / " + str(tried) + " ingredients."
	print str((tried-unmatched)/tried*100) + "% Success rate!"


	# Get the counts of ingredient short names.
	# Create a dictionary storing relationships between the various aliases.
	# Create a dictionary with aliases as keys and lists of lines they've been
	# associated with as values.

	fillAliasData(allRecipes, aliasData)

	#Temporarily removed to test.
	dumpAliasDataToJSONFiles(aliasData)

	#Now create small files
	smallAliasData = {}
	for _ in range(250):
		item = aliasData.popitem()
		smallAliasData[item[0]] = item[1]

	smallFilePath = os.path.join(c.PATH_TO_RESOURCES, "aliasData_small.json")
	util.dumpJSONDict(smallFilePath, smallAliasData)

	for _ in range(250):
		item = aliasData.popitem()
		smallAliasData[item[0]] = item[1]

	mediumFilePath = os.path.join(c.PATH_TO_RESOURCES, "aliasData_medium.json")
	util.dumpJSONDict(mediumFilePath, smallAliasData)

	for _ in range(500):
		item = aliasData.popitem()
		smallAliasData[item[0]] = item[1]

	largeFilePath = os.path.join(c.PATH_TO_RESOURCES, "aliasData_large.json")
	util.dumpJSONDict(largeFilePath, smallAliasData)

def hasAnAmount(tokens):
	for token in tokens:
		if isPossibleAmount(token):
			return True
	return False

##
# Function: extractRecipesFromJSON
# --------------------------------
# Loop throuh each of the tokens of the ingredient line, looking for a match
# with the units given for that particular ingredient.
#
##

def extractUnit(tokens, ingredient, conversionDict):

	#To limit to second word only, change to potentialUnit = token[1]
	#for potentialUnit in tokens:
	potentialUnit = tokens[1]
	if isPossibleAmount(potentialUnit):
		#return none none for naive
		return None, None
		#continue
	potentialUnit = translatePotentialUnit(potentialUnit)
	singular = potentialUnit
	plural = potentialUnit[:-1]
	validUnitList = ndb.listConversionUnits(ingredient)
	
	if validUnitList is not None:
		#Check for perfect match first.
		for validConversionUnit in validUnitList:
			#validConversionUnit= validConversionUnit.replace('.', '')
			if singular == validConversionUnit or plural == validConversionUnit:
				return validConversionUnit, True
		#Check for contains match second.
		for validConversionUnit in validUnitList:
			if singular in validConversionUnit or plural in validConversionUnit:
				return validConversionUnit, True
				
	# If here, couldn't find a matching unit within the nutritional data, so match
	# the unti we see in the ingredient line (if any) to match a standard unit.
	#for potentialUnit in tokens:
	potentialUnit = translatePotentialUnit(potentialUnit)
	if potentialUnit in conversionDict:
		return potentialUnit, False
	return None, None

def createWaterConversionDict():
	returnDict = {}
	returnDict['cup'] = 236.6
	returnDict['lb'] = 453.6
	returnDict['tsp'] = 4.929
	returnDict['tbsp'] = 14.79
	returnDict['oz'] = 28.35
	returnDict['ml'] = 1
	returnDict['l'] = 1000
	return returnDict

def translatePotentialUnit(unit):
	unit = unit.replace('.', '')
	if unit == 'cups':
		return 'cup'
	if unit == 'pounds' or unit == 'pound' or unit == 'lbs':
		return 'lb'
	if unit == 'teaspoons' or unit == 'teaspoon':
		return 'tsp'
	if unit == 'tablespoons' or unit == 'tablespoon' or unit == 'tbs':
		return 'tbsp'
	if unit == 'ounce' or unit == 'ounces' or unit == 'ozs':
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

def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]

##
# Function: extractRecipesFromJSON
# --------------------------------
# Reads in all data from the json file containing all recipe data.
##
def extractRecipesFromJSON(allRecipes):
	jsonFilePath = os.path.join(c.PATH_TO_RESOURCES, c.FILENAME_JSON_RECIPES)
	#jsonFilePath = os.path.join(c.PATH_TO_RESOURCES, "tempAllRecipes.json")	
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
	print "Initializing data"
	initializeAliasData(allRecipes, aliasData)
	print "Filling Counts"
	fillAliasCounts(allRecipes, aliasData)
	print "Filling Relations"
	fillAliasRelations(allRecipes, aliasData)
	print "Filling Line Relations"
	fillAliasLineRelations(allRecipes, aliasData)

	convertBuddyListToNormalDict(aliasData)

##
# Function: initializeAliasData
# ----------------------------
# Make the various field's for each alias's dict easier to add things to.
##
def initializeAliasData(allRecipes, aliasData):
	# for recipe in allRecipes:
	# 	for alias in recipe["ingredients"]:
	# 		if alias not in ingredientMassDict:
				# continue
	#print "Num aliases: " + str(len(ingredientMassDict))
	#count = 0
	for alias in ingredientMassDict:
		#print "Alias #: " + str(count)
		#count += 1
		if alias not in unitCountDict.keys():
			continue
		if alias not in aliasData:
			amountStats = {}
			amountStats['max'] = max(ingredientMassDict[alias])
			amountStats['min'] = min(ingredientMassDict[alias])
			amountStats['mean'] = numpy.mean(ingredientMassDict[alias])
			amountStats['stddev'] = numpy.std(ingredientMassDict[alias])
			amountStats['median'] = numpy.median(ingredientMassDict[alias])
			aliasData[alias] = \
				{"count": 0, 
				"aliasBuddies": collections.defaultdict(int), 
				"lines": [],
				"allAmounts": ingredientMassDict[alias],
				"amountStatistics": amountStats,
				"unitCounter": unitCountDict[alias]
				}

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
			if alias not in ingredientMassDict:
				continue
	#for alias in ingredientMassDict:
			try:
				aliasData[alias]["count"] += 1
			except KeyError:
				pass

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
			if alias not in ingredientMassDict:
				continue
			#if alias not in unitCountDict.keys():
			#	continue
			# Add the other aliases in this recipe to this alias's
			# buddy alias dict (aliases it's been seen with)
			for j, aliasBuddy in enumerate(ingredientAliases):
				if j == i:
					continue

				# Add 1 to the count for this buddy
				try:
					aliasData[alias]["aliasBuddies"][aliasBuddy] +=1
				except KeyError:
					pass

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
			if alias not in ingredientMassDict:
				continue
			#if alias not in unitCountDict.keys():
			#	continue
			try:
				aliasData[alias]["lines"].append(aliasLine)
			except KeyError:
				pass

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



















