'''
Random Recipe CS 221 Final Project
Austin Ray, Bruno De Martino, Alex Lin
'''

import math, random, collections, database

USER_INPUT = True

recipesInDatabase = False
remainingCalls = False
missedIngredients = False
allRecipesFilename = 'allRecipes.json'
allNutritionalFilename = 'allNutritional.json'
numRecipes = 500

if USER_INPUT:
	recipesInDatabase = raw_input('Show print line per recipe added on database?: ') in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
	print recipesInDatabase
	remainingCalls = raw_input('Show print line per time Gov Database is accessed?: ') in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
	missedIngredients = raw_input('Show print line per ingredient missed?: ') in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
	allRecipesFilename = raw_input('Filename to store all recipes (in JSON format): ') + ".json"
	allNutritionalFilename = raw_input('Filename to store all nutritional ingredient information (in JSON format): ') + ".json"
	numRecipes = int(raw_input('Number of recipes: '))

database.setConstants(recipesInDatabase, remainingCalls, missedIngredients)
database.createDatabases(allRecipesFilename, allNutritionalFilename, numRecipes)
# database.printMissedIngredients()