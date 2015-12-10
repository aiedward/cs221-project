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

	# Solve the csp of choosing aliases (identities) for each ingredient
	solveAliasCSP(verbose, traits)

	# With each ingredient now assigned an alias, solve the csp of choosing
	# amounts (mass in grams) for each ingredient
	solveAmountCSP(verbose, traits)

	# Print status update
	if verbose:
		print "csp.py ran successfully"

	return {k: v for k, v in traits.items() if k in ["alias_choices", "amount choices"]}

##
# Function: solveAliasCSP
# ---------------------------
# Solve the problem of picking aliases for the ingredients given 
# a set of constraints.
##
def solveAliasCSP(verbose, traits):
	csp = util.CSP()
	addVariables(csp, traits, "alias")
	addFactors(csp, traits, "alias")

	solver = util.BacktrackingSearch(numSolutions=100, verbose=False)
	solver.solve(csp)

	traits["alias_choices"] = solver.optimalAssignment

##
# Function: solveAmountCSP
# ---------------------------
# Solve the problem of picking amounts for the ingredients given pre-picked
# aliases and a set of constraints.
##
def solveAmountCSP(verbose, traits):
	csp = util.CSP()
	addVariables(csp, traits, "amount")
	addFactors(csp, traits, "amount")

	solver = util.BacktrackingSearch(numSolutions=10, verbose=False)
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
		for var in nameVariables:
			csp.add_variable(var, nameDomain)

	elif whichCSP == "amount":
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
# Function: addFactors
# --------------------------
#
##
def addFactors(csp, traits, whichCSP):
	if whichCSP == "alias":
		addSameNameFactors(csp, traits)

	if whichCSP == "amount":
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

##
# Function: addMaxTotalCaloriesFactor
# -----------------------------------
#
##
def addMaxTotalCaloriesFactor(csp, traits):
	def conversionFxn(nameAssignment, amountAssignment):
		return nutrition.unitConvert(nameAssignment, amountAssignment, "grams", "kcal")
	sumVal = traits["max"]["total"]["kcal"]
	get_ingredient_sum_variable(csp, traits, "kcal", sumVal, "max", conversionFxn)

##
# Function: addMaxTotalCaloriesFactor
# -----------------------------------
##
def getNameVars(csp):
	return sorted([var for var in csp.variables if var.startswith("alias")])

def getAmountVars(csp):
	return sorted([var for var in csp.variables if var.startswith("amount")])



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




