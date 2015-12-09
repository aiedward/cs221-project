'''
Random Recipe CS 221 Final Project
Austin Ray, Bruno De Martino, Alex Lin
'''

import math, random, collections, sys, time
import lib.database as database
import lib.constants as c

USER_INPUT = True

recipesInDatabase = False
remainingCalls = False
missedIngredients = False
allRecipesFilename = 'allRecipes.json'
allNutritionalFilename = 'allNutritional.json'
numRecipes = 500
startNum = 0
apiNum = 0

def main(argv):
	#if sys.argv[1] == "-d":
		
	#else:
	if USER_INPUT:
		recipesInDatabase = raw_input('Show print line per recipe added on database?: ') in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
		print recipesInDatabase
		remainingCalls = raw_input('Show print line per time Gov Database is accessed?: ') in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
		missedIngredients = raw_input('Show print line per ingredient missed?: ') in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
		allRecipesFilename = raw_input('Filename to store all recipes (in JSON format): ')# + ".json"
		allNutritionalFilename = raw_input('Filename to store all nutritional ingredient information (in JSON format): ')# + ".json"
		numRecipes = int(raw_input('Number of recipes: '))
		startNum = int(raw_input('Starting Recipe number: '))
		apiNum = int(raw_input('API Number: '))

	database.setConstants(recipesInDatabase, remainingCalls, missedIngredients, apiNum, startNum)
	#database.createDatabases(allRecipesFilename, allNutritionalFilename, numRecipes)
	start_time = time.time()
	
	#Do threading here:
	#################################################
	database.createOnlyRecipeDatabase(allRecipesFilename, allNutritionalFilename, numRecipes, startNum)
	#################################################

	# database.printMissedIngredients()
	print("--- %s seconds ---" % (time.time() - start_time))
