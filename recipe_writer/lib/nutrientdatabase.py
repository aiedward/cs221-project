import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata

from lib import constants as c
import util

STANDARD_GRAMS = 100 #everything is given with this
CALORIES_PER_GRAM_FAT = 9 #Taken from internet info
CALORIES_PER_GRAM_SUGAR = 3.87

class NutrientDatabase:
    def __init__(self):
        #Initializes copy of dictionary from json into working memory
        nutrientDataDictFilePath = os.path.join(c.PATH_TO_RESOURCES, "allNutrientData.json")
        validIngredientsFilePath = os.path.join(c.PATH_TO_RESOURCES, "validIngredients.json")
        validNutrientFilePath = os.path.join(c.PATH_TO_RESOURCES, "validNutrients.json")
        unitLookupFilePath = os.path.join(c.PATH_TO_RESOURCES, "nutrientUnits.json")

        self.nutrientDict = util.loadJSONDict(nutrientDataDictFilePath)
        self.validIngredientDict = util.loadJSONDict(validIngredientsFilePath)
        self.validNutrientsDict = util.loadJSONDict(validNutrientFilePath)
        self.unitLookupDict = util.loadJSONDict(unitLookupFilePath)

        conversionDict = util.createWaterConversionDict()

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
    # i.e. Given [five] grams of [butter], how many [calories] are there?
    # returns the number of calories
    ##
    def getNutrientFromGrams(self, grams, ingredient, nutrient):
        # Special case, for ease of use.
        nutrient = self.translateNutrient(nutrient)

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
    # i.e. How much [sodium] is in [one] [stick] of [butter]
    ##
    def getNutrientFromUnit(self, nutrient, amount, unit, ingredient):
        nutrient = self.translateNutrient(nutrient)

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
        nutrient = self.translateNutrient(nutrient)
        if not self.isValidIngredient(ingredient):
            return None
        if not self.isValidNutrient(nutrient):
            return None
        return float(self.nutrientDict[ingredient]['nutrients'][nutrient][0])
    
    ##
    # Function: getNutrientUnit
    # --------------------------------
    # Returns the unit of a nutrient in an ingredient
    # Returns an error if either the ingredient or the nutrient
    # is not found.
    ##    
    def getNutrientUnit(self, nutrient):
        nutrient = self.translateNutrient(nutrient)
        return self.unitLookupDict[nutrient]


    def getPercentage(self, inputString, ingredient):
        words = inputString.split('_')
      
        #Special Cases
        if inputString == 'caloriesfromfat':
            return self.getPercentageCaloriesFromFat(ingredient)
        if len(words) > 1:
            command = words[0]
            print words[1]
            nutrient = self.translateNutrient(words[1])
            if command == 'dailyvalues':
                return self.getPercentDailyValuesPerGram(ingredient, nutrient)
            if command == 'absolutedailyvalues':
                # Second input is mass in grams to calculate
                if len(words) == 2:
                    return float(words[2])*self.getPercentDailyValuesPerGram(ingredient, nutrient)

            if command == 'mass':
                return self.getNutrient(ingredient, nutrient)
        return None
        
    ##
    # Function: getPercentageCaloriesFromFat:
    # --------------------------------
    # Returns the percentage of calories from fat for a given ingredient.
    # i.e. 78% (78)
    ##    
    def getPercentageCaloriesFromFat(self, ingredient):
        if not self.isValidIngredient(ingredient):
            return None
        calories = float(self.getCalories(ingredient))
        gramsFat = self.getNutrient(ingredient, 'total lipid (fat)')
        return float(100*(gramsFat * CALORIES_PER_GRAM_FAT)/calories)
    
    ##
    # Function: getPercentageDailyValuesPerGram
    # --------------------------------
    # Returns the percentage of your daily value of a nutrient you get per
    # gram of a selected ingredient.  Returns null on error, negative if
    # we dont have a daily value for the nutrient
    #

    def getPercentDailyValuesPerGram(self, ingredient, nutrient):
        nutrient = self.translateNutrient(nutrient)
        if not self.isValidIngredient(ingredient):
            return None
        nutrientValuePerGram = self.getNutrient(ingredient, nutrient)/STANDARD_GRAMS
        return nutrientValuePerGram/self.validNutrientsDict[nutrient]



#######################################
#############   Helpers ###############
#######################################
    ##
    # Function: translateNutrient
    # --------------------------------
    # Translates special case nutrients to make communication easier
    ##
    def translateNutrient(self, potentialNutrient):
        # Special case, for ease of use.
        if potentialNutrient == 'calories' or potentialNutrient == 'kcal':
            return 'energy'
        if potentialNutrient == 'fat':
            return 'total lipid (fat)'
        if potentialNutrient == 'carbs':
            return 'carbohydrate, by difference'
        for key in self.validNutrientsDict:
            if potentialNutrient in key:
                #print key
                return key
        return potentialNutrient


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
        if unit in self.nutrientDict[ingredient]['measure']:
            gramsPerUnit = float(self.nutrientDict[ingredient]['measure'][unit])
        else:
            gramsPerUnit = float(self.conversionDict[unit])
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
        try:
            return self.nutrientDict[ingredient]['measure'].keys()
        except KeyError:
            return None

    ##
    # Function: isValidConversionUnit
    # --------------------------------
    # Given an ingredient and a unit, returns whether or not the ingredient
    # has been seen with that unit.
    ##
    def isValidConversionUnit(self, ingredient, unit):
        if not self.isValidIngredient(ingredient):
            return None
        try:
            return unit in self.nutrientDict[ingredient]['measure']
        except KeyError:
            return None