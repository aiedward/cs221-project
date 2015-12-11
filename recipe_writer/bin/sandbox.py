# Authors: Austin Ray, Bruno De Martino, Alex Lin
# File: sandbox.py
# ----------------
# This file exists so we can play around with different packages.
# As we develop useful functions, we will port groups of similar functions
# from sandbox.py into other package files.
#
# Note: Commenting encouraged so other people can learn from what you've done!

import collections, itertools, copy
import sys, os
import numpy, scipy, math
import re
import inspect
import json
from multiprocessing import Pool
from contextlib import closing
import thread
import threading
import time
from lib import util
from lib import constants as c
from lib import nutrientdatabase as ndb

def printFunctionName():
    print ""
    print ""
    print "Function: " + inspect.stack()[1][3]
    print "---------"


def test_makeTrigrams():
    printFunctionName()
    myStr = """1 teaspoon's coarse salt, plus more 
    for cooking water. """

    correctSplit = [word for word in re.split("([^a-zA-Z0-9_\''])", myStr) if word is not '' and word is not ' ']
    print correctSplit

    # 'zip()' basically takes the transpose of a matrix
    for trigram in zip(correctSplit, correctSplit[1:], correctSplit[2:]):
        print(trigram)
    print ""

def test_passByReference1():
    printFunctionName()
    def myAppend(li, n):
        li.append(n)

    def setEqual(li1, li2):
        li1 = li2

    def setEqual_dc(li1, li2):
        li1 = copy.deepcopy(li2)

    def setEqual_elems(li1, li2):
        li1 = li2[:]

    def setEqual_li(lili1, li2):
        lili1[0] = li2

    def setEqual_ret(li1, li2):
        return li2

    def changeFirstElem(li):
        newElem = [99, 99, 99]
        li[0] = newElem

    def changeAllElems1(li):
        for i in xrange(0, len(li)):
            myElem = li[i]
            myElem = [i]
            li[i] = myElem

    def changeAllElems2(li):
        counter = 0
        for elem in li:
            elem = [counter]
            counter += 1

    listA = [0, 1]
    listB = [4, 5]
    listC = [7, 8]
    print "listA: ", listA, "listB: ", listB, "listC: ", listC

    listA = [0, 1]
    listB = [4, 5]
    listC = [7, 8]
    myAppend(listA, 2)
    setEqual(listB, listC)
    print "listA: ", listA, "listB: ", listB, "listC: ", listC

    listA = [0, 1]
    listB = [4, 5]
    listC = [7, 8]
    myAppend(listA, 3)
    setEqual_dc(listB, listC)
    print "listA: ", listA, "listB: ", listB, "listC: ", listC

    listA = [0, 1]
    listB = [4, 5]
    listC = [7, 8]
    myAppend(listA, 20)
    setEqual_elems(listB, listC)
    print "listA: ", listA, "listB: ", listB, "listC: ", listC

    listA = [0, 1]
    listB = [4, 5]
    listC = [7, 8]
    myAppend(listA, 40)
    liliB = [listB]
    setEqual_li(liliB, listC)
    listB = liliB[0]
    print "listA: ", listA, "listB: ", listB, "listC: ", listC

    listA = [0, 1]
    listB = [4, 5]
    listC = [7, 8]
    myAppend(listA, 60)
    listB = setEqual_ret(listB, listC)
    print "listA: ", listA, "listB: ", listB, "listC: ", listC


def test_passByReference2():
    printFunctionName()
    listA = [0, 1]
    listB = [4, 5]
    listC = [7, 8]
    listD = [listA, listB, listC]
    myAppend(listA, 60)
    myAppend(listB, 6)
    listB = setEqual_ret(listB, listC)
    print "listA: ", listA, "listB: ", listB, "listC: ", listC, "listD: ", listD

    listA = [0, 1]
    listB = [4, 5]
    listC = [7, 8]
    listD = [listA, listB, listC]
    changeFirstElem(listD)
    print "listA: ", listA, "listB: ", listB, "listC: ", listC, "listD: ", listD

    listA = [0, 1]
    listB = [4, 5]
    listC = [7, 8]
    listD = [listA, listB, listC]
    changeAllElems1(listD)
    print "listA: ", listA, "listB: ", listB, "listC: ", listC, "listD: ", listD

    listA = [0, 1]
    listB = [4, 5]
    listC = [7, 8]
    listD = [listA, listB, listC]
    changeAllElems2(listD)
    print "listA: ", listA, "listB: ", listB, "listC: ", listC, "listD: ", listD

def test_slicing():
    listA = [5, 6, 7, 8, 9, 10, 11]
    numEndElems = 3
    listB = listA[-numEndElems:]
    print "listA: ", listA, "listB: ", listB
    print "listA[:-1]: ", listA[:-1]
    print "listA[-len(listA):] ", listA[-len(listA):]


def test_split1():
    sent = """Preheat the oven to 325 degrees F. Line a 9 x 1  baking 
pan with a kitchen towel. Line the brioche pan 
with plastic wrap. """
    sent = sent.replace(". ", ". @ ")
    sentVec = sent.split("@")
    print sentVec


def test_split2():
    printFunctionName()
    sent = """spicy seared scallop canapes 

MAKES 48 

6 tablespoons all-purpose flour """
    sentVec = sent.split("\n")
    print sentVec
    print "\n".join(sentVec)


def test_chain1():
    printFunctionName()
    listA = [0, 1]
    listB = [4, 5]
    listC = [7, 8]
    bigList = [listA, listB, listC]
    flattenedList = list(itertools.chain(*bigList))
    print "bigList: ", bigList
    print "flattenedList: ", flattenedList


def test_chain2():
    printFunctionName()
    listA = "hello "
    listB = "beautiful "
    listC = "world!"
    bigList = [listA, listB, listC]
    flattenedList = "".join(bigList)
    print "bigList: ", bigList
    print "flattenedList: ", flattenedList


def test_isupper():
    printFunctionName()
    word1 = "HELLO"
    word2 = "HELLo"
    print "word1.isupper(): ", word1.isupper()
    print "word2.isupper(): ", word2.isupper()

def test_regex1():
    printFunctionName()
    sent = """Preheat the oven to 325 degrees F. Line a 9 x 1  baking 
pan with a kitchen towel. Line the brioche pan 
with plastic wrap. """
    sentVec = re.split("([^a-zA-Z0-9_\''])", sent)
    print "sentVec: ", sentVec

def test_split3():
    printFunctionName()
    myW = "hey"
    wSplit = myW.split(" ")
    print "\"hey\".split(' '): ", wSplit

def test_tuple1():
    printFunctionName()
    myTuple1 = tuple("hey")
    myTuple2 = tuple(["hey"])
    myList1 = list(myTuple1)
    print "myTuple1: ", myTuple1
    print "myTuple2: ", myTuple2
    print "myList1: ", myList1

def test_exception1():
    printFunctionName()
    var1 = "yooooo"
    myDict = {"hi": 1}
    try:
        var1 = myDict["booooo"]
    except KeyError:
        pass
    print "var1: ", var1

def test_exception2():
    printFunctionName()
    exc = Exception("spam", "eggs")
    try:
        raise exc
    except Exception as inst:
        print "inst.args: ", inst.args

def test_exception3():
    printFunctionName()
    class MyException(Exception):
        pass

    exc = Exception("I am a normal exception")
    myExc = MyException("I'm special!!!")
    try:
        raise myExc
        raise exc
    except Exception as inst:
        print "inst.args: ", inst.args
    except MyException as inst:
        print "inst.args: ", inst.args

def test_exception4():
    printFunctionName()
    class MyException(Exception):
        pass

    exc = Exception("I am a normal exception")
    myExc = MyException("I'm special!!!")
    try:
        try:
            raise exc
        except Exception as inst:
            print "inst.args1: ", inst.args
            raise myExc
    except MyException as inst:
        print "inst.args2: ", inst.args

def test_database1():
    printFunctionName()
    dec = json.JSONDecoder()
    fullJsonString = open("allRecipes.json", 'r').read()
    myDict = dec.decode(fullJsonString)

    for key, val in myDict.items()[:10]:
        try:
            print key, ": ", val
        except UnicodeEncodeError:
            key = key.encode('utf-8')
            # val = [ch.encode('utf-8') for ch in val]
            # val = [ch.encode('ascii', 'ignore').decode('ascii') for ch in val]
            print key, ": ", val

    print

def test_threading1():
    printFunctionName()

    def writeThreadNameToFile(threadName, message, curFile):
        filedir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "res", "threadtest")
        filename = os.path.join(filedir, threadName) + ".txt"
        with open(filename, 'w+') as f:
            f.write(message)


    # Create new threads
    threads = []
    for i in xrange(4):
        threadName = "Thread-" + str(i)
        message = "I, the " + str(i) + "th thread, am super duper awesome."

        # Create a new thread that, when its start() method is called, will
        # execute target(args)
        newThread = threading.Thread(\
            target=writeThreadNameToFile, 
            args=(threadName, message, __file__)\
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

    print

def safeConnect(fxn, args, tries=20):
    returnVal = None
    for i in range(tries):
        try:
            returnVal = fxn(*args)
        except requests.exceptions.ConnectionError as e:
            pass
    return returnVal

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def buildNutrientDict(givenIngredient):
 
    #Flags
    ignoreNumericalLipids = True

    returnDict = {}
    measureDict = {}
    loadedMeasures = False
    nutrientDict = {}
    nutrientDict['proximates'] = {}
    nutrientDict['minerals'] = {}
    nutrientDict['vitamins'] = {}
    nutrientDict['lipids'] = {}
    nutrientDict['amino acids'] = {}
    nutrientDict['other'] = {}

    #Loop through each nutrient in the given ingredient
    for nutrient in givenIngredient['report']['food']['nutrients']:
        nutrientGroup = nutrient['group'].lower()
        nutrientName =  nutrient['name'].lower()
        nutrientVal = nutrient['value']
        nutrientUnit = nutrient['unit'].encode('ascii', errors='ignore')

        #Saves the nutrient value and unit per 100g
        if ignoreNumericalLipids and nutrientGroup == 'lipids' \
            and hasNumbers(nutrientName):
            continue                

        #Saves the info of the current nutrient to the dictionary
        nutrientDict[nutrientGroup][nutrientName] = tuple((nutrientVal, nutrientUnit))

        #Load the measurement conversions for each ingredient exactly once.
        if not loadedMeasures:
            for measureKey in nutrient['measures']:
                equivUnit = measureKey['label'].encode('ascii', errors='ignore')
                equivValue = measureKey['eqv']
                measureDict[equivUnit] = equivValue
            loadedMeasures = True
    # print "\n\nMeasures: \n"
    # print measureDict
    # print "\n\nNutrients: \n"
    # for group in nutrientDict:
    #     print "\nGroup: " + group
    #     for nutrient in nutrientDict[group]:
    #        print "Nutrient " + nutrient + "  Value: " +  str(nutrientDict[group][nutrient])
    returnDict[curIngredient] = {}
    returnDict[curIngredient]['measure'] = measureDict
    returnDict[curIngredient]['nutrients'] = nutrientDict
    return returnDict
    #util.dumpJSONDict(os.path.join(c.PATH_TO_RESOURCES, "testNutrients", "testcheesedump.json"), returnDict)
    #print returnDict;
    

    # mergeList = []
    # if getProximates: mergeList.append(nutrientDict['Proximates'])
    # if getMinerals: mergeList.append(nutrientDict['Minerals'])
    # if getVitamins: mergeList.append(nutrientDict['Vitamins'])
    # if getLipids: mergeList.append(nutrientDict['Lipids'])
    # if getAminoAcids: mergeList.append(nutrientDict['Amino Acids'])
    # if getOther: mergeList.append(nutrientDict['Other'])
    # returnDict['nutrients'] = util.naivelyMergeDicts([mergeList])


def testAliasExtraction():
    print "Hello world!"
    allRecipes = []

    # Each alias has 3 main fields:
    #   "count"
    #   "aliasBuddies"
    #   "lines"
    aliasData = {}

    # Read in and parse recipe data structures (dictionaries) from a json file.
    aliasList = util.listAllAliases()
    for alias in aliasList:
        print alias.encode('ascii', errors='ignore')

    print str(len(aliasList)) + " ingredients found!"


##
# Function: extractRecipesFromJSON
# --------------------------------
# Reads in all data from the json file containing all recipe data.
##
def extractRecipesFromJSON(allRecipes):
    jsonFilePath = os.path.join(c.PATH_TO_RESOURCES, "aliasdata", "miniAliases.json")
    myDict = util.loadJSONDict(jsonFilePath)

    # Fill allRecipes with just the values for each JSON member,
    # as the values actually contain the keys as a member
    for _, val in myDict.items():
        allRecipes.append(val)

def testNutrientDatabaseClass():
    nutDatabase = ndb.NutrientDatabase()
    print nutDatabase.getNumValidIngredients()
    print nutDatabase.getCalories("accent flavor enhancer")
    print nutDatabase.listConversionUnits("accent flavor enhancer")
    print nutDatabase.getConversionFactor("accent flavor enhancer", 'cup')
    print nutDatabase.getNutrientFromGrams(100,"accent flavor enhancer", 'calories')
    print nutDatabase.getNutrientFromUnit(1,"accent flavor enhancer", 'calories', 'cup')
    print nutDatabase.getNutrientFromGrams(200,"accent flavor enhancer", 'energy')
    print nutDatabase.getNutrientFromGrams(100,"accent flavor enhancer", 'protein')

[]




def main(argv):
    # test_slicing()
    # test_split1()
    # test_chain1()
    # test_chain2()
    # test_split2()
    # test_isupper()
    # test_regex1()

    # test_split3()
    # test_tuple1()
    # test_exception1()
    # test_exception2()
    # test_exception3()
    # test_exception4()

    # test_database1()
    # test_threading1()
    #saveNutrientInfo()
    #testAliasExtraction()
    testNutrientDatabaseClass()

if __name__ == "__main__":
    main(sys.argv)
