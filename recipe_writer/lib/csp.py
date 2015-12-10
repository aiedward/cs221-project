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

from lib import util, constants, nutrition, search


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
	# Initialize the CSP. No variables or factors as of yet.
	csp = CSP()

	# These variables will likely be fed through run()'s arguments later
	traits = util.loadJSONDict(constants.PATH_TO_RESOURCES, "csp_defaultTraits.json")

	traits["alias_choices"] = solveAliasCSP(verbose, traits)

	ingredientAliasAmountPairs = solveAmountCSP(verbose, traits)

	return "csp.py ran successfully"

##
# Function: solveAliasCSP
# ---------------------------
# Solve the problem of picking aliases for the ingredients given 
# a set of constraints.
##
def solveAliasCSP(verbose, traits):
	csp = CSP()
	addVariables(csp, traits, "name")
	addFactors(csp, traits, "name")

##
# Function: solveAliasCSP
# ---------------------------
# Solve the problem of picking amounts for the ingredients given pre-picked
# aliases and a set of constraints.
##
def solveAmountCSP(verbose, traits, ingredientAliases):
	csp = CSP()
	addAmountVariables(csp, traits, ingredientAliases)



##
# Function: addNameVariables
# ---------------------------
# Add a variable for the alias (name) of each ingredient.
##
def addNameVariables(csp, traits):
	num_ingredients = traits["num_ingredients"]

	nameVariables = ['name_%d'%i for i in xrange(0, num_ingredients)]
	nameDomain = util.listAllAliases()
	for var in nameVariables:
		csp.add_variable(var, nameDomain)

##
# Function: addAmountVariables
# --------------------------
# Add a variable for the mass of each ingredient.
##
def addAmountVariables(csp, traits):
	num_ingredients = traits["num_ingredients"]

	amountVariables = ['amount_%d'%i for i in xrange(0, num_ingredients)]

	# Every number from 0 to max_ingredient_mass in intervals of 5, not
	# including 0, but yes including max_ingredient_mass.
	amountDomain = getAmountDomain(traits)
	for var in amountVariables:
		csp.add_variable(var, amountDomain)

##
# Function: getAmountDomain
# --------------------------
#
##
def getAmountDomain(traits):
	range(*tuple(traits["amount_range"].values())) + [traits["amount_range"]["max"]]

##
# Function: addAliasFactors
# --------------------------
#
##
def addAliasFactors(csp, traits):
	addSameNameFactors(csp, traits)

##
# Function: addAmountFactors
# --------------------------
# Factors:
#	- No two variable names can be the same.
#	- The total
##
def addAmountFactors(csp, traits):
	if util.hasDeepKey(traits, ["max", "total", "kcal"]):
		addMaxTotalCaloriesFactor(csp, traits)
	

##
# Function: addSameNameFactors
# ----------------------------
# Add binary factors between all name variables to make sure no two ingredients
# have the same name.
##
def addSameNameFactors(csp, traits):
	nameVars = getNameVars(csp)
	n = len(nameVars)
	for i in xrange(n-1):
        for j in xrange(i+1, n):
			csp.add_binary_factor(nameVars[i], nameVars[j], lambda x, y: x != y)

def addMaxTotalCaloriesFactor(csp, traits):
	def conversionFxn(nameAssignment, amountAssignment):
		return nutrition.unitConvert(nameAssignment, amountAssignment, "grams", "kcal")
	sumVal = traits["max"]["total"]["kcal"]
	get_ingredient_sum_variable(csp, traits, "kcal", sumVal, "max", conversionFxn)

def getNameVars(csp):
	return sorted([var for var in csp.variables if var.startswith("name")])

def getAmountVars(csp):
	return sorted([var for var in csp.variables if var.startswith("amount")])

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

############################################################
# CSP examples.

def get_or_variable(csp, name, variables, value):
    """
    Create a new variable with domain [True, False] that can only be assigned to
    True iff at least one of the |variables| is assigned to |value|. You should
    add any necessary intermediate variables, unary factors, and binary
    factors to achieve this. Then, return the name of this variable.

    @param name: Prefix of all the variables that are going to be added.
        Can be any hashable objects. For every variable |var| added in this
        function, it's recommended to use a naming strategy such as
        ('or', |name|, |var|) to avoid conflicts with other variable names.
    @param variables: A list of variables in the CSP that are participating
        in this OR function. Note that if this list is empty, then the returned
        variable created should never be assigned to True.
    @param value: For the returned OR variable being created to be assigned to
        True, at least one of these variables must have this value.

    @return result: The OR variable's name. This variable should have domain
        [True, False] and constraints s.t. it's assigned to True iff at least
        one of the |variables| is assigned to |value|.
    """
    result = ('or', name, 'aggregated')
    csp.add_variable(result, [True, False])

    # no input variable, result should be False
    if len(variables) == 0:
        csp.add_unary_factor(result, lambda val: not val)
        return result

    # Let the input be n variables X0, X1, ..., Xn.
    # After adding auxiliary variables, the factor graph will look like this:
    #
    # ^--A0 --*-- A1 --*-- ... --*-- An --*-- result--^^
    #    |        |                  |
    #    *        *                  *
    #    |        |                  |
    #    X0       X1                 Xn
    #
    # where each "--*--" is a binary constraint and "--^" and "--^^" are unary
    # constraints. The "--^^" constraint will be added by the caller.
    for i, X_i in enumerate(variables):
        # create auxiliary variable for variable i
        # use systematic naming to avoid naming collision
        A_i = ('or', name, i)
        # domain values:
        # - [ prev ]: condition satisfied by some previous X_j
        # - [equals]: condition satisfied by X_i
        # - [  no  ]: condition not satisfied yet
        csp.add_variable(A_i, ['prev', 'equals', 'no'])

        # incorporate information from X_i
        def factor(val, b):
            if (val == value): return b == 'equals'
            return b != 'equals'
        csp.add_binary_factor(X_i, A_i, factor)

        if i == 0:
            # the first auxiliary variable, its value should never
            # be 'prev' because there's no X_j before it
            csp.add_unary_factor(A_i, lambda b: b != 'prev')
        else:
            # consistency between A_{i-1} and A_i
            def factor(b1, b2):
                if b1 in ['equals', 'prev']: return b2 != 'no'
                return b2 != 'prev'
            csp.add_binary_factor(('or', name, i - 1), A_i, factor)

    # consistency between A_n and result
    # hacky: reuse A_i because of python's loose scope
    csp.add_binary_factor(A_i, result, lambda val, res: res == (val != 'no'))
    return result


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

