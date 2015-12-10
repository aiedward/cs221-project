'''
Random Recipe CS 221 Final Project
Austin Ray, Bruno De Martino, Alex Lin
Database file

This file is responsible for constructing the Recipe and the Nutritional Databases
'''

# -------------------- NOTES --------------------

import collections, requests, json, time, pdb, sys, time, os
from lib import constants as c
from lib import util

# Yummly API constants
YUM_APP_ID = "4d1d7424"
YUM_APP_KEY = "419a5ef2649eb3b6e359b7a9de93e905"

#Creates the array of constant strings that are the API Keys for
#accessing the US Govt Nutritional Database.
govAPIArray = [c.GOV_NUT_API_KEY_0, c.GOV_NUT_API_KEY_1, c.GOV_NUT_API_KEY_2, \
	c.GOV_NUT_API_KEY_3, c.GOV_NUT_API_KEY_4, c.GOV_NUT_API_KEY_5,  c.GOV_NUT_API_KEY_6, \
	c.GOV_NUT_API_KEY_7, c.GOV_NUT_API_KEY_8, c.GOV_NUT_API_KEY_9, c.GOV_NUT_API_KEY_10, \
	c.GOV_NUT_API_KEY_11, c.GOV_NUT_API_KEY_12, c.GOV_NUT_API_KEY_13, c.GOV_NUT_API_KEY_14, \
	c.GOV_NUT_API_KEY_15, c.GOV_NUT_API_KEY_16, c.GOV_NUT_API_KEY_17, c.GOV_NUT_API_KEY_18, \
	c.GOV_NUT_API_KEY_19]

# Global variables
foundIngredients = {}
missedIngredients = {}
foundItems = 0
missedIngredients = 0

shouldCycleAPIKeys = True
lastSuccessfulAPIKeyIndex = c.NUM_API_KEYS - 1
lastAPIKeyIndex = lastSuccessfulAPIKeyIndex
currentAPIKey = 19 #Default value.



def getNextAPIKeyIndex():
	global shouldCycleAPIKeys
	global lastSuccessfulAPIKeyIndex
	global lastAPIKeyIndex
	global currentAPIKey


	nextAPIKeyIndex = lastAPIKeyIndex + 1
	if nextAPIKeyIndex == c.NUM_API_KEYS:
		nextAPIKeyIndex = 0
	lastAPIKeyIndex = nextAPIKeyIndex
	if lastSuccessfulAPIKeyIndex == nextAPIKeyIndex:
		shouldCycleAPIKeys = False
	return nextAPIKeyIndex


def setConstants(recipesInDatabase, remainingCalls, missedIngredients, apiNum,startNum):
	global shouldCycleAPIKeys
	global lastSuccessfulAPIKeyIndex
	global lastAPIKeyIndex
	global currentAPIKey

	#This starts at the last position so that the first call to getNextAPIKeyIndex
	#returns 0.
	shouldCycleAPIKeys = True
	lastSuccessfulAPIKeyIndex = c.NUM_API_KEYS - 1
	lastAPIKeyIndex = lastSuccessfulAPIKeyIndex
	currentAPIKey = 19 #Default value.
	print "Constants set!"


# Function: printMissedIngredients
# ---------------------
# Prints each ingredient in the @missedIngredients global list
def printMissedIngredients():
	print "These are the ingredients that do not exist in the government Nutritional Database:"
	for ingredient in missedIngredients:
		print ingredient

# Function: addIngredientToNutritionalList
# ---------------------
# Takes in a list of ingredients (@ingredients). For each ingredient, we search
# for it in the Nutritional Database. If we find it, we add it to our dictionary
# of ingredient -> ingredientIds (@foundIngredients). Otherwise, we add it to
# out missedIngredients list
def addIngredientToNutritionalList(ingredients):
	global shouldCycleAPIKeys
	global lastSuccessfulAPIKeyIndex
	global lastAPIKeyIndex
	global currentAPIKey

	foundItems = 0
	missedItems = 0
	foundIngredients = {}
	missedIngredients = {}
	print "adding ingredients to nutritionalList"
	foundIngredientsFilename = os.path.join(c.PATH_TO_RESOURCES, "nutrients", "foundingredients", "foundingredients")
	missedIngredientsFilename = os.path.join(c.PATH_TO_RESOURCES, "nutrients", "missedingredients", "missedingredients")
	foundFileCount = 0
	missedFileCount = 0
	for ingredient in ingredients:
		foundIngredient, searchRequest = nutritionalSearch(ingredient)

		if foundIngredient:
			# Adding ingredient to foundIngredients dict
			nutritionalResults = json.loads(searchRequest.content)
			resultList = nutritionalResults.get('list')
			if resultList is not None:
				ingredientId = resultList["item"][0]["ndbno"]
				if ingredient not in foundIngredients:
					foundIngredients[ingredient] = ingredientId
					foundItems += 1
			else:
				print "ERROR, list is None. Check it out the results: %s" % nutritionalResults
				print searchRequest.status_code

		else:
			# Adding ingredient to missedIngredients list
			if ingredient not in missedIngredients:
				missedIngredients[ingredient] = 0
				missedItems += 1
		if len(foundIngredients) % c.YUM_STEP == 0 and len(foundIngredients) != 0:
			# Dumps and prints out a .JSON file for every YUM_STEP recipes retrieved.
			jsonIngredientDatabase = json.dumps(foundIngredients, sort_keys=True, indent=4)
			#Filename is /res/jsonrecipes/jsonrecipe_index, where index is startIndex/100.
			targetFileName = foundIngredientsFilename + "_" + str(foundFileCount) + ".json"
			foundIngredientsFile = open(targetFileName, 'w+')
			foundIngredientsFile.write(jsonIngredientDatabase)
			foundIngredientsFile.close()
			#Adding to clears dict so that next iteration will print clean.
			foundIngredients.clear()
			foundFileCount += 1
		if len(missedIngredients) % c.YUM_STEP == 0 and len(missedIngredients) != 0:
			# Dumps and prints out a .JSON file for every YUM_STEP recipes retrieved.
			jsonIngredientDatabase = json.dumps(missedIngredients, sort_keys=True, indent=4)
			#Filename is /res/jsonrecipes/jsonrecipe_index, where index is startIndex/100.
			targetFileName = missedIngredientsFilename + "_" + str(missedFileCount) + ".json"
			missedIngredientsFile= open(targetFileName, 'w+')
			missedIngredientsFile.write(jsonIngredientDatabase)
			missedIngredientsFile.close()
			#Adding to clears dict so that next iteration will print clean.
			missedIngredients.clear()
			missedFileCount += 1


# Function: nutritionalSearch
# ---------------------
# Makes search request on Nutritional API. Then, if the status is not 200
# (i.e. the request did not go through), it gets the remaining requests
# we have left for the hour (@remaining) and, checks whether remaining is
# larger than SLEEP_THRESHOLD.
#
# If it is, then the reason why the request did not go through
# was because the ingredient was not found in the ingredient database, so we
# return False and the @searchRequest.
#
# Otherwise, it means that we have exceeded the gov 1K API requests/hour, and
# thus we sleep for 10 min and keep trying until we can make API requests again.
def nutritionalSearch(ingredient):
	global shouldCycleAPIKeys
	global lastSuccessfulAPIKeyIndex
	global lastAPIKeyIndex
	global currentAPIKey


	currentAPIKeyIndex = lastAPIKeyIndex
	currentAPIKey = govAPIArray[currentAPIKeyIndex]

	#print "Ingredient is:" + ingredient.encode('ascii', errors='ignore')
	#print "currentAPIKey is: " + str(currentAPIKey)
	#print "currentAPIKeyIndex is: " + str(currentAPIKeyIndex)

	apiSearchString = "http://api.nal.usda.gov/ndb/search/?format=json&q=%s&max=1&api_key=%s" % (ingredient, currentAPIKey)
	searchRequest = requests.get(apiSearchString)
	remaining = int(searchRequest.headers['X-RateLimit-Remaining'])

	#if c.PRINT_REMAINING_CALLS: 
	print "SEARCH: Gov Nutrional Database requests remaining: %d with API Key # %s" %	 (remaining, currentAPIKeyIndex)

	while searchRequest.status_code != 200:
		# This means the ingredient wasn't found.  The calling function should handle the return value
		# and add this ingredient to the missed ingredients list.
		if remaining >= c.SLEEP_THRESHOLD:
			if c.PRINT_MISSED_INGREDIENTS: print "SEARCH: Could not find ingredient: %s" % ingredient
			return False, searchRequest

		#This means we've hit the API Limit
		while remaining < c.SLEEP_THRESHOLD:
			# This is calculated in getNextAPIKeyIndex().  If a full cycle is made with no successful returns, that means we've exhausted
			# ALL of our API Keys, and we'll just chill for a bit.
			if shouldCycleAPIKeys:
				currentAPIKeyIndex = getNextAPIKeyIndex()
				currentAPIKey = govAPIArray[currentAPIKeyIndex]
				apiSearchString = "http://api.nal.usda.gov/ndb/search/?format=json&q=%s&max=1&api_key=%s" % (ingredient, currentAPIKey)
				searchRequest = requests.get(apiSearchString)
				remaining = int(searchRequest.headers['X-RateLimit-Remaining'])
			else:
				#Naptime.
				print "SEARCH: Request failed because exceeded Gov 1K API requests/hour"
				print "... Sleeping for 10 min ..."
				time.sleep(c.SLEEP_TIME)
				apiSearchString = "http://api.nal.usda.gov/ndb/search/?format=json&q=%s&max=1&api_key=%s" % (ingredient, currentAPIKey)
				searchRequest = requests.get(apiSearchString)
				remaining = int(searchRequest.headers['X-RateLimit-Remaining'])
		print "SEARCH: Gov Nutrional Database requests remaining: %d with API Key %s" %	 (remaining, currentAPIKeyIndex)
	
	#Updates variables for proper cycling through API Keys
	lastSuccessfulAPIKeyIndex = currentAPIKeyIndex
	shouldCycleAPIKeys = True
	return True, searchRequest


# Function: getNutritionalRequest
# ---------------------
# Makes get request on Nutritional API. Then, if the status is not 200
# (i.e. the request did not go through), it gets the remaining requests
# we have left for the hour (@remaining) and, checks whether remaining is
# larger than SLEEP_THRESHOLD.
#
# If it is, then the reason why the request did not go through
# for a unknown reason, and we return
#
# Otherwise, it means that we have exceeded the gov 1K API requests/hour, and
# thus we sleep for 10 min and keep trying until we can make API requests again.
def getNutritionalRequest(ingredientId):
	global shouldCycleAPIKeys
	global lastSuccessfulAPIKeyIndex
	global lastAPIKeyIndex
	global currentAPIKey


	#Load current values for the APIKeyIndex and the APIKey
	currentAPIKeyIndex = lastAPIKeyIndex
	currentAPIKey = govAPIArray[currentAPIKeyIndex]

	#Try to get the necessary info.
	apiGetString = "http://api.nal.usda.gov/ndb/reports/?ndbno={0}&type=b&format=json&api_key={1}".format(ingredientId, currentAPIKey)
	getRequest = requests.get(apiGetString)
	if c.PRINT_REMAINING_CALLS: 
		print "GET: Gov Nutrional Database requests remaining: %d" % int(getRequest.headers['X-RateLimit-Remaining'])

	#On failure, Notify and either return/break on error, or loop API keys if waiting for the API limit to refresh.
	while getRequest.status_code != 200:
		print
		print "[BROKE REQUEST] Status code != 200"

		remaining = int(getRequest.headers['X-RateLimit-Remaining'])
		print "GET: Gov Nutrional Database requests remaining: %d with API Key %s" %	 (remaining, currentAPIKeyIndex)

		if remaining >= c.SLEEP_THRESHOLD:
			print "[ERROR] GET: Status != 200 but remaining (%d) >= SLEEP_THRESHOLD (%d)" % (remaining, c.SLEEP_THRESHOLD)
			return None
		
		#This means we've hit the API Limit
		while remaining < c.SLEEP_THRESHOLD:
			# This is calculated in getNextAPIKeyIndex().  If a full cycle is made with no successful returns, that means we've exhausted
			# ALL of our API Keys, and we'll just chill for a bit.
			if shouldCycleAPIKeys:
				currentAPIKeyIndex = getNextAPIKeyIndex()
				currentAPIKey = govAPIArray[currentAPIKeyIndex]
				apiGetString = "http://api.nal.usda.gov/ndb/reports/?ndbno={0}&type=b&format=json&api_key={1}".format(ingredientId, currentAPIKey)
				searchRequest = requests.get(apiGetString)
				remaining = int(searchRequest.headers['X-RateLimit-Remaining'])
			else:
				print "GET: Request failed because exceeded Gov 1K API requests/hour"
				print "... Sleeping for 10 min ..."
				time.sleep(c.SLEEP_TIME)
				getRequest = requests.get(apiGetString)
				remaining = int(getRequest.headers['X-RateLimit-Remaining'])
		print "GET: Gov Nutrional Database requests remaining: %d with API Key %s" %	 (remaining, currentAPIKeyIndex)

	#Updates variables for proper cycling through API Keys
	lastSuccessfulAPIKeyIndex = currentAPIKeyIndex
	shouldCycleAPIKeys = True
	return getRequest

# Function: buildNutritionalDatabase
# ---------------------
# Goes through all ingredients in the @ingredientNameIdMap, makes a get request
# for their ingredientId on the Nutritional Database, and creates a ingredientObj
# for it, which is then mapped to the ingredient in the @nutritionalDatabase.
#
# A ingredientObj has: ingredientName, ingredientId, and foodCalories.
# A foodCalories object has: the default value and units in 100g, and the measures,
# which consists of translated values for other common units of the ingredient.
#
# Once we have looped through all ingredients, we store the nutritionalDatabase in
# json format on the file with the filename.
def buildNutritionalDatabase(ingredientNameIdMap, filename):
	numIngredients = len(ingredientNameIdMap)
	print "... Creating Nutritional Database with %d items ..." % numIngredients

	nutritionalDatabase = {}

	for ingredientName, ingredientId in ingredientNameIdMap.iteritems():
		getRequest = getNutritionalRequest(ingredientId, currentAPIKey)

		if getRequest is not None:
			getFood = json.loads(getRequest.content)
			foodCalories = getFood['report']['food']['nutrients'][1]

			ingredientObj = {'ingredientName': ingredientName,
							 'ingredientId': ingredientId,
							 'foodCalories': (foodCalories['value'], foodCalories['unit'], foodCalories['measures'])}

			nutritionalDatabase[ingredientName] = ingredientObj

	jsonNutritionalDatabase = json.dumps(nutritionalDatabase, sort_keys=True, indent=4)
	allNutritionalFile = open(filename, 'w+')
	allNutritionalFile.write(jsonNutritionalDatabase)
	allNutritionalFile.close()
	print "... Done creating Nutritional Database with %d items ..." % numIngredients

	print "... Out of all %d ingredient in our recipe, we found %d of them, and missed %d of them ..." % (foundItems + missedItems, foundItems, missedItems)

# Function: buildRecipeEntry
# ---------------------
# Used to extract the JSON fields necessary to our database.  This is
# called for each recipe that we see in our get request of YUM_STEP
# Recipes in buildOnlyRecipeDatabase.
#
# Gets additional info from Yummly for each recipe,most importantly the
# List of igredients.  For a given recipe, we extract the field we want
# in our version of a recipe object. Then, we make a Yummly API get request
# to get more information on the recipe, so we can have access to the
# ingredientList of the recipe, which tells us the quantities per ingredient.
#
# Then, we create a recipeObj that has: recipeName, recipeId, ingredients,
# ingredientLines, cuisine and/or course,
# totalTimesInSeconds, flavors, and return it.
def buildRecipeEntry(recipe):
	recipeName = recipe['recipeName']
	recipeId= recipe['id']
	ingredients = recipe['ingredients']
	#Commenting out to test recipe dump.
	#addIngredientToNutritionalList(ingredients)
	
	brokeRequest = True

	while brokeRequest:
		apiGetString = "http://api.yummly.com/v1/api/recipe/%s?_app_id=4d1d7424&_app_key=419a5ef2649eb3b6e359b7a9de93e905" % recipeId
		getRequest = util.safeConnect(requests.get, tuple([apiGetString]))
		if getRequest == None:
			return None
		brokeRequest = not (getRequest.status_code == 200)

	getRecipe = json.loads(getRequest.content)
	ingredientLines = getRecipe["ingredientLines"]

	recipeObj = {'recipeName': recipeName,
				 'recipeId': recipeId,
				 'ingredients': ingredients,
				 'ingredientLines': ingredientLines,
				 'cuisine': recipe['attributes'].get('cuisine'),
				 'course': recipe['attributes'].get('course'),
				 'totalTimeInSeconds': recipe.get('totalTimeInSeconds'),
				 'flavors': recipe.get('flavors')}

	return recipeName, recipeObj

# Function: getNumSteps
# ---------------------
# Quick calculations to return the number of steps given totalResults
# and YUM_STEP.
def getNumSteps(totalResults):
	numSteps = totalResults/c.YUM_STEP
	if totalResults % c.YUM_STEP != 0:
		numSteps += 1
	return numSteps


# Function: indexedGetStartAndMaxResults
# ---------------------
# Quick calculations to return the start number and the
# maxResults number given the iteration we are in and the
# totalResults.  Used to build the API Request.
def indexedGetStartAndMaxResults(i, numSteps, totalResults, startIndex):
	#print "startnumber = " + str(startNumber)
	start = c.YUM_STEP * i + startIndex #Added offset into the recipe lists.
	maxResults = c.YUM_STEP
	if i == numSteps - 1:
		maxResults = totalResults - start + startIndex
	if totalResults < c.YUM_STEP:
		maxResults = totalResults
	return start, maxResults


# Function: buildOnlyRecipeDatabase
# ---------------------
# Modifies Bruno's original buildRecipeDatabase to constantly output to a set of files,
# writing within each loop.
def buildOnlyRecipeDatabase(recipeFilename, totalResults, startIndex):
	# Set up loop parameters.  
	numSteps = getNumSteps(totalResults)
	recipeDatabase = {}
	# Loops once for every YUM_STEPS recipes.
	for i in range(numSteps):
		brokeRequest = True
		start, maxResults = indexedGetStartAndMaxResults(i, numSteps, totalResults, startIndex)
		processUpdateStatement = "... Processing recipes: %d to %d ..." % (start + 1, start + maxResults)
		sys.stdout.write(processUpdateStatement +  '\n')

		while brokeRequest:
			apiSearchString = "http://api.yummly.com/v1/api/recipes?_app_id=%s&_app_key=%s&q=&allowedCourse[]=%s&maxResult=%d&start=%d" % (YUM_APP_ID, YUM_APP_KEY, c.YUM_ALLOWED_COURSE, maxResults, start)
			searchRequest = util.safeConnect(requests.get, tuple([apiSearchString]))
			if searchRequest == None:
				print "\n\nTHE FOLLOWING RANGE IS BAD: %d to %d" % (start + 1, start + maxResults)
				print "\n\n"
				#EXIT
			brokeRequest = not (searchRequest.status_code == 200)

		# check out BROKEREQUEST!!!
		# Creates recipes dict from the loaded json file
		allRecipes = json.loads(searchRequest.content)
		matches = allRecipes["matches"]
		for recipe in matches:
			recipeName, recipeObj = buildRecipeEntry(recipe)
			if recipeObj == None:
				print "\n\nTHE FOLLOWING RANGE IS BAD: %d to %d" % (start + 1, start + maxResults)
				print "\n\n"
				#EXIT
			recipeDatabase[recipeName] = recipeObj
			
		# Dumps and prints out a .JSON file for every YUM_STEP recipes retrieved.
		jsonRecipeDatabase = json.dumps(recipeDatabase, sort_keys=True, indent=4)
		#Filename is /res/jsonrecipes/jsonrecipe_index, where index is startIndex/100.
		targetFileName = recipeFilename + "_" + str(startIndex/c.YUM_STEP + i) + ".json"
		allRecipesFile = open(targetFileName, 'a')
		allRecipesFile.write(jsonRecipeDatabase)
		allRecipesFile.close()
		#Adding to clears dict so that next iteration will print clean.
		recipeDatabase.clear()


# Function: createOnlyRecipeDatabase
# ---------------------
# Creates the Recipe and the Nutritional Databases and store them in the
# respective files in json format.
def createOnlyRecipeDatabase(recipeFilename, nutritionalFileName, numRecipes, startIndex):
	buildOnlyRecipeDatabase(recipeFilename, numRecipes, startIndex)

# Function: createOnlyRecipeDatabase
# ---------------------
# Creates the Recipe and the Nutritional Databases and store them in the
# respective files in json format.
def createOnlyNutrientDatabase():
	print "creatingNutrientDatabase!"
	#aliasList = ["white rice", "chocolate", "parmesan cheese", "salsa", "peas", "couch", "horse", "wall"]
	aliasList = util.listAllAliases()
	hitIngredientCount = 0
	missedIngredientCount = 0
	filename = "nutrientTestRead"
	addIngredientToNutritionalList(aliasList)
	print foundIngredients
	#buildNutritionalDatabase(aliasList, filename)
	#buildOnlyRecipeDatabase(recipeFilename, numRecipes, startIndex)





###########################################################
###############   DEPRECATED FUNCTIONS   ##################
###########################################################



# Function: [DEPRECATED] getStartAndMaxResults
# ---------------------
# Quick calculations to return the start number and the
# maxResults number given the iteration we are in and the
# totalResults.
def getStartAndMaxResults(i, numSteps, totalResults):
	start = c.YUM_STEP * i + startNumber #Added offset into the recipe lists.
	maxResults = c.YUM_STEP
	if i == numSteps - 1:
		maxResults = totalResults - start
	if totalResults < YUM_STEP:
		maxResults = totalResults
	return start, maxResults


# Function: [DEPRECATED] createDatabases
# ---------------------
# Creates the Recipe and the Nutritional Databases and store them in the
# respective files in json format.
def createDatabases(recipeFilename, nutritionalFileName, numRecipes):
	buildRecipeDatabase(recipeFilename, numRecipes)
	print
	buildNutritionalDatabase(foundIngredients, nutritionalFileName)
	print
	print "The recipe and nutritional databases are ready to go! Access them at %s and %s, respectively" % (recipeFilename, nutritionalFileName)
	print

# Function: [DEPRECATED] buildRecipeDatabase
# ---------------------
# Since the Yummly Search API only returns ~150 items at a time successfuly, we
# break down our totalResults number into smaller chunks of YUM_STEP, and loop
# through the necessary number of chunks, where at each iteration we make a API
# search request and add the recipe to the @recipeDatabase. Finally, once we get all
# totalResults recipe, we store the recipeDatabase in json format in the file with
# filename.
def buildRecipeDatabase(recipeFilename, totalResults):
	print "... Creating Recipe Database with %d recipes ..." % totalResults

	numSteps = getNumSteps(totalResults)
	recipeDatabase = {}
	count = 0

	for i in range(numSteps):
		brokeRequest = True
		start, maxResults = getStartAndMaxResults(i, numSteps, totalResults)
		print "... Processing recipes: %d to %d ..." % (start + 1, start + maxResults)
		# print "... start: %d, maxResults: %d ..." % (start, maxResults)
		# allRecipesFile = open(recipeFilename, 'a')
		while brokeRequest:
			apiSearchString = "http://api.yummly.com/v1/api/recipes?_app_id=%s&_app_key=%s&q=&allowedCourse[]=%s&maxResult=%d&start=%d" % (YUM_APP_ID, YUM_APP_KEY, c.YUM_ALLOWED_COURSE, maxResults, start)
			searchRequest = util.safeConnect(requests.get, tuple([apiSearchString]))	
			brokeRequest = not (searchRequest.status_code == 200)
		# check out BROKEREQUEST!!!
		allRecipes = json.loads(searchRequest.content)
		matches = allRecipes["matches"]
		for recipe in matches:
			recipeName, recipeObj = buildRecipeEntry(recipe)
			recipeDatabase[recipeName] = recipeObj
			count += 1
			if c.PRINT_RECIPE_IN_DATABASE:
				print "--> recipe %d: %s" % (count, recipeName)
				print "--> len of recipeDatabase = %d" % len(recipeDatabase)

	jsonRecipeDatabase = json.dumps(recipeDatabase, sort_keys=True, indent=4)
	print "--> len of recipeDatabase = %d" % len(recipeDatabase)
	allRecipesFile = open(recipeFilename + ".json", 'a')
	allRecipesFile.write(jsonRecipeDatabase)
	allRecipesFile.close()

	print "... Done creating Recipe Database with %d recipes ..." % totalResults
