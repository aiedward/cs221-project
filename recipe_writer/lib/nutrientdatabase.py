import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
from lib import util
from lib import constants as c

STANDARD_GRAMS = 100 #everything is given with this

class NutrientDatabase:
    def __init__(self):
        #Initializes copy of dictionary from json into working memory
        nutrientDataDictFilePath = os.path.join(c.PATH_TO_RESOURCES, "allNutrientData.json")
        validIngredientsFilePath = os.path.join(c.PATH_TO_RESOURCES, "validIngredients.json")
        validNutrientFilePath = os.path.join(c.PATH_TO_RESOURCES, "validNutrients.json")

        self.nutrientDict = util.loadJSONDict(nutrientDataDictFilePath)
        self.validIngredientDict = util.loadJSONDict(validIngredientsFilePath)
        self.validNutrientsDict = util.loadJSONDict(validNutrientFilePath)


    ##
    # Function: getCalories
    # --------------------------------
    # Returns the number of calories per 100g of a given ingredient
    ##
    def getCalories(self, ingredient):
        if not self.isValidIngredient(ingredient):
            return None  
        return self.nutrientDict[ingredient]['nutrients']['energy'][0]
    
    ##
    # Function: getNutrientFromGrams
    # --------------------------------
    # Returns a unitless value of the specified nutrient given a value
    # in grams.
    #
    # i.e. how many calories are in 10 g of flour?
    ##
    def getNutrientFromGrams(self, grams, ingredient, nutrient):
        # Special case, for ease of use.
        if nutrient == 'calories':
            nutrient = 'energy'

        if not self.isValidIngredient(ingredient):
            return None
        if not self.isValidNutrient(nutrient):
            return None
        return float(grams*self.getNutrient(ingredient, nutrient)/STANDARD_GRAMS)

    ##
    # Function: getNutrientFromUnit
    # --------------------------------
    # Returns a unitless value of the specified nutrient given a amount
    # in a certain unit, and that unit.
    #
    # i.e. how many calories are in 10 g of flour?
    ##
    def getNutrientFromUnit(self, amount, ingredient, nutrient, unit):
        # Special case, for ease of use.
        if nutrient == 'calories':
            nutrient = 'energy'
        if not self.isValidIngredient(ingredient):
            return None
        if not self.isValidNutrient(nutrient):
            return None
        if not self.isValidConversionUnit(ingredient, unit):
            return None

        return float(amount*self.getNutrient(ingredient, nutrient)* \
            self.getConversionFactor(ingredient, unit)/STANDARD_GRAMS)

    ##
    # Function: getNutrient
    # --------------------------------
    # Returns the amount of a nutrient in an ingredient as a unitless
    # value per 100g.  Call getNutrientUnit to see it. Returns an error
    # if either the ingredient or the nutrient is not found.
    ##    
    def getNutrient(self, ingredient, nutrient):
        if not self.isValidIngredient(ingredient):
            return None
        if not self.isValidNutrient(nutrient):
            return None
        return float(self.nutrientDict[ingredient]['nutrients'][nutrient][0])
    
    ##
    # Function: getNutrientUnit
    # --------------------------------
    # Returns the unit of a nutrient in an ingredient as a unitless
    # value. Returns an error if either the ingredient or the nutrient
    # is not found.
    ##    
    def getNutrientUnit(self, ingredient, nutrient):
        if not self.isValidIngredient(ingredient):
            return None
        if not self.invalidNutrient(nutrient):
            return None
        return float(self.nutrientDict[ingredient]['nutrients'][nutrient][1])

    ##
    # Function: getConversionFactor
    # --------------------------------
    # Returns a float that is used to convert a unit of an ingredient
    # to the equivalent amount of grams of that ingredient.  i.e.
    # getConversionFactor("water", "cup") = 245 (grams)
    ##
    def getConversionFactor(self, ingredient, unit):
        if not self.isValidIngredient(ingredient):
            return None
        gramsPerUnit =  float(self.nutrientDict[ingredient]['measure'][unit])
        return gramsPerUnit

    ##
    # Function: numValidIngredients
    # --------------------------------
    # Returns the number of valid ingredients.
    ##    
    def getNumValidIngredients(self):
        return len(self.validIngredientDict)

    ##
    # Function: numValidNutrients
    # --------------------------------
    # Returns the number of valid nutrients
    ##
    def getNumValidNutrients(self):
        return len(self.validNutrientsDict)

    ##
    # Function: isValidIngredient
    # --------------------------------
    # Returns whether or not the ingredient supplied has nutritional data
    ##
    def isValidIngredient(self, ingredient):
        return ingredient in self.validIngredientDict

    ##
    # Function: isValidNutrient
    # --------------------------------
    # Returns whether or not the nutrient supplied is valid
    ##
    def isValidNutrient(self, nutrient):
        return nutrient in self.validNutrientsDict

    ##
    # Function: listConversionUnits
    # --------------------------------
    # Given an ingredient, returns the list of types of units it has been seen in
    # i.e. ["cup", "teaspoon", "tablespoon"]
    ##
    def listConversionUnits(self, ingredient):
        if not self.isValidIngredient(ingredient):
            return None
        return self.nutrientDict[ingredient]['measure'].keys()

    ##
    # Function: isValidConversionUnit
    # --------------------------------
    # Given an ingredient and a unit, returns whether or not the ingredient
    # has been seen with that unit.
    ##
    def isValidConversionUnit(self, ingredient, unit):
        if not self.isValidIngredient(ingredient):
            return None
        return unit in self.nutrientDict[ingredient]['measure']



