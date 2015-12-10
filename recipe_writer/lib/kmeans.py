##
# File: kmeans.py
# ---------------
#
##

import collections
import os, importlib
import json, unicodedata

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

# NOTE
# measurements = [
# 	{'city': 'Dubai', 'temperature': 33.},
# 	{'city': 'London', 'temperature': 12.},
# 	{'city': 'San Fransisco', 'temperature': 18.},
# 	]

def testDatapoints():
	# sparse matrix, shape = (n_samples, n_features)
	allPoints = [
		{'0':0, '1':0},
		{'0':2, '1':0},
		{'0':10, '1':0},
		{'0':12, '1':0},
		]

	# loadJSON file and store it in global variable, to be passed to kmeans algorithm

	vec = DictVectorizer()
	dataMatrix = vec.fit_transform(allPoints)

	return dataMatrix

def createDatapoints(jsonFilePath):
	# sparse matrix, shape = (n_samples, n_features)
	allPoints = []

	allRecipes = util.loadJSONDict(jsonFilePath)

	print allRecipes

	# loadJSON file and store it in global variable, to be passed to kmeans algorithm

	# vec = DictVectorizer()
	# dataMatrix = vec.fit_transform(allPoints)

	# return dataMatrix

	return None

def cluster(jsonFilePath, K):
	'''
    datapoints: list of datapoints, each datapoint is a string-to-double dict representing a sparse vector.
    K: number of desired clusters. Assume that 0 < K <= |datapoints|.
    maxIters: maximum number of iterations to run for (you should terminate early if the algorithm converges).
    Return: (length K list of cluster centroids,
            list of assignments, (i.e. if datapoints[i] belongs to centers[j], then assignments[i] = j)
            final reconstruction loss)
    '''
	# dataMatrix = createDatapoints(jsonFilePath)
	dataMatrix = testDatapoints()
	est = KMeans(n_clusters = K)
	est.fit_predict(dataMatrix)

	print est.cluster_centers_
	print 30 * '-'
	print est.labels_
	print 30 * '-'
	print est.inertia_

def run(verbose):

	print "hello cluster_kmeans.py"
	print 30 * '*'

	# jsonFilePath = os.path.join(c.PATH_TO_ROOT, "res", "allRecipes.json")

	cluster('test', 2)


