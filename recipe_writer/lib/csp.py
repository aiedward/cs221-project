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
import constraint

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from lib import util, constants, nutrition, search, nutrientdatabase
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
    traits = initializeTraits(verbose)
    
    if traits["verbose"]:
        print "Creating recipe with %d ingredients." % traits["num_ingredients"]

    # Solve the csp of choosing aliases (identities) for each ingredient
    solveAliasCSP(traits)

    # With each ingredient now assigned an alias, solve the csp of choosing
    # amounts (mass in grams) for each ingredient
    solveAmountCSP(traits)

    printResults(traits)

    return "" #{k: v for k, v in traits.items() if k in ["alias_choices", "amount choices"]}

##
# Function: printResults
# -----------------------
# 
##
def printResults(traits):
    ND = traits["ND"]
    print
    totals = [0.0 for _ in range(max(traits["nutrientIndices"].values()) + 1)]
    for k, v in traits["amount_choices"].items():
        print "%s: " % traits["amountVarToAlias"][k]
        for nu in traits["focusNutrients"]:
            nuInd = traits["nutrientIndices"][nu]
            print "  %f %s %s" % (v[nuInd], ND.getNutrientUnit(nu), nu)
            totals[nuInd] += v[nuInd]
    print
    for nu in traits["focusNutrients"]:
        nuInd = traits["nutrientIndices"][nu]
        print "Total %s: %f %s" % (nu, totals[nuInd], ND.getNutrientUnit(nu))

##
# Function: initializeTraits
# --------------------------
#
##
def initializeTraits(verbose):
    traitsDataPath = os.path.join(constants.PATH_TO_ROOT, "res", "csp_defaultTraits.json")
    traits = util.loadJSONDict(traitsDataPath)
    traits["verbose"] = verbose
    traits["ND"] = nutrientdatabase.NutrientDatabase()
    return traits

##
# Function: solveAliasCSP
# ---------------------------
# Solve the problem of picking aliases for the ingredients given 
# a set of constraints.
##
def solveAliasCSP(traits):
    ## TO DO: Create another version of BacktrackingSearch that
    # works with AliasCSP (which just skips preprocessing) and
    # stops after a certain number of calls to backtrack()
    csp = AliasCSP()
    addVariablesAndFactors(csp, traits, "alias")

    solver = AliasCSPSolver(traits, numSolutions=1, verbose=traits["verbose"])
    solver.solve(csp)

    traits["alias_choices"] = solver.curAssignment

    for k, v in traits["alias_choices"].items():
        print "Alias for %s is %s" % (k, v)

##
# Function: solveAmountCSP
# ---------------------------
# Solve the problem of picking amounts for the ingredients given pre-picked
# aliases and a set of constraints.
##
def solveAmountCSP(traits):
    csp = util.CSP()
    addVariablesAndFactors(csp, traits, "amount")

    solver = util.BacktrackingSearch()
    solver.solve(csp, mcv=True, ac3=True)

    assign = solver.optimalAssignment
    print solver.optimalAssignment
    amountAssigns = {k: v for k, v in assign.items() if "_" in k}
    traits["amount_choices"] = amountAssigns

##
# Function: addVariables
# ---------------------------
# 
##
def addVariablesAndFactors(csp, traits, whichCSP):
    num_ingredients = traits["num_ingredients"]

    if whichCSP == "alias":
        nameVariables = ['alias_%d'%i for i in xrange(0, num_ingredients)]
        nameDomain = util.listAllAliases()
        csp.set_domain(nameDomain)
        for var in nameVariables:
            csp.add_variable(var, nameDomain)

        if traits["verbose"]:
            "Solving aliasCSP. Added variables: ", csp.variables

        constraints = traits["alias_constraints"]
        addFactors_sameName(csp, traits)
        if constraints.get("free_of_nuts", "False").lower() == "true":
            addFactors_freeOfNuts(csp, traits)
        if constraints.get("free_of_meat", "False").lower() == "true":
            addFactors_freeOfMeat(csp, traits)
        addFactors_nutrientDataExists(csp, traits)
        addFactors_buddyScore(csp, traits)

    elif whichCSP == "amount":
        # Shorthand for nutritional database class
        ND = traits["ND"]

        variables = ['amount_%d'%i for i in xrange(0, num_ingredients)]
        aliasVarDict = {variables[i]: traits["alias_choices"][k] \
            for i, k in enumerate(sorted(traits["alias_choices"].keys()))}
        traits["amountVarToAlias"] = aliasVarDict
        domainDict = {}

        # Get a list of all nutrients that are mentioned in amount constraints
        # (focusNutrients)
        # validNutrients = ND.validNutrientsDict.keys() + ['kcal'] + ['sodium']
        focusNutrients = ['kcal', 'carbs', 'fat', 'protein', 'sodium']
        # for constraint in traits["amount_constraints"]:
        #     focusNutrients += [n for n in constraint.split("_") if n in validNutrients]

        traits["focusNutrients"] = focusNutrients[:]

        # Create domains for the variables
        for var in variables:
            allDomains = []
            gramDomain = getAmountDomain(traits)
            allDomains.append(gramDomain)
            for nu in focusNutrients:
                nuDomain = [ND.getNutrientFromGrams(g, aliasVarDict[var], nu) for g in gramDomain]
                allDomains.append(nuDomain)
            domainDict[var] = [tuple(li) for li in zip(*allDomains)]

        # Where each unit is in the value tuple
        nutrientIndexDict = {unit: i for i, unit in enumerate(["grams"] + focusNutrients)}
        traits["nutrientIndices"] = nutrientIndexDict

        # Add all the amount variables
        for var in variables:
            print "Domain of var %s is %r" % (var, domainDict[var])
            csp.add_variable(var, domainDict[var])

        # Add all amount constraints specified in csp_defaultTraits.json
        for constraint, val in traits["amount_constraints"].items():
            splitConstraint = constraint.split("_")
            unit = splitConstraint[2]

            # If the amount constraint is a "max total ___" constraint...
            if splitConstraint[:2] == ["max", "total"]:
                print "Max sum is %s for unit %s: " % (val, unit)
                util.make_max_sum_variable(csp, unit, variables, val, nutrientIndexDict[unit])
            if splitConstraint[:2] == ["min", "total"]:
                print "Min sum is %s for unit %s: " % (val, unit)
                util.make_min_sum_variable(csp, unit, variables, val, nutrientIndexDict[unit])
            if splitConstraint[:2] == ["close", "total"]:
                print "Close sum is %s for unit %s: " % (val, unit)
                util.make_close_sum_variable(csp, unit, variables, val, nutrientIndexDict[unit])

        print "Finished making amountCSP..."
                
##
# Function: amountVarToAlias
# ----------------------------
#
##
def amountVarToAlias(traits, amountVar):
    return [val for key, val in traits['alias_choices'].items() if key[-2:] == amountVar[-2:]][0]

##
# Function: indToAlias
# ----------------------------
#
##
def indToAlias(traits, ind):
    return [val for key, val in traits['alias_choices'].items() if key.endswith(str(ind))][0]
    

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
# Function: addFactors_nutrientDataExists
# ----------------------------
# Makes sure no alias has meat in it.
##
def addFactors_nutrientDataExists(csp, traits):
    for var in csp.variables:
        csp.add_unary_factor(var, lambda a: traits["ND"].isValidIngredient(a))


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
    rangeArgs = tuple([traits["amount_range"]["min"], traits["amount_range"]["max"], traits["amount_range"]["step"]])
    return range(*rangeArgs) + [traits["amount_range"]["max"]]








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
                if self.verbose:
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
                    if self.verbose:
                        print
                        print "Old assignments: ", self.curAssignment.values()
                        print "Old score: ", self.calculateCurrentWeight()
                    self.curAssignment[var] = val
                    if self.verbose:
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


if __name__ == "__main__":
    run(False)
