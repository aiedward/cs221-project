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

# Function: getNextAPIKeyIndex
# ---------------------
# Returns the next key, or stays at the same one
# and set the global shouldCycleAPIKeys if all the keys
# in the loop have been used up and we're ACTUALLY waiting.

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

# Function: setConstants
# ---------------------
# Sets initial values for the globals
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
# of ingredient -> foundIngredients.  We periodically save and dump this as a json
# for every YUM_STEP ingredients either found or missed to be consolidated later.
def addIngredientToNutritionalList(ingredients):
	global shouldCycleAPIKeys
	global lastSuccessfulAPIKeyIndex
	global lastAPIKeyIndex
	global currentAPIKey

	foundIngredients = {}
	missedIngredients = {}
	
	foundIngredientsFilename = os.path.join(c.PATH_TO_RESOURCES, "nutrients", "foundingredients", "foundingredients")
	missedIngredientsFilename = os.path.join(c.PATH_TO_RESOURCES, "nutrients", "missedingredients", "missedingredients")
	foundFileCount = 0
	missedFileCount = 0
	
	#Loops trough a sorted list of ingredients, printing the index along the way (can restart if necessary on failure.)
	for i in range(0, len(ingredients)):
		ingredient = ingredients[i]
		print "Ingredient #" + str(i)
		#nutritionalSearch makes all the API calls
		foundIngredient, searchRequest = nutritionalSearch(ingredient)

		# If sucessfully pulled the ID of the ingredient from the online databse, 
		if foundIngredient:
			nutritionalResults = json.loads(searchRequest.content)
			resultList = nutritionalResults.get('list')
			if resultList is not None:
				ingredientId = resultList["item"][0]["ndbno"]
				if ingredient not in foundIngredients:
					foundIngredients[ingredient] = ingredientId
			else:
				print "ERROR, list is None. Check it out the results: %s" % nutritionalResults
				print searchRequest.status_code

		#Otherwise, add the ingredient to the list of misses.
		else:
			if ingredient not in missedIngredients:
				missedIngredients[ingredient] = 0

		#Prints the dictionaries to json files if they are of size YUM_STEP
		if shouldWriteJSON(foundingredients):
			writeSegmentedJSONFile(foundingredients, foundIngredientsFilename, foundFileCount)
			#Adding to clears dict so that next iteration will print clean.
			foundIngredients.clear()
			foundFileCount += 1
		if shouldWriteJSON(missedingredients):
			writeSegmentedJSONFile(missedingredients, missedIngredientsFilename, missedFileCount)
			missedIngredients.clear()
			missedFileCount += 1
	#Write anything that hasn't yet been written.
	writeSegmentedJSONFile(foundingredients, foundIngredientsFilename, foundFileCount)
	writeSegmentedJSONFile(missedingredients, missedIngredientsFilename, missedFileCount)

def shouldWriteJSON(dictToTest):
    if len(dictToTest) % c.YUM_STEP == 0 and len(dictToTest) != 0:
        return True
    return False

def writeSegmentedJSONFile(dictionaryToDump, baseFilename, segmentIndex):
	# Dumps and prints out a .JSON file for every YUM_STEP recipes retrieved.
	jsonToWrite = json.dumps(dictionaryToDump, sort_keys=True, indent=4)
	#Filename is /res/jsonrecipes/jsonrecipe_index, where index is startIndex/100.
	targetFileName = baseFilename + "_" + str(segmentIndex) + ".json"
	writeFile= open(targetFileName, 'w+')
	writeFile.write(jsonToWrite)
	writeFile.close()
	# #Adding to clears dict so that next iteration will print clean.
	# dictionaryToDump.clear()
	# segmentIndex += 1


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

	searchRequest = getSearchRequest(ingredient, currentAPIKey)
	remaining = getRemaining(searchRequest)
	if remaining < 0 or searchRequest is None:
		return False, None

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
				searchRequest = getSearchRequest(ingredient, currentAPIKey)
				remaining = getRemaining(searchRequest)
				if remaining < 0 or searchRequest is None:
					return False, None
			else:
				#Naptime.
				print "SEARCH: Request failed because exceeded Gov 1K API requests/hour"
				print "... Sleeping for 10 min ..."
				time.sleep(c.SLEEP_TIME)
				searchRequest = getSearchRequest(ingredient, currentAPIKey)
				remaining = getRemaining(searchRequest)
				if remaining < 0 or searchRequest is None:
					return False, None

		print "SEARCH: Gov Nutrional Database requests remaining: %d with API Key %s" %	 (remaining, currentAPIKeyIndex)
	
	#Updates variables for proper cycling through API Keys
	lastSuccessfulAPIKeyIndex = currentAPIKeyIndex
	shouldCycleAPIKeys = True
	return True, searchRequest

def getSearchRequest(ingredient, currentAPIKey):
	apiSearchString = "http://api.nal.usda.gov/ndb/search/?format=json&q=%s&max=1&api_key=%s" % (ingredient, currentAPIKey)
	try:
		return requests.get(apiSearchString)
	except requests.exceptions.ConnectionError as e:
		return None

def getRemaining(searchRequest):
	if 'X-RateLimit-Remaining' in searchRequest.headers:
		return int(searchRequest.headers['X-RateLimit-Remaining'])
	return -1

def getDataRequest(ingredientId, currentAPIKey):
	apiGetString = "http://api.nal.usda.gov/ndb/reports/?ndbno={0}&type=b&format=json&api_key={1}".format(ingredientId, currentAPIKey)
	try:
		return requests.get(apiGetString)
	except requests.exceptions.ConnectionError as e:
		return None
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

	getRequest = getDataRequest(ingredientId, currentAPIKey)
	remaining = getRemaining(getRequest)
	if remaining < 0 or getRequest is None:
		return None

	#On failure, Notify and either return/break on error, or loop API keys if waiting for the API limit to refresh.
	while getRequest.status_code != 200:
		print "[BROKE REQUEST] Status code != 200"
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
				getRequest = getDataRequest(ingredientId, currentAPIKey)
				remaining = getRemaining(getRequest)
				if remaining < 0 or getRequest is None:
					return None
			else:
				print "GET: Request failed because exceeded Gov 1K API requests/hour"
				print "... Sleeping for 10 min ..."
				time.sleep(c.SLEEP_TIME)
				getRequest = getDataRequest(ingredientId, currentAPIKey)
				remaining = getRemaining(getRequest)
				if remaining < 0 or getRequest is None:
					return None
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
def buildNutritionalDatabase(ingredientNameIdMap):
	nutrientFilename = os.path.join(c.PATH_TO_RESOURCES, "nutrients", "nutrientdata", "nutrientdata")
	numIngredients = len(ingredientNameIdMap)
	print "... Creating Nutritional Database with %d items ..." % numIngredients

	nutritionalDatabase = {}
	nutrientFileCount = 0
	numLoaded = 0
	for ingredientName in ingredientNameIdMap:
		ingredientId = ingredientNameIdMap[ingredientName].encode('ascii', errors='ignore')
		print "Getting data for ingredient ID %s, (%d/%d) complete" % (ingredientId, numLoaded, numIngredients)
		getRequest = getNutritionalRequest(ingredientId)
		if getRequest is not None:
			requestAsJson = json.loads(getRequest.content)
			requestAsFormattedDict = nutrientDictFromJSON(requestAsJson)
			nutritionalDatabase[ingredientName] = requestAsFormattedDict
			numLoaded += 1
		#If dictionary threshold of YUM_STEP is reached, output it to a json file.
		if shouldWriteJSON(nutritionalDatabase):
			writeSegmentedJSONFile(nutritionalDatabase, nutrientFilename, nutrientFileCount)
			nutritionalDatabase.clear()
			nutrientFileCount+=1

	# jsonNutritionalDatabase = json.dumps(nutritionalDatabase, sort_keys=True, indent=4)
	# allNutritionalFile = open(filename, 'w+')
	# allNutritionalFile.write(jsonNutritionalDatabase)
	# allNutritionalFile.close()
	print "... Done creating Nutritional Database with %d items ..." % numIngredients

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
def createNutrientIDFiles():
	aliasList = util.listAllAliases()
	aliasList.sort()
	hitIngredientCount = 0
	missedIngredientCount = 0
	print "Number of Ingredients to Query: " + str(len(aliasList))
	addIngredientToNutritionalList(aliasList)
	print foundIngredients

def createNutrientDataJSON():
	nutrientIDsFilePath = os.path.join(c.PATH_TO_RESOURCES, "allNutrientIDs.json")
	nutrientIDs = util.loadJSONDict(nutrientIDsFilePath)
	buildNutritionalDatabase(nutrientIDs)

def hasNumbers(inputString):	
    return any(char.isdigit() for char in inputString)


# Function: nutrientDictFromJSON
# ---------------------
# Given a dict loaded from a json file for a nutrient (basically from the API)
# get request, and returns a unified dict of all the selected nutrient groups:
# (proximates, minerals, vitamins, lipids, amino acids, other)
#
# Returns a dictionary with the nutrient map and conversion values.
# returnDict['nutrients'], returnDict['measure']

def nutrientDictFromJSON(givenIngredient):

    #Flags
    ignoreNumericalLipids = True

    returnDict = {}
    measureDict = {}
    loadedMeasures = False

    #Variables that determine which groups are included
    getProximates = True
    getMinerals = True
    getVitamins = True
    getLipids = True
    getAminoAcids = True
    getOther = True


    nutrientDict = {}
    nutrientDict['proximates'] = {}
    nutrientDict['minerals'] = {}
    nutrientDict['vitamins'] = {}
    nutrientDict['lipids'] = {}
    nutrientDict['amino acids'] = {}
    nutrientDict['other'] = {}

    #Loop through each nutrient in the given ingredient
    for nutrient in givenIngredient['report']['food']['nutrients']:
        nutrientGroup = nutrient['group'].encode('ascii', errors='ignore').lower()
        nutrientName =  nutrient['name'].encode('ascii', errors='ignore').lower()
        nutrientVal = nutrient['value'].encode('ascii', errors='ignore').lower()
        nutrientUnit = nutrient['unit'].encode('ascii', errors='ignore')

        #Saves the nutrient value and unit per 100g
        if ignoreNumericalLipids and nutrientGroup == 'lipids' \
            and hasNumbers(nutrientName):
            continue                

        #Saves the info of the current nutrient to the dictionary
        nutrientDict[nutrientGroup][nutrientName] = tuple((nutrientVal, nutrientUnit))

        #Load the measurement conversions for each ingredient exactly once.
        if not loadedMeasures:
            for measureKey in nutrient['measures']:
                equivUnit = measureKey['label'].encode('ascii', errors='ignore')
                equivValue = measureKey['eqv']
                measureDict[equivUnit] = equivValue
            loadedMeasures = True

    # Creates a merged dictionary based on which groups are selected.
    mergeList = []

    if getProximates: mergeList.append(nutrientDict['proximates'])
    if getMinerals: mergeList.append(nutrientDict['minerals'])
    if getVitamins: mergeList.append(nutrientDict['vitamins'])
    if getLipids: mergeList.append(nutrientDict['lipids'])
    if getAminoAcids: mergeList.append(nutrientDict['amino acids'])
    if getOther: mergeList.append(nutrientDict['other'])

    returnDict['nutrients'] = util.mergeNutrientDicts([mergeList])   
    returnDict['measure'] = measureDict

    # print "\n\n\n"
    # print "Nutrients:"
    # print returnDict['nutrients']
    # print "Conversions:"
    # print returnDict['measure']
    # print "Calories per 100g: " + returnDict['nutrients']['energy'][0] + " " + returnDict['nutrients']['energy'][1]
    

    return returnDict


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
