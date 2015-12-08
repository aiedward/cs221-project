'''
Random Recipe CS 221 Final Project
Austin Ray, Bruno De Martino, Alex Lin
'''

import collections, requests, json

YUM_APP_ID = "4d1d7424"
YUM_APP_KEY = "419a5ef2649eb3b6e359b7a9de93e905"
YUM_STEP = 100
YUM_ALLOWED_COURSE = "course^course-Main Dishes"

GOV_NUT_API_KEY = "5YbfzajkZSaGWi7hibcD4Nq1EXSGHRtZP5Pvlkvv"

allIngredientIds = {}
missedIngredients = []
foundItems = 0
missedItems = 0

def printMissedIngredients():
	print "These are the ingredients that do not exist in the government Nutritional Database:"
	for ingredient in missedIngredients:
		print ingredient


def addIngredientToNutritionalList(ingredients):
	global foundItems
	global missedItems
	
	for ingredient in ingredients:
		apiSearchString = "http://api.nal.usda.gov/ndb/search/?format=json&q=%s&max=1&api_key=%s" % (ingredient, GOV_NUT_API_KEY)
		searchRequest = requests.get(apiSearchString)
		if searchRequest.status_code == 200:
			nutritionalResults = json.loads(searchRequest.content)
			ingredientId = nutritionalResults["list"]["item"][0]["ndbno"]
			if ingredient not in allIngredientIds:
				allIngredientIds[ingredient] = ingredientId
				foundItems += 1
		else:
			if ingredient not in missedIngredients:
				missedIngredients.append(ingredient)
				missedItems += 1


def buildNutritionalDatabase(ingredientNameIdMap, filename):
	numIngredients = len(ingredientNameIdMap)
	allNutritionalFile = open(filename, 'w+')
	nutritionalDatabase = {}
	print "... Creating Nutritional Database with %d items ..." % numIngredients
	for ingredientName, ingredientId in ingredientNameIdMap.iteritems():
		apiGetString = "http://api.nal.usda.gov/ndb/reports/?ndbno={0}&type=b&format=json&api_key={1}".format(ingredientId, GOV_NUT_API_KEY)
		getRequest = requests.get(apiGetString)
		assert getRequest.status_code == 200
		getFood = json.loads(getRequest.content)
		foodCalories = getFood['report']['food']['nutrients'][1]
		nutritionalDatabase[ingredientName] = {'ingredientName': ingredientName, 'ingredientId': ingredientId, 'foodCalories': (foodCalories['value'], foodCalories['unit'], foodCalories['measures'])}

	jsonNutritionalDatabase = json.dumps(nutritionalDatabase, sort_keys=True, indent=4)
	allNutritionalFile.write(jsonNutritionalDatabase)
	allNutritionalFile.close()
	print "... Done creating Nutritional Database with %d items ..." % numIngredients

	print " Out of all ingredient in our recipe, we found %d of them, and missed %d of them" % (foundItems, missedItems)
	print


def buildRecipeEntry(recipe):
	recipeName = recipe["recipeName"]
	recipeId= recipe["id"]
	ingredients = recipe["ingredients"]
	addIngredientToNutritionalList(ingredients)

	apiGetString = "http://api.yummly.com/v1/api/recipe/%s?_app_id=4d1d7424&_app_key=419a5ef2649eb3b6e359b7a9de93e905" % recipeId
	getRequest = requests.get(apiGetString)
	assert getRequest.status_code == 200
	getRecipe = json.loads(getRequest.content)
	ingredientLines = getRecipe["ingredientLines"]

	return recipeName, {'recipeName': recipeName, 'recipeId': recipeId, 'ingredients':ingredients, 'ingredientLines':ingredientLines}


def buildRecipeDatabase(recipeFilename, totalResults):
	print "... Creating Recipe Database with %d recipes ..." % totalResults

	numSteps = totalResults/YUM_STEP
	if totalResults % YUM_STEP != 0: 
		numSteps += 1
	recipeDatabase = {}
	allRecipesFile = open(recipeFilename, 'w+')

	for i in range(numSteps):
		start = YUM_STEP * i
		maxResults = YUM_STEP
		if i == numSteps - 1:
			maxResults = totalResults - start + 1
		if totalResults < YUM_STEP:
			maxResults = totalResults

		print "... Processing recipes: %d to %d ..." % (start + 1, start + maxResults)
		
		apiSearchString = "http://api.yummly.com/v1/api/recipes?_app_id=%s&_app_key=%s&q=&allowedCourse[]=%s&maxResult=%d&start=%d" % (YUM_APP_ID, YUM_APP_KEY, YUM_ALLOWED_COURSE, maxResults, start) 
		searchRequest = requests.get(apiSearchString)
		assert searchRequest.status_code == 200
		
		allRecipes = json.loads(searchRequest.content)
		matches = allRecipes["matches"]

		for recipe in matches:
			recipeName, recipeObj = buildRecipeEntry(recipe)
			recipeDatabase[recipeName] = recipeObj
	
	jsonRecipeDatabase = json.dumps(recipeDatabase, sort_keys=True, indent=4)
	allRecipesFile.write(jsonRecipeDatabase)
	allRecipesFile.close()

	print "... Done creating Recipe Database with %d recipes ..." % totalResults


def createDatabases(recipeFilename, nutritionalFileName, numRecipes):
	buildRecipeDatabase(recipeFilename, numRecipes)
	print
	buildNutritionalDatabase(allIngredientIds, nutritionalFileName)
	print
	print "The recipe and nutritional databases are ready to go! Access them at %s and %s, respectively" % (recipeFilename, nutritionalFileName)


# TODO: need to figure out a way to not go over 1000 API calls/hour from government, by checking request header and not making
# call if it will make it go over our hourly limit