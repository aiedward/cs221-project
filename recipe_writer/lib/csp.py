##
# File: csp.py
# ------------
# Uses recipe data from Yummly and nutrition data from nutrition.gov to
# make good recipes that satisfy certain constraints.
##
import collections, itertools, copy, Queue
import numpy, scipy, math, random
import os, sys, time, importlib
import tokenize, re, string
import json, unicodedata
import thread

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from lib import util, constants, nutrition, search
constants.init(os.path.dirname(os.path.dirname(__file__)))


##
# Function: run
# -------------
# csp.py's version of main(). This function is called by write_recipes.py
# with arguments given to it. 
#
#   verbose: If verbose is True, then status updates should
#            be printed as csp.py progresses through its solution.
##
def run(verbose):
    # These variables will likely be fed through run()'s arguments later
    traitsDataPath = os.path.join(constants.PATH_TO_ROOT, "res", "csp_defaultTraits.json")
    traits = util.loadJSONDict(traitsDataPath)

    traits["verbose"] = verbose

    if traits["verbose"]:
        print "Creating recipe with %d ingredients." % traits["num_ingredients"]

    # Solve the csp of choosing aliases (identities) for each ingredient
    solveAliasCSP(traits)

    # With each ingredient now assigned an alias, solve the csp of choosing
    # amounts (mass in grams) for each ingredient
    solveAmountCSP(traits)

    # Print status update
    if verbose:
        print "csp.py ran successfully"

    # return {k: v for k, v in traits.items() if k in ["alias_choices"]}
    return {k: v for k, v in traits.items() if k in ["alias_choices", "amount choices"]}

##
# Function: solveAliasCSP
# ---------------------------
# Solve the problem of picking aliases for the ingredients given 
# a set of constraints.
##
def solveAliasCSP(traits):
    csp = AliasCSP()
    addVariables(csp, traits, "alias")
    addFactors(csp, traits, "alias")

    solver = AliasCSPSolver(traits, numSolutions=1, verbose=True)
    solver.solve(csp)

    traits["alias_choices"] = solver.curAssignment

##
# Function: solveAmountCSP
# ---------------------------
# Solve the problem of picking amounts for the ingredients given pre-picked
# aliases and a set of constraints.
##
def solveAmountCSP(traits):
    csp = util.CSP()
    addVariables(csp, traits, "amount")
    addFactors(csp, traits, "amount")

    solver = util.BacktrackingSearch(numSolutions=10, verbose=True)
    solver.solve(csp)

    traits["amount_choices"] = solver.optimalAssignment

##
# Function: addVariables
# ---------------------------
# 
##
def addVariables(csp, traits, whichCSP):
    num_ingredients = traits["num_ingredients"]

    if whichCSP == "alias":
        nameVariables = ['alias_%d'%i for i in xrange(0, num_ingredients)]
        nameDomain = util.listAllAliases()
        csp.set_domain(nameDomain)
        for var in nameVariables:
            csp.add_variable(var, nameDomain)

        if traits["verbose"]:
            "Solving aliasCSP. Added variables: ", csp.variables

    elif whichCSP == "amount":
        amountVariables = ['amount_%d'%i for i in xrange(0, num_ingredients)]

        # Every number from 0 to max_ingredient_mass in intervals of 5, not
        # including 0, but yes including max_ingredient_mass.
        amountDomain = getAmountDomain(traits)
        for var in amountVariables:
            csp.add_variable(var, amountDomain)

##
# Function: addFactors
# --------------------------
#
##
def addFactors(csp, traits, whichCSP):
    if whichCSP == "alias":
        constraints = traits["alias_constraints"]
        addFactors_sameName(csp, traits)
        if constraints.get("free_of_nuts", "False").lower() == "true":
            addFactors_freeOfNuts(csp, traits)
        if constraints.get("free_of_meat", "False").lower() == "true":
            addFactors_freeOfMeat(csp, traits)
        addFactors_buddyScore(csp, traits)

    if whichCSP == "amount":
        constraints = traits["amount_constraints"]
        if "max_total_kcal" in constraints:
            addFactors_maxTotalCalories(csp, traits)
    

##
# Function: addFactor_sameName
# ----------------------------
# Add binary factors between all name variables to make sure no two ingredients
# have the same name.
##
def addFactors_sameName(csp, traits):
    aliasVars = csp.variables
    n = len(aliasVars)
    for i in xrange(n-1):
        for j in xrange(i+1, n):
            def containSameWord(string1, string2):
                return not (True in [w in string2 for w in string1.split(" ")]\
                         or True in [w in string1 for w in string2.split(" ")])
            csp.add_binary_factor(aliasVars[i], aliasVars[j], containSameWord)

##
# Function: addFactors_freeOfNuts
# ----------------------------
# Makes sure no alias has nuts in it.
##
def addFactors_freeOfNuts(csp, traits):
    for var in csp.variables:
        csp.add_unary_factor(var, lambda a: not util.nutStringQ(a))

##
# Function: addFactors_freeOfMeat
# ----------------------------
# Makes sure no alias has meat in it.
##
def addFactors_freeOfMeat(csp, traits):
    for var in csp.variables:
        csp.add_unary_factor(var, lambda a: not util.meatStringQ(a))

##
# Function: addFactors_buddyScore
# -------------------------------
# Optimize for good buddy scores between all the aliases.
##
def addFactors_buddyScore(csp, traits):
    aliasVars = csp.variables
    n = len(aliasVars)
    for i in xrange(n-1):
        for j in xrange(i+1, n):
            csp.add_binary_factor(aliasVars[i], aliasVars[j], util.aliasBuddyScore)

##
# Function: addFactor_maxTotalCalories
# ------------------------------------
#
##
def addFactor_maxTotalCalories(csp, traits):
    def conversionFxn(nameAssignment, amountAssignment):
        return nutrition.unitConvert(nameAssignment, amountAssignment, "grams", "kcal")
    sumVal = traits["max"]["total"]["kcal"]
    get_ingredient_sum_variable(csp, traits, "kcal", sumVal, "max", conversionFxn)


##
# Function: getAmountDomain
# --------------------------
#
##
def getAmountDomain(traits):
    range(*tuple(traits["amount_range"].values())) + [traits["amount_range"]["max"]]








class AliasCSP:
    def __init__(self):
        self.numVars = 0
        self.variables = []
        self.values = {}
        self.binaryFactors = {}
        self.unaryFactors = {}
        self.domain = None

    def set_domain(self, domain):
        self.domain = list(set(domain))

    def add_variable(self, var, domain):
        if var in self.variables:
            raise Exception("Variable name already exists: %s" % str(var))

        self.numVars += 1
        self.variables.append(var)
        self.unaryFactors[var] = []
        self.binaryFactors[var] = dict()

    def get_neighbor_vars(self, var):
        return self.binaryFactors[var].keys()

    def add_unary_factor(self, var, factorFunc):
        self.unaryFactors[var].append(factorFunc)

    def add_binary_factor(self, var1, var2, factorFunc):
        self.binaryFactors[var1][var2] = self.binaryFactors[var1].get(var2, [])
        self.binaryFactors[var2][var1] = self.binaryFactors[var2].get(var1, [])
        self.binaryFactors[var1][var2].append(factorFunc)
        self.binaryFactors[var2][var1].append(factorFunc)

    def binaryFactorExists(self, var1, var2):
        return var2 in self.binaryFactors[var1]

class AliasCSPSolver:
    def __init__(self, traits, numSolutions=float('inf'), verbose=False):
        # Max number of solutions we should find.
        self.numSolutions = numSolutions

        self.traits = traits

        self.numIters = traits["num_iters"]

        # Whether progress and stats should be printed
        self.verbose = verbose

        self.curAssignment = {}
        self.curVarsAssigned = set()

        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # List of all solutions found.
        self.allAssignments = []

    def solve(self, csp):
        self.csp = csp
        self.beamSearch()
        if self.verbose:
            print
            print "Solved alias csp with optimal assignment: "
            print self.curAssignment.values()
            print 
            print "And average alias buddy score:"
            print util.averageAliasBuddyScore(self.curAssignment.values())
            print
        return self.curAssignment

    def initializeVariables(self):
        self.curAssignment = {var: None for var in self.csp.variables}
        self.curVarsAssigned = set()
        failed = False
        for var in self.csp.variables:
            for counter in xrange(100):
                possibleValues = self.csp.domain
                val = random.choice(possibleValues)
                print "Trying an initial assignment for %s: %s" % (var, val)
                if self.getDeltaWeight2(var, val) > 0:
                    self.curAssignment[var] = val
                    self.curVarsAssigned.add(var)
                    break

            # An ingredient we added was a dud and progresion wasn't possible. Start over.
            # (really should implement backtracking here)
            if var not in self.curVarsAssigned:
                failed = True
                break
        if failed:
            self.initializeVariables()


    def beamSearch(self):
        if self.verbose:
            print "\nStarting beamSearch in csp.py to pick aliases..."
        self.initializeVariables()
        for i in xrange(self.numIters):
            for var in self.csp.variables:
                possibleValues = self.csp.domain
                if len(possibleValues) == 0:
                    return
                # elif len(possibleValues) % 100 == 0:
                #     print "\n###"
                #     print "There are %d ingredients left to try." % len(possibleValues)
                #     print "\n###"
                val = random.choice(possibleValues)
                if self.getDeltaWeight2(var, val) > 0:
                    print
                    print "Old assignments: ", self.curAssignment.values()
                    print "Old score: ", self.calculateCurrentWeight()
                    self.curAssignment[var] = val
                    print "New assignments: ", self.curAssignment.values()
                    print "New score: ", self.calculateCurrentWeight()
                self.csp.domain.remove(val)

        def getDeltaWeight(self, newVar, newVal, varAssigned=True):
        oldWeight = self.calculateCurrentWeight()

        oldVal = self.curAssignment[newVar]
        self.curAssignment[newVar] = newVal
        if not varAssigned:
            self.curVarsAssigned.add(newVar)

        newWeight = self.calculateCurrentWeight()

        self.curAssignment[newVar] = oldVal
        if not varAssigned:
            self.curVarsAssigned.remove(newVar)

        if self.verbose:
            print
            print "  --- Considering changing var %s to %s ---" % (newVar, newVal)
            print "  Current full assignment = %s" % self.curAssignment
            print "  Current weight = %f" % oldWeight
            print "  With var change, new weight = %f" % newWeight
        return newWeight - oldWeight

    def getDeltaWeight2(self, var, newVal):
        weight = float(0)

        curVarsAssigned = list(self.curVarsAssigned)
        oldVal = self.curAssignment[var]

        oldWeight = 1.0
        newWeight = 1.0

        oldScore = None

        # Add in unary factors
        for factorFunc in self.csp.unaryFactors[var]:
            if oldVal == None:
                oldScore = 0.0
            else:
                oldScore = float(factorFunc(oldVal))
            newScore = float(factorFunc(newVal))
            oldWeight *= oldScore
            newWeight *= newScore


        # Add in binary factors
        for neighbor in curVarsAssigned:
            if var == neighbor:
                continue
            if self.csp.binaryFactorExists(var, neighbor):
                neighborVal = self.curAssignment[neighbor]
                for factorFunc in self.csp.binaryFactors[var][neighbor]:
                    if oldVal == None:
                        oldScore = 0.0
                    else:
                        oldScore = factorFunc(oldVal, neighborVal)

                    # The evaluation of aliasBuddyScore should never be 0,
                    # since laplace smoothing is implemented
                    newScore = factorFunc(newVal, neighborVal)
                    
                    oldWeight *= oldScore
                    newWeight *= newScore

        # print "newWeight: ", newWeight
        # print "oldWeight: ", oldWeight
        return newWeight - oldWeight
        

    def calculateCurrentWeight(self):
        nAssigned = len(self.curVarsAssigned)

        if nAssigned == 0:
            return float(0)

        weight = float(0)

        curVarsAssigned = list(self.curVarsAssigned)

        # Add in unary factors
        for var in curVarsAssigned:
            val = self.curAssignment[var]
            for factorFunc in self.csp.unaryFactors[var]:
                score = float(factorFunc(val))
                if score == 0:
                    return float(0)
                else:
                    weight += score

        # Add in binary factors
        for i in xrange(nAssigned-1):
            for j in xrange(i+1, nAssigned):
                var1 = curVarsAssigned[i]
                var2 = curVarsAssigned[j]
                if self.csp.binaryFactorExists(var1, var2):
                    val1 = self.curAssignment[var1]
                    val2 = self.curAssignment[var2]
                    for factorFunc in self.csp.binaryFactors[var1][var2]:
                        score = factorFunc(val1, val2)
                        
                        if score == 0 and factorFunc.__name__ != "aliasBuddyScore":
                            return float(0)
                        else:
                            weight += score

        return weight

##
# Function: get_ingredient_sum_variable
# -------------------------------------
# Create a set of variables that have binary factors in between them to limit
# the sum of a certain trait of the ingredients.
# conversionFxn takes in a name variable assignment
def get_ingredient_sum_variable(csp, traits, name, sumVal, minOrMax, conversionFxn):
    nameVars = getNameVars(csp)
    amountVars = getAmountVars(csp)

    # maxVarAmounts = [max(csp.values[amountVar]) for amountVar in amountVars]
    # minVarAmounts = [min(csp.values[amountVar]) for amountVar in amountVars]

    # runningMaxSum = 0
    # runningMinSum = 0

    last_var = None
    last_var_domain = None

    # The domain for the first/second value of a B pair is set to be the same
    # as the amountVar for simplicity.
    # Add all unique first/second value pairs to the full domain of a B pair.
    sumVarDomain = itertools.permutations(getAmountDomain(traits), 2)

    for i, amountVar in enumerate(amountVars):
        # Give the new variable a name
        newVar = ('sum', name, i)

        # The first of the sum variables can only have 0 as its first element.
        newVarDomain = None
        if i == 0:
            newVarDomain = filter(function=lambda B: B[0] == 0, iterable=sumVarDomain)
        else:
            newVarDomain = sumVarDomain

        # Add the new variable/domain pair to the csp
        csp.add_variable(newVar, newVarDomain)

        # Add a binary factor that ties this new sum var to its corresponding
        # amount var
        def amountVar_sumVar_CongruentQ(xi, bi):
            return bi[1] == bi[0] + xi
        csp.add_binary_factor(amountVars[i], newVar, amountVar_sumVar_CongruentQ)
        
        if i != 0:
            csp.add_binary_factor(last_var, newVar, lambda bimin1, bi: bi[0] == bimin1[1])

        last_var = newVar
        last_var_domain = newVarDomain

    finalSumVar = ('sum', name, len(amountVars))
    csp.add_variable(finalSumVar, range(0, sumVal+1))

    if minOrMax == "max":
        csp.add_unary_factor(finalSumVar, lambda bn: bn <= sumVal)
    else:
        csp.add_unary_factor(finalSumVar, lambda bn: bn >= sumVal)

    if last_var:
        csp.add_binary_factor(last_var, finalSumVar, lambda bnmin1, bn: bn == bnmin1[1])
    else:
        csp.add_unary_factor(finalSumVar, lambda bn: bn == 0)

    return sumVar


if __name__ == "__main__":
    run(True)
