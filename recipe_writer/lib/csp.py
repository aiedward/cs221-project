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
# Function: addFactors
# --------------------------
#
##
def addFactors(csp, traits, whichCSP):
	if whichCSP == "alias":
		constraints = traits["alias_constraints"]
		addFactors_sameName(csp, traits)
		if "free_of_nuts" in constraints:
			addFactors_freeOfNuts(csp, traits)
		if "free_of_meat" in constraints:
			addFactors_freeOfMeat(csp, traits)

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
			csp.add_binary_factor(aliasVars[i], aliasVars[j], lambda x, y: x != y)

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




