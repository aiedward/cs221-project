'''
Random Recipe CS 221 Final Project
Austin Ray, Bruno De Martino, Alex Lin
'''

import math, random, collections, sys, time, os, threading
import lib.database as database
import lib.constants as c




recipesInDatabase = False
remainingCalls = False
missedIngredients = False
allRecipesFilename = 'allRecipes.json'
allNutritionalFilename = 'allNutritional.json'
apiNum = 0


def main(argv):
	recipes = False
	recipesInDatabase = False
	remainingCalls = False
	missedIngredients = False
	allRecipesFilename = 'allRecipes.json'
	allNutritionalFilename = 'allNutritional.json'
	apiNum = 0
	numRecipes = 500
	startNum = 0



	if recipes:
		if argv[1] == "-d":
			#Automatically sets default values 
			print "Default settings chosen."
			numRecipes = 10000
			pass
		else:
			print "Standard Input Flag Chosen"
			#These calls are Bruno's original functions / option flags to process the file.  Original approach was to download one recipe, download all the
			#ingredients for that recipe, repeat.  This version separates the two, polling basically unlimited requests from Yummly for recipes.  Evening of 12/9
			#Alex plans on porting the code for the Yummly requests to the nutritional databse.
			recipesInDatabase = raw_input('Show print line per recipe added on database?: ') in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
			remainingCalls = raw_input('Show print line per time Gov Database is accessed?: ') in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
			missedIngredients = raw_input('Show print line per ingredient missed?: ') in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']

			#Bruno's original implementation called the suffix here, mine has a constant string that's appended on inside createOnlyRecipeDatabase
			allRecipesFilename = raw_input('Filename to store all recipes (in JSON format): ')# + ".json" 
			allNutritionalFilename = raw_input('Filename to store all nutritional ingredient information (in JSON format): ')# + ".json"

			#Used for selecting the API Key from an array of our available API keys, so we can get k*1000 requests/hour if we need
			#This isn't fully implemented yet, will probably end up compiling it into some threaded approach to pulling the nutritional database.
			apiNum = int(raw_input('API Number: '))

		#These are the two critical calls for setting up the Recipe JSON files.  You give it the number of recipes that you want to get total (in a multiple of 100
		#that's divisible by the numThreads (in this case 2), and it'll break it up for you automatically between the threads.
		#You need to manually set the Starting Recipe Number to the number of the last file loaded * 100.  (If last file is jsonrecipe_1002, your start number is 100200)
		startNum = int(raw_input('Starting Recipe number: '))
		numRecipes = int(raw_input('Number of recipes (multiple of 100): '))

		database.setConstants(recipesInDatabase, remainingCalls, missedIngredients, apiNum, startNum)
		
		#This is commented out, but now taken care of by the threads, left as a prototype for reference.
		#database.createDatabases(allRecipesFilename, allNutritionalFilename, numRecipes)
		start_time = time.time()
		allRecipesFilename = os.path.join(c.PATH_TO_RESOURCES, "jsonrecipes", "recipeDownload")


		#This section is all thread-related administrativa.  The two things you need to know are the function
		#being called, createOnlyRecipeDatabase, which queries the Yummly database for recipes
		#(see documentation in database.py), and how the threads/numRecipes work.
		#################################################
		# Specify the number of threads you want to use, 
		numThreads = 2
		#
		numRecipesPerThread = numRecipes/numThreads
		threads = []
		for i in xrange(numThreads):
			threadName = "Thread-" + str(i)
			# Create a new thread that, when its start() method is called, will
			# execute target(args)

			newThread = threading.Thread(\
				target=database.createOnlyRecipeDatabase, 
				args=(allRecipesFilename, allNutritionalFilename, numRecipesPerThread, startNum + numRecipesPerThread*i)\
			)

			# Append the new thread to the list of all threads
			# (you must keep track of all active threads)
			threads.append(newThread)

		# Start new Threads
		for t in threads:
		    t.start()

		# Wait for all threads to finish
		for t in threads:
		    t.join()

		print "Exiting Main Thread"	

		
		#################################################

		# database.printMissedIngredients()
		print("--- %s seconds ---" % (time.time() - start_time))
	else:
		database.setConstants(recipesInDatabase, remainingCalls, missedIngredients, apiNum, startNum)
		database.createOnlyNutrientDatabase()