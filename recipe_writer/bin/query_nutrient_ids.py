'''
Random Recipe CS 221 Final Project
Austin Ray, Bruno De Martino, Alex Lin
'''

import math, random, collections, sys, time, os, threading
import lib.database as database
import lib.constants as c


def main(argv):
	database.setConstants()
	database.createNutrientIDFiles()

if __name__ == "__main__":
    main(sys.argv)
