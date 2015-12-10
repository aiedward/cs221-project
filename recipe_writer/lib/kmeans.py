##
# File: kmeans.py
# ---------------
#
##

import collections
import numpy, scipy, math, random
import os, importlib
import json, unicodedata
import pdb

from sklearn.cluster import KMeans
from sklearn.feature_extraction import DictVectorizer
# import matplotlib.pyplot as plt
from lib import util
from lib import constants as c

# NOTE
# K-Means
#     1a. Cluster recipes together based on
#         - flavors
#         - course/meal
#         - common ingredients
#         - subsets of common ingredients like spices, meats, sweets
#         - cooking time
#         - total calories
#         - % calories from fat
#         - # ingredients
#         - average ingredient line length
#     1b. Cluster ingredients together based on
#         - common ingredient/alias buddies 
#           (implemented like synonyms from 107)
#     2.  After clustering
#         - Manually label clusters as mexican/meats/breakfast/etc.

def testDatapoints():
	# sparse matrix, shape = (n_samples, n_features)
	allPoints = [
		{'0':0, '1':0},
		{'0':2, '1':0},
		{'0':10, '1':0},
		{'0':12, '1':0},
		]

	vec = DictVectorizer()
	dataMatrix = vec.fit_transform(allPoints)

	return dataMatrix

def createPoint(recipe):
	point = {}

	cuisine = recipe.get('cuisine')
	flavors = recipe.get('flavors')
	ingredients = recipe['ingredients']

	if cuisine is not None and len(cuisine) > 0:
		for c in cuisine:
			point['cuisine-'+c] = 1

	if flavors is not None and len(flavors) > 0:
		point['bitter'] = flavors['bitter']
		point['meaty'] = flavors['meaty']
		point['piquant'] = flavors['piquant']
		point['salty'] = flavors['salty']
		point['sour'] = flavors['sour']
		point['sweet'] = flavors['sweet']

	point['totalTimeInSeconds'] = recipe['totalTimeInSeconds']
	point['numIngredients'] = len(ingredients)

	for ingredient in ingredients:
		point['ingredient-'+ingredient] = 1

	return point


def createDatapoints(jsonFilePath):
	# sparse matrix, shape = (n_samples, n_features)
	allPoints = []
	pointToRecipeName = {}

	allRecipes = util.loadJSONDict(jsonFilePath)

	count = 0
	for recipeName, recipe in allRecipes.items():
		point = createPoint(recipe)
		allPoints.append(point)
		pointToRecipeName[count] = recipeName
		count += 1

	vec = DictVectorizer()
	dataMatrix = vec.fit_transform(allPoints)

	return dataMatrix, pointToRecipeName

def clusterAssignment(est, pointToRecipeName):
	clusterToRecipes = {}
	labels = est.labels_

	for point, recipeName in pointToRecipeName.iteritems():
		cluster = labels[point]
		clusterRecipeList = clusterToRecipes.get(labels[point])
		if clusterRecipeList is None:
			clusterRecipeList = []
		clusterRecipeList.append(recipeName)
		clusterToRecipes[cluster] = clusterRecipeList

	return clusterToRecipes

def printClusters(clusterToRecipes, est):
	# print 10 * '-' + ' Cluster Centers ' + 10 * '-'
	# print est.cluster_centers_
	# print 10 * '-' + ' Labels ' + 10 * '-'
	# print est.labels_

	for cluster, recipeList in clusterToRecipes.iteritems():
		print 10 * '-' + ' Cluster ' + str(cluster) + ' '+ 10 * '-'
		for recipe in recipeList:
			print recipe
		print

def cluster(jsonFilePath, K):
	'''
	datapoints: list of datapoints, each datapoint is a string-to-double dict representing a sparse vector.
	K: number of desired clusters. Assume that 0 < K <= |datapoints|.
	maxIters: maximum number of iterations to run for (you should terminate early if the algorithm converges).
	Return: (length K list of cluster centroids,
	        list of assignments, (i.e. if datapoints[i] belongs to centers[j], then assignments[i] = j)
	        final reconstruction loss)
	Use dataMatrix = testDatapoints() instead to test.
	'''
	dataMatrix, pointToRecipeName = createDatapoints(jsonFilePath)
	est = KMeans(n_clusters = K)
	est.fit_predict(dataMatrix)
	clusterToRecipes = clusterAssignment(est, pointToRecipeName)
	
	print printClusters(clusterToRecipes, est)
	

def run(verbose=False, K='5', filename='testRecipeTh'):

	numClusters = int(K)
	fullFilename = filename+'.json'

	print '***** Starting Kmeans on ' + fullFilename + '! *****'
	print
	jsonFilePath = os.path.join(c.PATH_TO_ROOT, "res", fullFilename)
	cluster(jsonFilePath, numClusters)

	print
	return '***** Kmeans completed on ' + fullFilename + '! :) *****'

