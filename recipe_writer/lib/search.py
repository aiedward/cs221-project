##
# File: search.py
# ---------------
#
##
def run(verbose):
    # These variables will likely be fed through run()'s arguments later
    traitsDataPath = os.path.join(constants.PATH_TO_ROOT, "res", "csp_defaultTraits.json")
    traits = util.loadJSONDict(traitsDataPath)

    traits["verbose"] = verbose

    if traits["verbose"]:
        print "Creating recipe with %d ingredients." % traits["num_ingredients"]




if __name__ == "__main__":
    run(True)
