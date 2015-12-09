'''
Random Recipe CS 221 Final Project
Austin Ray, Bruno De Martino, Alex Lin
'''

import math, random, collections, requests, json

# Function: Create Recipe Database
# -----------------------
# Access the Yummly API, and does an empty search for maxResults. Then, it writes 
# all recipes from that query on the file specified by filename
#
# maxResults: max number of recipes from Yummly database
# filename: name of the file the recipes will be written into
# See example at: https://developer.yummly.com/documentation/search-recipes-response-sample
def createRecipeDatabase(filename, maxResults):
	apiString = "http://api.yummly.com/v1/api/recipes?_app_id=4d1d7424&_app_key=419a5ef2649eb3b6e359b7a9de93e905&q=&maxResult=%d" % maxResults
	request = requests.get(apiString)
	assert request.status_code == 200
	print request.headers
	allRecipesFile = open(filename, 'w+')
	allRecipesFile.write(request.content)
	allRecipesFile.close()

# Function: Create Nutritional Database
# -----------------------
# 
def createNutritionalDatabase(filename, maxResults):
	assert maxResults <= 1500
	apiString = "http://api.nal.usda.gov/ndb/list?format=json&lt=f&max=%d&sort=n&api_key=5YbfzajkZSaGWi7hibcD4Nq1EXSGHRtZP5Pvlkvv" % maxResults
	request = requests.get(apiString)
	assert request.status_code == 200
	allNutritionalFile = open(filename, 'w+')
	allNutritionalFile.write(request.content)
	allNutritionalFile.close()

# Function: Test Recipe Database
# -----------------------
# Calls createRecipeDatabase with filename 'allRecipes.json' and maxResults = 100,
# then proceeds to print all ingredients from each recipe fetched
#
# maxResults: max number of recipes from Yummly database
# filename: name of the file the recipes will be written into
# See example at: https://developer.yummly.com/documentation/search-recipes-response-sample
def testRecipeDatabase():
	filename = 'allRecipes.json'
	createRecipeDatabase(filename, 100)
	readFile = open(filename)
	allRecipes = json.loads(readFile.read())

	matches = allRecipes["matches"]
	count = 0
	for recipe in matches:
		print "********** %d *********" % count
		ingredients = recipe["ingredients"]
		for ingredient in ingredients:
			print ingredient
		print "********** %d *********" % count
		count += 1

# Function: Test Nutritional Database
# -----------------------
# 
def testNutritionalDatabase():
	filename = 'allNutritional.json'
	createNutritionalDatabase(filename, 100)
	readFile = open(filename)
	allNutritional = json.loads(readFile.read())
	foodList = allNutritional["list"]
	items = foodList["item"]
	for itemObject in items:
		itemName = itemObject["name"]
		itemId = itemObject["id"] 
		print itemName + ": " + itemId


# TODO: since neither API let's me call the WHOLE database, I need to figure out a way to do
# several small calls, and be able to merge them in my allRecipes.json and allNutritional.json
# finals, so they only have one master object each.




