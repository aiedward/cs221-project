import shell
import util
import wordsegUtil

############################################################
# Problem 1b: Solve the segmentation problem under a unigram model

class SegmentationProblem(util.SearchProblem):
    def __init__(self, query, unigramCost):
        self.query = query
        self.unigramCost = unigramCost

    def startState(self):
        # BEGIN_YOUR_CODE (around 1 line of code expected)
        return (0, 0)
        # END_YOUR_CODE

    def isGoal(self, state):
        # BEGIN_YOUR_CODE (around 2 lines of code expected)
        queryLen = len(self.query)
        return state == (queryLen, queryLen)
        # END_YOUR_CODE

    def succAndCost(self, state):
        # BEGIN_YOUR_CODE (around 10 lines of code expected)
        returnList = [("cut", (state[1], state[1]), self.unigramCost(self.query[state[0]:state[1]]))]

        if (state[1] != len(self.query)):
            returnList.append(("extend", (state[0], state[1] + 1), 0))

        return returnList
        # END_YOUR_CODE

def segmentWords(query, unigramCost):
    if len(query) == 0:
        return ''

    ucs = util.UniformCostSearch(verbose=0)
    ucs.solve(SegmentationProblem(query, unigramCost))

    # BEGIN_YOUR_CODE (around 3 lines of code expected)
    index = 0
    returnWords = []
    curWord = ""

    for action in ucs.actions:
        if action is "extend":
            curWord += query[index]
            index += 1
        else:
            returnWords.append(curWord)
            curWord = ""

    return ' '.join(returnWords)
    # END_YOUR_CODE

############################################################
# Problem 2b: Solve the vowel insertion problem under a bigram cost

class VowelInsertionProblem(util.SearchProblem):
    def __init__(self, queryWords, bigramCost, possibleFills):
        self.queryWords = queryWords
        self.bigramCost = bigramCost
        self.possibleFills = possibleFills

    def startState(self):
        # BEGIN_YOUR_CODE (around 1 line of code expected)
        return (wordsegUtil.SENTENCE_BEGIN, 0)
        # END_YOUR_CODE

    def isGoal(self, state):
        # BEGIN_YOUR_CODE (around 2 lines of code expected)
        return state[1] == len(self.queryWords)
        # END_YOUR_CODE

    def succAndCost(self, state):
        # BEGIN_YOUR_CODE (around 10 lines of code expected)
        noVowelWord = self.queryWords[state[1]]

        actions = self.possibleFills(noVowelWord)

        returnArr = []
        if len(actions) == 0:
            returnArr.append((noVowelWord, (noVowelWord, state[1] + 1), self.bigramCost(state[0], noVowelWord)))

        for action in actions:
            returnArr.append((action, (action, state[1] + 1), self.bigramCost(state[0], action)))

        return returnArr
        # END_YOUR_CODE

def insertVowels(queryWords, bigramCost, possibleFills):
    # BEGIN_YOUR_CODE (around 3 lines of code expected)
    queryWords = [word.replace(" ", "") for word in queryWords if word is not ""]

    ucs = util.UniformCostSearch(verbose=1)
    ucs.solve(VowelInsertionProblem(queryWords, bigramCost, possibleFills))

    return " ".join(ucs.actions)
    # END_YOUR_CODE

############################################################
# Problem 3b: Solve the joint segmentation-and-insertion problem

class JointSegmentationInsertionProblem(util.SearchProblem):
    def __init__(self, query, bigramCost, possibleFills):
        self.query = query
        self.bigramCost = bigramCost
        self.possibleFills = possibleFills

    def startState(self):
        # BEGIN_YOUR_CODE (around 2 lines of code expected)
        return (wordsegUtil.SENTENCE_BEGIN, 0, 0)
        # END_YOUR_CODE

    def isGoal(self, state):
        # BEGIN_YOUR_CODE (around 2 lines of code expected)
        return state[1] == len(self.query)
        # END_YOUR_CODE

    def succAndCost(self, state):
        # BEGIN_YOUR_CODE (around 15 lines of code expected)
        noVowelWord = self.query[state[1]:state[2]]

        returnList = []

        if (state[2] != len(self.query)):
            returnList.append((1, (state[0], state[1], state[2] + 1), 0))

        actions = self.possibleFills(noVowelWord)

        for action in actions:
            returnList.append((action, (action, state[2], state[2]), self.bigramCost(state[0], action)))

        return returnList
        # END_YOUR_CODE

def segmentAndInsert(query, bigramCost, possibleFills):

    if len(query) == 0:
        return ''

    # BEGIN_YOUR_CODE (around 5 lines of code expected)
    ucs = util.UniformCostSearch(verbose=0)
    ucs.solve(JointSegmentationInsertionProblem(query, bigramCost, possibleFills))

    return ' '.join([action for action in ucs.actions if action is not 1])
    # END_YOUR_CODE

############################################################

if __name__ == '__main__':
    shell.main()
