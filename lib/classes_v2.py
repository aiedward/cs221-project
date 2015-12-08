import collections, itertools, Queue
import numpy, scipy, math, random
import os, sys
import tokenize, re, string



###
### NOTE
### THIS FILE MIGHT NOT BE NECESSARY
###


### Data Structures 
class Ingredient:
    def __init__(self):
        self.amount = ""
        self.units = ""
        self.ingredientName = ""
        self.entireLine = ""          # Contains amount, units, and ingredient name
        self.cleanLine = ""           # Line with the % at the beginning and numbers added
        self.lineWithoutAmount = ""

        self.wordsInIngredient = []            # Vector of strings
        self.cleanWordsInIngredient = []       # Words including '%' and numbers
        self.nonUnitWordsInIngredient = []     # Vector of strings
        self.endSeed = []   

 """
 * Class: Recipe
 * ------------------------------------------------
 * Recipe contains the ingredients, name, serving size
 * and instructions for a recipe. It also implements
 * very useful functions for the whole program.
 """
 class Recipe:
    def __init__(self, jsonData):
        self.jsonData = jsonData


    # Overloads [] operator for Recipe class to just return the same
    # thing called on the recipe's JSON data
    def __getitem__(self, key):
        return self.jsonData[key]