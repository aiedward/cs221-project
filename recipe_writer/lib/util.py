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
import lib.constants as c
from lib import constants as c

aliasData = None
nutrientData = None
# Function: safeConnect
# ---------------------
# Wrapper for a function requesting info from a server.  Returns the
# requested value on success, None on error.  It retries a default
# of 40 times before breaking and returning none, attempting to circumvent
# connection errors and server overload by integrating a sleep call.
def safeConnect(fxn, args, tries=40):
    returnVal = None
    for i in range(tries):
        try:
            returnVal = fxn(*args)
            break
        except requests.exceptions.ConnectionError as e:
            if i % 10 == 0:
                time.sleep(2)
            pass
    return returnVal

##
# Function: loadJSONDict
# ----------------------
# Loads a JSON file into a python dictionary and returns that dictionary.
#
##
def loadJSONDict(jsonFilePath):

    global aliasData
    # Read in the JSON file containing recipe data
    fullJsonString = None
    with open(jsonFilePath, 'r') as f:
		fullJsonString = f.read().encode('ascii', errors='ignore')


    # This is dead code I was trying to use to remove all escaped unicode
    # characters (e.g. \u00bd) or convert them to ascii
    #noUnicodeJsonString = fullJsonString.decode('unicode_escape').encode('ascii','ignore')
    #asciiJsonString = fullJsonString.decode('unicode-escape')

    # Read the JSON file in as a dictionary
    d = json.JSONDecoder()
    returnDict = d.decode(fullJsonString)

    if "aliasData_" in jsonFilePath:
        aliasData = copy.deepcopy(returnDict)
    return returnDict

##
# Function: loadJSONDicts
# -----------------------
# Loads multiple JSON files into python dictionaries and returns 
# a list of those dictionaries.
##
def loadJSONDicts(jsonFilePaths):
    return [loadJSONDict(f) for f in jsonFilePaths]

##
# Function: dumpDictToJSONFile
# ----------------------------
# Writes a dictionary to a JSON file with the full path 'fullFilePath'
##
def dumpJSONDict(fullFilePath, dict2dump):
    jsonDatabase = json.dumps(dict2dump, sort_keys=True, indent=4)
    with open(fullFilePath, "w") as f:
        f.write(jsonDatabase)

##
# Function: naivelyMergeDicts
# ---------------------------
# Merges a list of dictionaries into one dictionary, not caring which
# value it keeps for keys that have multiple values.
##
def naivelyMergeDicts(listOfDicts):
    masterList = []
    for d in listOfDicts:
        masterList += d.items()
    return dict(masterList)
    # return dict(deleteDuplicatesBy(masterList, lambda x, y: x[0] == y[0]))

##
# Function: greedyMergeDicts
# ---------------------------
# Merges a list of dictionaries into one dictionary, not caring which
# value it keeps for keys that have multiple values.
##
def greedyMergeDicts(listOfDicts):
    masterDict = collections.defaultdict(list)
    for d in listOfDicts:
        for k, v in d.items():
            masterDict[k].append(v)
    return dict(masterDict)
    # return dict(deleteDuplicatesBy(masterList, lambda x, y: x[0] == y[0]))

def mergeNutrientDicts(listOfDicts):
	masterList = []
	masterDict = {}
	for d in listOfDicts:
		for item in listOfDicts:
			for item2 in item:
				masterList += dict(item2).items()
				#print
		#masterList += d.items()
	return dict(masterList)
##
# Function: listFilesWtihSuffix
# -----------------------------
# Returns a list of full file paths for all files whose names end in suffixStr 
# and are in the specified directory.
#
# Example suffixStr's are ".json", ".txt", ".py"
##
def listFilesWithSuffix(directoryPath, suffixStr):
    allFiles = os.listdir(directoryPath)
    return [os.path.join(directoryPath, f) for f in allFiles if f.endswith(suffixStr)]

##
# Function: deleteDuplicates
# --------------------------
# Does not change the argument given. Returns a version of the list given
# with only the first appearance of all duplicate elements saved.
##
def deleteDuplicates(li):
    new_li = []
    for elem in li:
        if elem not in new_li:
            new_li.append(elem)
    return new_li

##
# Function: deleteDuplicatesBy
# ----------------------------
# Does not change the argument given. Returns a version of the list given
# with only the first appearance of all duplicate elements saved.
#
# Duplicates are decided by the lambda function given.
##
def deleteDuplicatesBy(li, duplicatesQ):
    new_li = []
    for e1 in li:
        shouldAppend = True
        for e2 in new_li:
            if duplicatesQ(e1, e2):
                shouldAppend = False
                break
        if shouldAppend:
            new_li.append(e1)
    return new_li

##
# Function: loadLatestAliasData
# -----------------------------
# Loads in the file with the most recent date that ends in ".json" in /res/aliasdata
# and returns the resulting dictionary.
##
def loadLatestAliasData():
    print "GOt to alias data laoding"
    aliasDataFolder = os.path.join(c.PATH_TO_RESOURCES, "aliasdata")
    latestAliasDataFileFullPath = sorted(listFilesWithSuffix(aliasDataFolder, ".json"))[-1]
    print "Path: "+ latestAliasDataFileFullPath
    return loadJSONDict(latestAliasDataFileFullPath)

##
# Function: getAliasData
# ----------------------
# If alias data has already been loaded durin this session, that data
# is returned. Otherwise, the latest alias data is loaded in and returned.
##
def getAliasData():
    global aliasData
    if aliasData == None:
        print "Loading new data"
        return loadLatestAliasData()
    else:
        return aliasData

##
# Function: listAllAliases
# ------------------------
# Return a list of all aliases found in recipes.
##
def listAllAliases():
    aliasDict = getAliasData()
    #print aliasDict
    return aliasDict.keys()
  
##
# Function: string_appendDateAndTime
# ----------------------------------
# Return a string with the current date and time appended.
##
def string_appendDateAndTime(s):
    return "_".join([s, time.strftime("%m-%d-%Y"), time.strftime("%Hh-%Mm-%Ss")]) + ".json"

##
# Function: hasDeepKey
# --------------------
# Dive into a dictionary, recursively asking for values corresponding to a
# list of keys until you reach a non-dictionary-type value or you reach a
# sub-dictionary that doesn't have the current key in the key list.
#
# Example:
#   myDict = {"a": {"b": {"c": 1}, "d": 9}, "e": {"f": 3}}
#   hasDeepKey(myDict, ["a", "b", "c"]) returns True
#   hasDeepKey(myDict, ["a", "d"]) returns True
#   hasDeepKey(myDict, ["a", "b", "h"]) returns False
##
def hasDeepKey(myDict, keyList):
    curDict = myDict
    for key in keyList:
        if (type(curDict) is not dict) or (key not in curDict):
            return False
        curDict = curDict[key]
    return True

def nutStringQ(alias):
    nutdict = loadJSONDict(os.path.join(c.PATH_TO_ROOT, "res", "nutwords.json"))
    nutwords = nutdict.values()[0]
    for w in nutwords:
        if w in alias:
            return True
    return False

def meatStringQ(alias):
    meatdict = loadJSONDict(os.path.join(c.PATH_TO_ROOT, "res", "meatwords.json"))
    meatwords = meatdict.values()[0]
    for w in meatwords:
        if w in alias:
            return True
    return False

##
# Function aliasBuddyScore
# ------------------------
# score = ((# times seen together) / (total # alias1 appearances) + 
#          (# times seen together) / (total # alias2 appearances)) / 2
##
def aliasBuddyScore(alias1, alias2):
    aliasData = getAliasData()
    laplaceSmooth = 0.0
    freq1 = aliasData[alias1]["count"] + laplaceSmooth
    freq2 = aliasData[alias2]["count"] + laplaceSmooth
    freqTogether = aliasData[alias1]["aliasBuddies"].get(alias2, float(0)) + laplaceSmooth
    buddyScore1 = (float(freqTogether) / float(freq1)) + (float(freqTogether) / float(freq2))
    buddyScore1 /= float(2)
    buddyScore2 = 2 * float(freqTogether) / (float(freq1) + float(freq2))
    if False:
        print
        print "   Computing buddy score for %s and %s..." % (alias1, alias2)
        print "   Freq of %s is %f" % (alias1, freq1)
        print "   Freq of %s is %f" % (alias2, freq2)
        print "   Freq together is %f" % freqTogether
        print "   Final score is %f" % buddyScore2

    return buddyScore2

def averageAliasBuddyScore(aliasList):
    n = len(aliasList)
    count = 0.0
    total = 0.0
    for i in xrange(0, n-1):
        for j in xrange(i+1, n):
            count += 1.0
            total += aliasBuddyScore(aliasList[i], aliasList[j])
    return total / count


# General code for representing a weighted CSP (Constraint Satisfaction Problem).
# All variables are being referenced by their index instead of their original
# names.
class CSP:
    def __init__(self):
        # Total number of variables in the CSP.
        self.numVars = 0

        # The list of variable names in the same order as they are added. A
        # variable name can be any hashable objects, for example: int, str,
        # or any tuple with hashtable objects.
        self.variables = []

        # Each key K in this dictionary is a variable name.
        # values[K] is the list of domain values that variable K can take on.
        self.values = {}

        # Each entry is a unary factor table for the corresponding variable.
        # The factor table corresponds to the weight distribution of a variable
        # for all added unary factor functions. If there's no unary function for 
        # a variable K, there will be no entry for K in unaryFactors.
        # E.g. if B \in ['a', 'b'] is a variable, and we added two
        # unary factor functions f1, f2 for B,
        # then unaryFactors[B]['a'] == f1('a') * f2('a')
        self.unaryFactors = {}

        # Each entry is a dictionary keyed by the name of the other variable
        # involved. The value is a binary factor table, where each table
        # stores the factor value for all possible combinations of
        # the domains of the two variables for all added binary factor
        # functions. The table is represented as a dictionary of dictionary.
        #
        # As an example, if we only have two variables
        # A \in ['b', 'c'],  B \in ['a', 'b']
        # and we've added two binary functions f1(A,B) and f2(A,B) to the CSP,
        # then binaryFactors[A][B]['b']['a'] == f1('b','a') * f2('b','a').
        # binaryFactors[A][A] should return a key error since a variable
        # shouldn't have a binary factor table with itself.

        self.binaryFactors = {}

    def add_variable(self, var, domain):
        """
        Add a new variable to the CSP.
        """
        if var in self.variables:
            raise Exception("Variable name already exists: %s" % str(var))

        self.numVars += 1
        self.variables.append(var)
        self.values[var] = domain
        self.unaryFactors[var] = None
        self.binaryFactors[var] = dict()


    def get_neighbor_vars(self, var):
        """
        Returns a list of variables which are neighbors of |var|.
        """
        return self.binaryFactors[var].keys()

    def add_unary_factor(self, var, factorFunc):
        """
        Add a unary factor function for a variable. Its factor
        value across the domain will be *merged* with any previously added
        unary factor functions through elementwise multiplication.

        How to get unary factor value given a variable |var| and
        value |val|?
        => csp.unaryFactors[var][val]
        """
        factor = {val:float(factorFunc(val)) for val in self.values[var]}
        if self.unaryFactors[var] is not None:
            assert len(self.unaryFactors[var]) == len(factor)
            self.unaryFactors[var] = {val:self.unaryFactors[var][val] * \
                factor[val] for val in factor}
        else:
            self.unaryFactors[var] = factor

    def add_binary_factor(self, var1, var2, factor_func):
        """
        Takes two variable names and a binary factor function
        |factorFunc|, add to binaryFactors. If the two variables already
        had binaryFactors added earlier, they will be *merged* through element
        wise multiplication.

        How to get binary factor value given a variable |var1| with value |val1| 
        and variable |var2| with value |val2|?
        => csp.binaryFactors[var1][var2][val1][val2]
        """
        # never shall a binary factor be added over a single variable
        try:
            assert var1 != var2
        except:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print '!! Tip:                                                                       !!'
            print '!! You are adding a binary factor over a same variable...                  !!'
            print '!! Please check your code and avoid doing this.                               !!'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            raise

        self.update_binary_factor_table(var1, var2,
            {val1: {val2: float(factor_func(val1, val2)) \
                for val2 in self.values[var2]} for val1 in self.values[var1]})
        self.update_binary_factor_table(var2, var1, \
            {val2: {val1: float(factor_func(val1, val2)) \
                for val1 in self.values[var1]} for val2 in self.values[var2]})

    def update_binary_factor_table(self, var1, var2, table):
        """
        Private method you can skip for 0c, might be useful for 1c though.
        Update the binary factor table for binaryFactors[var1][var2].
        If it exists, element-wise multiplications will be performed to merge
        them together.
        """
        if var2 not in self.binaryFactors[var1]:
            self.binaryFactors[var1][var2] = table
        else:
            currentTable = self.binaryFactors[var1][var2]
            for i in table:
                for j in table[i]:
                    assert i in currentTable and j in currentTable[i]
                    currentTable[i][j] *= table[i][j]




# A backtracking algorithm that solves weighted CSP.
# Usage:
#   search = BacktrackingSearch()
#   search.solve(csp)
class BacktrackingSearch():

    def reset_results(self, numSolutions=float('inf'), verbose=False):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """

        # Max number of solutions we should find.
        self.numSolutions = numSolutions

        # Whether progress and stats should be printed
        self.verbose = verbose

        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
        else:
            print "No solution was found."

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        return w

    def solve(self, csp, mcv = False, ac3 = False):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Set the search heuristics requested asked.
        self.mcv = mcv
        self.ac3 = ac3

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        # Perform backtracking search.
        try:
            self.backtrack({}, 0, 1)
        except Exception as e:
            # self.numSolutions solutions have been found
            pass

        # Print summary of solutions.
        if self.verbose:
            self.print_stats()

    def backtrack(self, assignment, numAssigned, weight):
        """
        Perform the back-tracking algorithms to find all possible solutions to
        the CSP.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param numAssigned: Number of currently assigned variables
        @param weight: The weight of the current partial assignment.
        """

        self.numOperations += 1
        assert weight > 0
        if numAssigned == self.csp.numVars:
            # A satisfiable solution have been found. Update the statistics.
            self.numAssignments += 1
            newAssignment = {}
            for var in self.csp.variables:
                newAssignment[var] = assignment[var]
            self.allAssignments.append(newAssignment)

            if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
                if weight == self.optimalWeight:
                    self.numOptimalAssignments += 1
                else:
                    self.numOptimalAssignments = 1
                self.optimalWeight = weight

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations

            # If we've found enough solutions, return all the way up
            # the recursion tree
            if len(self.allAssignments) >= numSolutions:
                raise Exception()

            # Otherwise, just return from this level of reursion
            else:
                return

        # Select the next variable to be assigned.
        var = self.get_unassigned_variable(assignment)

        # Get an ordering of the values.
        ordered_values = self.domains[var]

        # Austin addition: Sort the values based on how optimal they will be
        ordered_values = sorted(ordered_values, key=lambda val: -self.get_delta_weight(assignment, var, val))

        # Continue the backtracking recursion using |var| and |ordered_values|.
        if not self.ac3:
            # When arc consistency check is not enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    del assignment[var]
        else:
            # Arc consistency check is enabled.
            # Problem 1c: skeleton code for AC-3
            # You need to implement arc_consistency_check().
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    # create a deep copy of domains as we are going to look
                    # ahead and change domain values
                    localCopy = copy.deepcopy(self.domains)
                    # fix value for the selected variable so that hopefully we
                    # can eliminate values for other variables
                    self.domains[var] = [val]

                    # enforce arc consistency
                    self.arc_consistency_check(var)

                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    # restore the previous domains
                    self.domains = localCopy
                    del assignment[var]

    def get_unassigned_variable(self, assignment):
        """
        Given a partial assignment, return a currently unassigned variable.

        @param assignment: A dictionary of current assignment. This is the same as
            what you've seen so far.

        @return var: a currently unassigned variable.
        """

        if not self.mcv:
            # Select a variable without any heuristics.
            for var in self.csp.variables:
                if var not in assignment: return var
        else:
            # Problem 1b
            # Heuristic: most constrained variable (MCV)
            # Select a variable with the least number of remaining domain values.
            # Hint: given var, self.domains[var] gives you all the possible values
            # Hint: get_delta_weight gives the change in weights given a partial
            #       assignment, a variable, and a proposed value to this variable
            # BEGIN_YOUR_CODE (around 10 lines of code expected)
            mcv = None
            minValidDomainSize = float('inf')

            nonZeroDomains = 0
            for var in self.csp.variables:
                if var in assignment:
                    continue
                validDomain = [self.get_delta_weight(assignment, var, val) for val in self.domains[var] if self.get_delta_weight(assignment, var, val)]
                validDomainSize = float(len(validDomain))

                if validDomainSize < minValidDomainSize:
                    mcv = var
                    minValidDomainSize = validDomainSize

            return mcv


            # END_YOUR_CODE

    def arc_consistency_check(self, var):
        """
        Perform the AC-3 algorithm. The goal is to reduce the size of the
        domain values for the unassigned variables based on arc consistency.

        @param var: The variable whose value has just been set.
        """
        # Problem 1c
        # Hint: How to get variables neighboring variable |var|?
        # => for var2 in self.csp.get_neighbor_vars(var):
        #       # use var2
        #
        # Hint: How to check if two values are inconsistent?
        # For unary factors
        #   => self.csp.unaryFactors[var1][val1] == 0
        #
        # For binary factors
        #   => self.csp.binaryFactors[var1][var2][val1][val2] == 0
        #   (self.csp.binaryFactors[var1][var2] returns a nested dict of all assignments)

        # BEGIN_YOUR_CODE (around 20 lines of code expected)

        var_queue = [var]

        while len(var_queue) > 0:
            cur_var = var_queue.pop(0)
            cur_domain = self.domains[cur_var]

            # Cycle through all the neighbors of cur_var
            for neighbor_var in self.csp.get_neighbor_vars(cur_var):
                neighborDomain = self.domains[neighbor_var]
                neighborDomainLength = len(neighborDomain)
                newNeighborDomain = {}
                newNeighborDomainLength = 0

                # The new domain of the neighbor var will be
                # all values for which at least one cur_val/neighbor_val
                # pair is consistent
                for neighbor_val in neighborDomain:
                    # If the neighbor var has a unary factor and factor(neighbor_val) is 0,
                    # then this neighbor_val is not consistent
                    if self.csp.unaryFactors[neighbor_var] and not self.csp.unaryFactors[neighbor_var][neighbor_val]:
                        continue

                    # Try to find a cur_val that is consistent with neighbor_val
                    # Note: Since cur and neighbor are neighbors, we know they
                    #       have a binary factor together
                    for cur_val in cur_domain: 
                        if self.csp.binaryFactors[cur_var][neighbor_var][cur_val][neighbor_val]:
                            newNeighborDomain[neighbor_val] = 1
                            newNeighborDomainLength += 1
                            break

                    # If the domain of the neighboring var will definitely
                    # not change, then skip this neighbor var
                    if newNeighborDomainLength == neighborDomainLength:
                        break

                # If the domain of neighbor_var changed, then add
                # it to the ac3 queue
                if newNeighborDomainLength != neighborDomainLength:
                    self.domains[neighbor_var] = newNeighborDomain.keys()
                    var_queue.append(neighbor_var)

        # END_YOUR_CODE

def get_sum_variable(csp, name, variables, maxSum):
    """
    Given a list of |variables| each with non-negative integer domains,
    returns the name of a new variable with domain range(0, maxSum+1), such that
    it's consistent with the value |n| iff the assignments for |variables|
    sums to |n|.

    @param name: Prefix of all the variables that are going to be added.
        Can be any hashable objects. For every variable |var| added in this
        function, it's recommended to use a naming strategy such as
        ('sum', |name|, |var|) to avoid conflicts with other variable names.
    @param variables: A list of variables that are already in the CSP that
        have non-negative integer values as its domain.
    @param maxSum: An integer indicating the maximum sum value allowed. You
        can use it to get the auxiliary variables' domain

    @return result: The name of a newly created variable with domain range
        [0, maxSum] such that it's consistent with an assignment of |n|
        iff the assignment of |variables| sums to |n|.
    """
    # BEGIN_YOUR_CODE (around 20 lines of code expected)
    # new_vars = []
    # new_var_domains = []

    num_variables = len(variables)

    maxes_of_variables = [max(csp.values[variable]) for variable in variables]

    mins_of_variables = [min(csp.values[variable]) for variable in variables]

    runningMaxSum = 0
    runningMinSum = 0

    last_var = None
    last_var_domain = None

    for i in xrange(num_variables):
        new_var = ('sum', name, i)
        new_var_domain = None
        old_runningMaxSum = runningMaxSum
        runningMaxSum += maxes_of_variables[i]

        old_runningMinSum = runningMinSum
        runningMinSum += mins_of_variables[i]

        # if i == num_variables - 1:
        #     maxDomainVal = max(runningMaxSum, maxSum)
        #     new_var_domain = [[ for x in ] for y in range(runningMinSum, maxDomainVal + 1)] 
        # else:
        new_var_domain = []

        leftRange = range(old_runningMinSum, old_runningMaxSum + 1)
        rightRange = range(runningMinSum, runningMaxSum + 1)

        leftRange = range(0, maxSum + 1)
        rightRange = range(0, maxSum + 1)

        if i == 0:
            leftRange = [0]
            # csp.add_unary_factor(new_var, lambda bi: bi[1] == 0)

        for x in leftRange:
            for y in rightRange:
                new_var_domain.append((x, y))

        csp.add_variable(new_var, tuple(new_var_domain))

        csp.add_binary_factor(variables[i], new_var, lambda xi, bi: bi[1] == bi[0] + xi)
        
        if i != 0:
            csp.add_binary_factor(last_var, new_var, lambda bimin1, bi: bi[0] == bimin1[1])

        last_var = new_var
        last_var_domain = new_var_domain

    sum_var = ('sum', name, num_variables)
    csp.add_variable(sum_var, range(0, maxSum+1))
    csp.add_unary_factor(sum_var, lambda bn: bn <= maxSum)
    if last_var:
        csp.add_binary_factor(last_var, sum_var, lambda bnmin1, bn: bn == bnmin1[1])
    else:
        csp.add_unary_factor(sum_var, lambda bn: bn == 0)

    return sum_var

