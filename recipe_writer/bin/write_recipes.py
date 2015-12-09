import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time
import tokenize, re, string
import json, unicodedata
import thread

##
# Function: main
# --------------
#
##
def main(argv):
	print os.listdir(PATH_TO_ALIASDATA)