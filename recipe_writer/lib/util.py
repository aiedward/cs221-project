##
# File: /lib/util.py
# ------------------
# Commonly used functions.
##

import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
import thread

##
# Function: loadJSONDict
# ----------------------
# Loads a JSON file into a python dictionary and returns that dictionary.
##
def loadJSONDict(jsonFilePath):
	# Read in the JSON file containing recipe data
	fullJsonString = None
	with open(jsonFilePath, 'r') as f:
		fullJsonString = f.read()

	# This is dead code I was trying to use to remove all escaped unicode
	# characters (e.g. \u00bd) or convert them to ascii
	#noUnicodeJsonString = fullJsonString.decode('unicode_escape').encode('ascii','ignore')
	#asciiJsonString = fullJsonString.decode('unicode-escape')

	# Read the JSON file in as a dictionary
	d = json.JSONDecoder()
	return d.decode(fullJsonString)

##
# Function: dumpDictToJSONFile
# ----------------------------
# Writes a dictionary to a JSON file with the full path 'fullFilePath'
##
def dumpJSONDict(fullFilePath, dict2dump):
	jsonDatabase = json.dumps(dict2dump, sort_keys=True, indent=4)
	with open(fullFilePath, "w") as f:
		f.write(jsonDatabase)