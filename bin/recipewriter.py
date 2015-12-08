"""
 Authors: Austin Ray, Bruno De Martino, Alex Lin
 File: randomwriter.py
 ---------------------
 This file includes all main code for the recipe writer.
"""

import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys
import tokenize, re, string
from classes import *


# Seed length used for weighted-random-writing ingredient lines of
# already-picked ingredients
seedLength = 2

# Main Program */
def main(argv):
    res_dirName = "res"

    # Number of words at end of ingredient used as seed
    # for picking other ingredients
    endSeedLength = 2

    # Collect a set of adjectives from the ./res/adjectives.txt file
    adjectives = gatherAdjectives(res_dirName)
    
    # Splice out the proper adjectives from the adjectives list
    properAdjectives = [adj for adj in adjectives if adj[0].isupper()]

    # Give the user a quick welcome message
    greetUser()

    # Ask the user if they want the program explained
    # to them or not
    if getStartResponse(argv) == "explain":
        explainProgram()

    # Ask user:
    #   - How many ingredients per recipe?
    #   - How many past ingredients factor in to the next ingredient?
    #   - How many recipes should be made?
    #   - Do you want to print the recipes all at once or one by one?
    numIngredients = getNumIngredientsResponse(argv)
    endSeedSeedLength = getEndSeedLengthResponse(argv)
    numRecipesToPrint = getNumRecipesToPrintResponse(argv)
    # allAtOnce = getAllAtOnceResponse(argv)

    # Update the user on program progress
    printUpdate(0)

    # Separate complete cookbook text into individual recipe chunks
    allRecipes = separateRawRecipeTexts(res_dirName)

    # Parse each individual recipe into its component parts
    splitRecipes(allRecipes, adjectives, endSeedLength)

    # Delete any recipes that only have one ingredient
    deleteOneIngredientRecipes(allRecipes)

    # Update the user on program progress
    printUpdate(1)
    
    # Add '% ' to beginning of lines, add numbers/amounts
    prepIngredientsForMaps(allRecipes)

    # Make a reverse n-gram map that will allow us to write backwards later
    reverseSeedMap = makeReverseBigramDict(allRecipes)
   
    # Update the user on program progress
    printUpdate(2)

    # Make a map from end seeds of ingredients to lists of other end seeds
    # from ingredients they've been seen with in recipes
    endSeedMap = makeEndSeedMap(allRecipes)

    printUpdate(3)

    isd = InstructionSentenceData()

    isd.fillData(allRecipes, endSeedMap)

    metaTextToPrint = printRecipeBookTitle()

    i = 0
    while i < numRecipesToPrint:

        markovIngredientsList = None
        for i in xrange(200):
            markovIngredientsList = None
            try:
                markovIngredientsList = makeRandomIngredientsList(reverseSeedMap, endSeedMap, numIngredients, endSeedLength, endSeedSeedLength)
            except IngredientsListException as inst:
                # print "markovIngredientsList exception: " + inst.args[0]
                pass
            if markovIngredientsList != None:
                break

        recipeTitle = writeRecipeTitle(properAdjectives, markovIngredientsList)
        
        numServings = random.choice(allRecipes).getNumServings()

        textToPrint = " " + recipeTitle + " (SERVES " + str(numServings) + ")\n"

        textToPrint += "   Ingredients:\n"
        for ingredient in markovIngredientsList:
            if ingredient[2]=='/':
                ingredient = ingredient[0] + ingredient[4:]
            textToPrint += "      " + ingredient + "\n"
        textToPrint += "\n"

        randomInstructions = []
        try:
            randomInstructions = makeRandomInstructions(isd.goodSentencesWithSeeds, markovIngredientsList)
        except InstructionsListException as inst:
            # print "Instructions list exception: ", inst.args[0]
            pass
        if randomInstructions == []:
            continue
        instructionsToPrint = refineRandomInstructions(randomInstructions, isd.servingSentencesWithoutSeeds)

        textToPrint += "   Instructions:\n" + instructionsToPrint + "\n\n\n"
        print textToPrint
        metaTextToPrint += textToPrint

        i += 1

    print "\n\n\n   I have saved your recipes in \"Random_Recipe_Book.txt\" in this application's folder.\n\n\n"

    outfileName = os.path.join(res_dirName, "Random_Recipe_Book.txt")
    with open(outfileName, 'w') as outfile:
        outfile.write(metaTextToPrint)





### Function Implementations ###

##
# The following functions are used to separate the raw cookbook
# text into individual, raw recipe texts 
#    - separateRawRecipeTexts
##
def separateRawRecipeTexts(res_dirName):
    cookbook_fileName = os.path.join(res_dirName, "MarthaStewart-LivingCookbook.txt")
    allText = open(cookbook_fileName, 'r').read()

    # Remove any lines from allText that have any 
    # all-caps words in them that aren't MAKES or SERVES. These 
    # deleted lines are unimportant.
    allText = removeAllCapsLines(allText)

    allRecipes = []
    lines = allText.split('\n')
    numLines = len(lines)
    print "num lines in cookbook: ", len(lines)
    pastFirstRecipe = False
    recipeIndBounds = [0, None]
    for ind, line in enumerate(lines):
        lineWords = line.strip().split()
        if ind == numLines - 1:
            # This accounts for the last recipe
            newRecipe = Recipe()
            newRecipe.allRecipeText = "\n".join(lines[recipeIndBounds[0]:])
            newRecipe.recipeCharLength = len(newRecipe.allRecipeText)
            allRecipes.append(newRecipe)
        elif lineWords != [] and (lineWords[0] in ["MAKES", "SERVES"]):

            # Doesn't work on first iteration, so have to punt
            if pastFirstRecipe == False:
                pastFirstRecipe = True
                continue

            # Create new recipe for insertion into allRecipes list
            newRecipe = Recipe()

            # Find nearest previous non-blank line
            indFirstPrevNonBlank = ind - 1
            while True:
                if indFirstPrevNonBlank <= 0 or lines[indFirstPrevNonBlank] != '':
                    break
                indFirstPrevNonBlank -= 1

            # Find nearest previous blank line after nearest previous non-blank line
            indSecondPrevBlank = indFirstPrevNonBlank - 1
            while True:
                if indSecondPrevBlank <= 0 or lines[indSecondPrevBlank] == '':
                    break
                indSecondPrevBlank -= 1

            recipeIndBounds[1] = indSecondPrevBlank

            newRecipe.allRecipeText = "\n".join(lines[recipeIndBounds[0]:recipeIndBounds[1]])
            newRecipe.recipeCharLength = len(newRecipe.allRecipeText)
            allRecipes.append(newRecipe)

            recipeIndBounds[0] = recipeIndBounds[1]
    allRecipes = [recipe for recipe in allRecipes if recipe.allRecipeText != '']
    print "num recipes: ", len(allRecipes)
    return allRecipes

##
# Function: Recipe::removeAllCapsLines
# ------------------------------------
# Remove any lines from the text that don't have the all-caps words
# MAKES or SERVES. These deleted lines are unimportant.
##
def removeAllCapsLines(text):
    newText = []
    lines = [(line, line.strip().split(" ")) for line in text.split('\n')]
    for line, lineWords in lines:
        allCapsWords = [word for word in lineWords if word.isupper()]
        if allCapsWords == [] or lineWords[0] in ["MAKES", "SERVES"]:
            newText += [line]
    newText = "\n".join(newText)
    return newText

def splitRecipes(allRecipes, adjectives, endSeedLength):
    # for recipe in allRecipes[:3]:
    #     print len(recipe.allRecipeText)
    # sys.exit()
    for i, myRecipe in enumerate(allRecipes):

        # Find the title of this recipe in myRecipe.allRecipeText and set
        # myRecipe.name equal to that title.
        myRecipe.findAndSetTitle()

        # Find and set the number of servings this recipe makes.
        myRecipe.findAndSetNumServings()

        # Split myRecipe.allRecipeText into myRecipe.allIngredientsText
        # and myRecipe.allInstructionsText
        myRecipe.splitIngredientsInstructionText()

        # myRecipe.printAllInstructionText()
        # myRecipe.printAllIngredientsText()

        myRecipe.separateIngredients(adjectives)

        myRecipe.separateInstructions()
        myRecipe.findIngredientAmounts()
        myRecipe.findIngredientUnits()
        myRecipe.fillIngredientWords()
        myRecipe.fillEndSeeds(endSeedLength)
        myRecipe.divideInstructionSentences()
        myRecipe.findFinalIngredientWords()
        myRecipe.findSeedsInInstructionSentences()

        allRecipes[i] = myRecipe

##
# Function: makeReverseBigramDict
# -------------------------------
# Makes dictionary of classic bigram relations
# between words, except in reverse.
# Ex:
#   - The sentence is: "% 5 teaspoons of olive oil"
#   - reverseBigramDict:
#       {("5" "teaspoons"): ["%"],
#        ("teaspoons" "of"): ["5"], 
#        ("of", "olive"): ["teaspoons"],
#        ("olive" "oil"): ["of"]}
#   - The "%" means the beginning of an ingredient line
def makeReverseBigramDict(allRecipes):
    reverseBigramDict = {}
    for recipe in allRecipes:
        for ingredient in recipe.ingredients:
            ingWords = ingredient.cleanWordsInIngredient
            if len(ingWords) >= 3:
                for word1, word2, word3 in zip(ingWords[:], ingWords[1:], ingWords[2:]):
                    bigram = (word2, word3)
                    unigram = tuple([word3])
                    reverseBigramDict[bigram] = reverseBigramDict.get(bigram, []) + [word1]
                    reverseBigramDict[unigram] = reverseBigramDict.get(unigram, []) + [word2]

    return reverseBigramDict


# Function: makeEndSeedMap
# ------------------------
# Makes a map from all end seeds to the other end seeds they've been seen with.
# Ex:
#  - endSeedMap originally is {}
#  - First recipe has large carrots, ground pepper, and grilled chicken as ingredients
#  - After processing first recipe, endSeedMap is:
#       - {("large", "carrots"): [("ground", "pepper"), ("grilled", "chicken")],
#          ("ground", "pepper"): [("large", "carrots"), ("grilled", "chicken")],
#          ("grilled", "chicken"): [("ground", "pepper"), ("large", "carrots")]
#          }
def makeEndSeedMap(allRecipes):
    endSeedMap = {}
    for recipe in allRecipes:
        endSeeds = recipe.endSeeds
        for i, es in reversed(list(enumerate(endSeeds))):
            if len(es) == 0:
                endSeeds.pop(i)
        for endSeed in endSeeds:
            otherEndSeeds = [seed for seed in endSeeds if seed != endSeed]
            endSeedMap[endSeed] = endSeedMap.get(endSeed, []) + otherEndSeeds

    return endSeedMap


## 
# Function: compileAllIngredients
# -------------------------------
# Do some adjustments to the ingredients, adding % signs
# to the beginning of the ingredient lines and adding in
# some numbers (amounts).
##
def prepIngredientsForMaps(allRecipes):
    for i, recipe in enumerate(allRecipes):
        for j, myIngredient in enumerate(recipe.ingredients):
            line = "% "
            if myIngredient.amount != "NO_LEADING_NUMBER":
                line += myIngredient.amount + " "

            lastWord = ""
            for word in myIngredient.wordsInIngredient:
                if lastWord == "plus" and allRecipes[0].isUnit(word):
                    line += str(random.randint(1,10)) + " "
                line += word + " "
                lastWord = word
            line += "\n"

            myIngredient.cleanWordsInIngredient = line.split(" ")
            myIngredient.cleanLine = line
            recipe.ingredients[j] = myIngredient
        allRecipes[i] = recipe

##
# Function: deleteOneIngredientRecipes
# ------------------------------------
# allRecipes will have no recipes with only 1 ingredient
# after this function is executed.
##
def deleteOneIngredientRecipes(allRecipes):
    for i in reversed(xrange(0, len(allRecipes))):
        currentRecipe = allRecipes[i]
        numEndSeeds = len(currentRecipe.getEndSeeds())
        if numEndSeeds == 1 or numEndSeeds == 0:
            allRecipes.pop(i)



def makeRandomInstructions(goodSentencesWithSeeds, ingredientsList):
    returnVec = []
    unusedEndWords = [ingredient.split(" ")[-1] for ingredient in ingredientsList]
    instSent = None

    iterationCounter1 = 0
    while True:

        if iterationCounter1 > 30:
            raise InstructionsListException("More than 30 iters.")

        if unusedEndWords == []:
            break

        # Try to find pre-made instruction sentences with some of the
        # unused words already inside them
        refinedGoodSentencesWithSeeds = []
        for goodSentence in goodSentencesWithSeeds:
            for word in goodSentence.order1EndSeedsInside:
                if word in unusedEndWords:
                    refinedGoodSentencesWithSeeds.append(goodSentence)
                    break

        # Make an instruction sentence
        if refinedGoodSentencesWithSeeds == []:
            instSent = copy.deepcopy(random.choice(goodSentencesWithSeeds))

            # Replace order 1 seeds in the sentence with unused words
            numReplacementPairs = min(len(unusedEndWords), len(instSent.order1EndSeedsInside))
            replacementPairs = zip(instSent.order1EndSeedsInside[:numReplacementPairs], unusedEndWords[:numReplacementPairs])
            for sentWord, unusedWord in replacementPairs:
                instSent.sentence = instSent.sentence.replace(sentWord, unusedWord)
        else:
            instSent = random.choice(refinedGoodSentencesWithSeeds)

        returnVec.append(instSent.sentence)

        unusedEndWords = [ew for ew in unusedEndWords if (ew not in instSent.sentence)]
        iterationCounter1 += 1
    return returnVec



def refineRandomInstructions(instructions, servingSentencesWithoutSeeds):
    serveSentence = ""
    startSentence = ""
    servingWords = ["Serve", "serve", "Served", "served"]
    startWords = ["Add", "Mix", "Combine", "In", "Prepare", "Preheat", "Blend", "Using", "Place", "Melt", "Slice", "Halve", "Heat"]
    servingSentenceExists = False
    for i, sentence in enumerate(instructions):

        for word in servingWords:
            if word in sentence:
                instructions[i] = instructions[-1]
                instructions[-1] = sentence
                servingSentenceExists = True

        for word in startWords:
            if sentence.startswith(word):
                instructions[i] = instructions[0]
                instructions[0] = sentence
    if not servingSentenceExists:
        servingSentence = random.choice(servingSentencesWithoutSeeds).sentence
        instructions.append(servingSentence)
    returnString = ""
    counter = 1
    for sentence in instructions:
        newSentence = ""
        charCounter = 0
        for ch in sentence:
            if (charCounter>60 and ch==' '):
                charCounter = 0
                newSentence += " " + "\n" + "         "
                if (counter/10==1):
                    newSentence += " "
            else:
                newSentence += ch
            charCounter += 1
        sentence = newSentence
        returnString += "      " + str(counter) + ". " + sentence + "\n"
        counter += 1
    return returnString


def makeRandomIngredientsList(reverseSeedMap, endSeedMap, numIngredients, endSeedLength, endSeedSeedLength):
    outputTokens = []
    ingredientList = []
    usedEndSeedKeys = []

    allEndSeedKeys = endSeedMap.keys()
    allRevSeedKeys = reverseSeedMap.keys()

    # Choose the first end seed (which is for the first ingredient)
    nextESK = list(random.choice(allEndSeedKeys))
    usedEndSeedKeys.append(nextESK)

    # Get the first ingredient started
    newIngredient = writeIngredientLine(nextESK, reverseSeedMap)
    ingredientList.append(newIngredient)

    possibleNextEndSeedKeys = None
    for i in xrange(0, numIngredients):
        numEndSeedSeeds = min(len(usedEndSeedKeys), endSeedSeedLength)
        possibleNextEndSeedKeys = [endSeedMap[tuple(seedKey)] for seedKey in usedEndSeedKeys[-numEndSeedSeeds:]]
        possibleNextEndSeedKeys = list(itertools.chain(*possibleNextEndSeedKeys))
        while True:
            if possibleNextEndSeedKeys == []:
                 raise IngredientsListException("No possible next ingredients")
            nextESK = random.choice(possibleNextEndSeedKeys)
            if (nextESK not in usedEndSeedKeys) and ("plus" not in nextESK) and ("lengths" not in nextESK) and ("inch" not in nextESK):
                break
            else:
                possibleNextEndSeedKeys.remove(nextESK)

        usedEndSeedKeys.append(nextESK)
        newIngredient = writeIngredientLine(nextESK, reverseSeedMap)
        ingredientList.append(newIngredient)
    return ingredientList

def writeIngredientLine(nextESK, reverseSeedMap):
    ingredientLine = " ".join(nextESK)
    bigram = list(nextESK[0 : min(len(nextESK), seedLength)])
    while True:
        possiblePreviousTokens = []
        try:
            possiblePreviousTokens = reverseSeedMap[tuple(bigram)]
        except KeyError:
            pass
        if possiblePreviousTokens == []:
            raise IngredientsListException("Can't write rest of ingredient line")

        token = random.choice(possiblePreviousTokens)

        # If we've reached the beginning of the ingredient line,
        # we stop writing
        if token == "%":
            break

        # Account for tokens like 3/8 or 5/6 (amounts)
        space = ""
        if not (token == "/" or ingredientLine[0] == '/'):
            space = " "

        ingredientLine = token + space + ingredientLine
        bigram = [token] + bigram[:-1]
    return ingredientLine

def writeRecipeTitle(properAdjectives, markovIngredientsList):
    validEndsOfTitles = ["bread", "oil", "sausage", "cheese", "corn", "salad", "dressing",
            "stock", "pepper", "bacon", "meat", "mustard", "butter", "water", "melon",
            "kiwi", "lettuce", "yogurt", "sauce", "rice", "salt", "port", "vinegar"]
    badTitleWords = ["halves", "thighs", "leaves", "stalks", "cloves", "half", "thigh",
                    "leaf", "stalk", "clove", "extract"]

    lastWordsInTitle = [None, None]
    lastTokens = [line.split(" ")[-1] for line in markovIngredientsList]
    lastTokens = set([t for t in lastTokens if t not in badTitleWords])

    for token in lastTokens:
        if (token[-1] == 's') or (token in validEndsOfTitles):
            if not lastWordsInTitle[0]:
                lastWordsInTitle[0] = token
            elif not lastWordsInTitle[1] and token != lastWordsInTitle[0]:
                lastWordsInTitle[1] = token
                break

    if lastWordsInTitle[0]:
        lastTokens.remove(lastWordsInTitle[0])
    if lastWordsInTitle[1]:
        lastTokens.remove(lastWordsInTitle[1])

    descriptorWord = None
    for token in lastTokens:
        if token[-1] != 's':
            descriptorWord = token
            break

    recipeTitle = []
    recipeTitle.append(random.choice(properAdjectives).strip())

    if descriptorWord:
        recipeTitle.append(descriptorWord.capitalize())

    if lastWordsInTitle[0]:
        recipeTitle.append(lastWordsInTitle[0].capitalize())
        if lastWordsInTitle[1]:
            recipeTitle += ["with", lastWordsInTitle[1].capitalize()]

    # If no words are valid, just make the title "<proper_adjective> Dish"
    if not descriptorWord and not lastWordsInTitle[0] and not lastWordsInTitle[1]:
        recipeTitle.append("Dish")

    recipeTitle = " ".join(recipeTitle)
    return recipeTitle


















##
# Functional Group: Utility
###########################
# List of functions:
#   - invertMap
##
def invertMap(map):
    returnMap = {}
    for key in map.keys():
        val = map[key]
        returnMap[val] = key
    return returnMap




##
# Functional Group: Reading and Writing to Files
################################################
# List of functions:
#   - gatherAdjectives
##
def gatherAdjectives(res_dirName):
    adjectives = set()
    adj_filename = os.path.join(res_dirName, "adjectives.txt")
    with open(adj_filename) as f:
        for adj in f:
            adjectives.add(adj)
    return adjectives




##
# Functional Group: User-Interaction
####################################
# List of functions:
#   - greetUser
#   - explainProgram
#   - printUpdate
#
#   - printListOfRecipesIngredients
#   - printRecipeEndSeeds
#   
#   - getNumIngredientsResponse
#   - getStartResponse
#   - getEndSeedLengthResponse
#   - getNumRecipesToPrintResponse
#   - getAllAtOnceResponse
##
def greetUser():
    greet = "            Random Recipe Writer | Austin Ray, Bruno De Martino, Alex Lin\n"
    greet += "   -----------------------------------------------------------------------------\n\n"
    greet += "   Hello there! I am a random recipe writer! Thanks for checking me out!\n"
    greet += "   I am able to create random recipes for you based on the recipes found in\n"
    greet += "   The Martha Stewart Living Cookbook\" by using Markov chains. If you want to\n"
    greet += "   know how I do this, enter \"explain\", otherwise enter \"start\" to begin: "
    print greet

def explainProgram():
    print "\n\n   -----------------------------Program Explanation-----------------------------\n"
    print "   ", "   The first thing I do is separate all of Martha's recipes into C++ objects."
    print "   ", "Next, I do some refinement on each recipe, separating ingredients from"
    print "   ", "instructions, separating ingredients from each other, etc. After that,"
    print "   ", "I realize that the last two words of each ingredient are the best"
    print "   ", "description of that ingredient. So I make a C++ map to associate"
    print "   ", "each \"end seed\" with other end seeds that they've been seen with in"
    print "   ", "recipes. This is the Markov chain that allows me to add new ingredients"
    print "   ", "to the recipe that go well with previous ingredients. Next, I create another"
    print "   ", "Markov chain to associate words in an ingredient with the words behind"
    print "   ", "(to the left of) them. This allows me to add a new ingredient just by its"
    print "   ", "end seed, then fill in the rest of the line from right to left, forming"
    print "   ", "a complete ingredient. In this way, I create my full ingredients list."
    print "   ", "Since it uses a Markov chain, more ingredients means less cohesiveness"
    print "   ", "between all of the ingredients. You've been Warned!"
    print "   ", "   Next, for the title, I examine the ingredients in my recipe, adding"
    print "   ", "good words for titles and ignoring the bad ones. Oh, and I also add"
    print "   ", "a special adjective at the beginning of the title to give each recipe"
    print "   ", "its own personal flair. Next, for the instructions, I first look at"
    print "   ", "all the instruction sentences I've seen in the cookbook. We can see"
    print "   ", "that certain sentences are too complicated to try to fit my freshly"
    print "   ", "picked ingredients into, while others are simple and allow me to work"
    print "   ", "my ingredients in just fine. Primarily, this includes sentences that"
    print "   ", "use small connector words like with, and, to, the, etc. around their"
    print "   ", "ingredients. This allows me to input my ingredients without creating"
    print "   ", "too crazy of a sentence - pretty cool, huh? Next, I associate each"
    print "   ", "sentence with the ingredients found in it. When I go to write the"
    print "   ", "instructions for my newly generated recipe, I look at my ingredients"
    print "   ", "and try to find simple sentences I've seen them in before. If I find"
    print "   ", "a good sentence with the ingredient in it, I put that sentence down"
    print "   ", "as an instruction step and move on to my other ingredients. If I can't"
    print "   ", "find a good sentence with an ingredient, I just take any old simple"
    print "   ", "sentence and insert my ingredient into it, replacing the one that was"
    print "   ", "there before. After I've written instructions that include all of my"
    print "   ", "ingredients, I then add a good ending sentence, if one isn't there"
    print "   ", "already. And voila! You have your scrumptious new randomly generated"
    print "   ", "recipe. Happy cooking!"

def printUpdate(updateNum):
    if updateNum == 0:
        print "\n\n   -------------------------------Main Program----------------------------------\n"
        print "\n   ", "I'm going to generate your recipes now. This might take a minute...\n\n"
    elif updateNum == 1:
        print "   ", "...Making progress..."
    elif updateNum == 2:
        print "   ", "...Still working..."
    elif updateNum == 3:
        print "   ", "...Can't be much longer now..."

def printRecipeBookTitle():
    text = "\n\n\n\n\n\n\n"
    text += "               Randomly Generated Recipe Booklet\n"
    text += "            ----------------------------------------- \n\n"
    print text
    return text

def printListOfRecipesIngredients(allRecipes, startingIndex, numToPrint):
    for myRecipe in allRecipes[0:numToPrint]:
        print myRecipe.getName()
        print "-------------------------------"
        myRecipe.printIngredients()
        print "\n\n"

def printRecipeEndSeeds(allRecipes, startingIndex, numToPrint):
    if (startingIndex==-5):
        startingIndex = 0
    if (numToPrint==-5):
        numToPrint = len(allRecipes)
    for myRecipe in allRecipes[startingIndex:numToPrint]:
        myRecipe.printEndSeeds()
        print "\n\n"

def getNumIngredientsResponse(argv):
    numIngredients = 0
    if argv[1] in ["-d", "--default"]:
        numIngredients = 10
    elif len(argv) > 2:
        numIngredients = int(argv[2])
    else:
        while (True):
            numIngredients = int(raw_input("   Enter the desired number of ingredients per recipe (5-15 allowed): "))
            if (numIngredients<5 or numIngredients>15):
                print "\n   Invalid number of ingredients. Try again.\n"
                continue
            break
    return numIngredients

def getStartResponse(argv):
    start = ""
    if argv[1] in ["-d", "--default"]:
        start = "start"
    elif len(argv) > 1:
        start = argv[1]
    else:
        start = raw_input("")
    return start

def getEndSeedLengthResponse(argv):
    endSeedSeedLength = 0
    if argv[1] in ["-d", "--default"]:
        endSeedSeedLength = 3
    elif len(argv) > 3:
        endSeedSeedLength = int(argv[3])
    else:
        while (True):
            endSeedSeedLength = int(raw_input("   Enter ingredient similarity within recipes (1-5 allowed, 5 = very similar): "))
            if (endSeedSeedLength<1 or endSeedSeedLength>5):
                print "\n   Invalid ingredient similarity. Try again.\n"
                continue
            break
    return endSeedSeedLength

def getNumRecipesToPrintResponse(argv):
    numRecipesToPrint = 0
    if argv[1] in ["-d", "--default"]:
        numRecipesToPrint = 20
    elif len(argv) > 4:
        numRecipesToPrint = int(argv[4])
    else:
        while (True):
            numRecipesToPrint = int(raw_input("   Enter the number of recipes you want (1-100 allowed): "))
            if (numRecipesToPrint<1 or numRecipesToPrint>100):
                print "\n   Invalid number of recipes. Try again.\n"
                continue
            break
    return numRecipesToPrint

def getAllAtOnceResponse(argv):
    allAtOnce = ""
    if argv[1] in ["-d", "--default"]:
        allAtOnce = "all"
    elif len(argv) > 5:
        allAtOnce = argv[5]
    else:
        while (True):
            allAtOnce = raw_input("   Do you want to print recipes one by one, or all at once?\n   (Enter either \"one\" or \"all\"): ")
            if (not (allAtOnce=="one") and not (allAtOnce=="all")):
                print "\n   Invalid input. Try again.\n"
                continue
            elif (allAtOnce=="one"):
                print "\n   Got it. Press Enter after each recipe prints to get the next one."
            break






# If called from command line, call the main() function
if __name__ == "__main__":
    #main(sys.argv)
    main(sys.argv + ["-d"])
