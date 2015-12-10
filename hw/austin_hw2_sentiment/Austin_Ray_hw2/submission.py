#!/usr/bin/python

import random
import collections
import math
import sys
from collections import Counter
from util import *
from math import sqrt
from itertools import *
import numpy as np

from copy import deepcopy
import pdb

############################################################
# Problem 3: binary classification
############################################################

############################################################
# Problem 3a: feature extraction

def extractWordFeatures(x):
    """
    Extract word features for a string x. Words are delimited by
    whitespace characters only.
    @param string x: 
    @return dict: feature vector representation of x.
    Example: "I am what I am" --> {'I': 2, 'am': 2, 'what': 1}
    """

    # BEGIN_YOUR_CODE (around 5 lines of code expected)

    wordFeatures = {}

    wordFeatures = Counter(x.split())
    return wordFeatures

    # END_YOUR_CODE

############################################################
# Problem 3b: stochastic gradient descent

def makeBinaryPredictor(w, featureExtractor):
    def binaryPredictor(x):
        return (1 if (score(w, featureExtractor(x)) >= 0) else -1)
    return binaryPredictor

def score(w, phi):
    return dotProduct(w, phi);

def margin(w, phi, y):
    return dotProduct(w, phi) * y

def residual(w, phi, y):
    return score(w, phi) - y

def hingeLoss(w, phi, y):
    return max(0, 1 - margin(w, phi, y))


def dHingeLoss(w, phi, y):
    d_hloss = {}
    # increment(d_hloss, 0, w)

    cur_margin = margin(w, phi, y)
    
    if (cur_margin < 1):
        increment(d_hloss, -y, phi)

    return d_hloss


def StochasticGradientDescent(w, D_train, stepSize, featureExtractor):
    for example in D_train:
        phi = featureExtractor(example[0])
        y = example[1]
        increment(w, -stepSize, dHingeLoss(w, phi, y))
        #print "w: %r" % w


def learnPredictor(trainExamples, testExamples, featureExtractor):
    '''
    Given |trainExamples| and |testExamples| (each one is a list of (x,y)
    pairs), a |featureExtractor| to apply to x, and the number of iterations to
    train |numIters|, return the weight vector (sparse feature vector) learned.

    You should implement stochastic gradient descent.

    Note: only use the trainExamples for training!
    You should call evaluatePredictor() on both trainExamples and testExamples
    to see how you're doing as you learn after each iteration.
    numIters refers to a variable you need to declare. It is not passed in.
    '''
    weights = {} # feature => weight
    # BEGIN_YOUR_CODE (around 15 lines of code expected)

    phi_arr = []
    y_arr = []


    iters = 11
    eta = 0.062

    for i in xrange(1, iters+1):
        StochasticGradientDescent(weights, trainExamples, eta, featureExtractor)
        binaryPredictor = makeBinaryPredictor(weights, featureExtractor)

        trainError = evaluatePredictor(trainExamples, binaryPredictor)

        print "Iteration %d" % i
        print "Train error: %f" % trainError
        print "Test error: %f\n" % evaluatePredictor(testExamples, binaryPredictor)

        # Apparently I can't do this...
        #if (trainError < 0.0000001):
        #    return weights

    # END_YOUR_CODE
    # return makeUnitVector(weights)
    return weights


def makeUnitVector(sparse_vec):
    sv_new = {}
    norm = sqrt(sum([(val ** 2) for val in sparse_vec.values()]))
    increment(sv_new, 1.0 / norm, sparse_vec)
    return sv_new










############################################################
# Problem 3c: generate test case

def generateDataset(numExamples, weights):
    '''
    Return a set of examples (phi(x), y) randomly which are classified correctly by
    |weights|.
    '''
    random.seed(42)
    # Return a single example (phi(x), y).
    # phi(x) should be a dict whose keys are a subset of the keys in weights
    # and values can be anything (randomize!) with a nonzero score under the given weight vector.
    # y should be 1 or -1 as classified by the weight vector.
    def generateExample():
        # BEGIN_YOUR_CODE (around 2 lines of code expected)
        phi = {}
        score_sum = 0
        for item in weights.items():
            r = random.randint(0, 100)
            score_sum += item[1] * r
            phi[item[0]] = r

        if score_sum == 0:
            key = (weights.keys())[0]
            score_sum -= weights[key] * phi[key]
            phi[key] += 1
            score_sum += weights[key] * phi[key]

        y = (1 if score_sum >= 0 else -1)

        # END_YOUR_CODE
        return (phi, y)

    return [generateExample() for _ in range(numExamples)]



############################################################
# Problem 3f: character features

def extractCharacterFeatures(n):
    '''
    Return a function that takes a string |x| and returns a sparse feature
    vector consisting of all n-grams of |x| without spaces.
    EXAMPLE: (n = 3) "I like tacos" --> {'Ili': 1, 'lik': 1, 'ike': 1, ...
    You may assume that n >= 1.
    '''
    def extract(x):
        # BEGIN_YOUR_CODE (around 10 lines of code expected)
        no_spaces = x.replace(" ", "").replace("\t", "")
        n_grams = [no_spaces[ind : ind + n] for ind in xrange(0, len(no_spaces) - n + 1)]

        return Counter(n_grams)
        # END_YOUR_CODE
    return extract

def extractCharacterFeatures2(n):
    '''
    Return a function that takes a string |x| and returns a sparse feature
    vector consisting of all n-grams of |x| without spaces.
    EXAMPLE: (n = 3) "I like tacos" --> {'Ili': 1, 'lik': 1, 'ike': 1, ...
    You may assume that n >= 1.
    '''
    def extract(x):
        # BEGIN_YOUR_CODE (around 10 lines of code expected)
        no_spaces = x.replace(" ", "").replace("\t", "")
        n_grams = [no_spaces[ind : ind + n] for ind in xrange(0, len(no_spaces) - n + 1)]

        n2 = n + 1
        n_plus_one_grams = [no_spaces[ind : ind + n2] for ind in xrange(0, len(no_spaces) - n2 + 1)]

        return Counter(chain(n_grams, n_plus_one_grams))
        # END_YOUR_CODE
    return extract


 ### ANSWER TO 3g:
 # 4-grams and 5-grams give approximately the same test error on polarity.dev after training.
 # Their test errors are 0.292 and 0.297, respectively, which is close to 0.27
 # I suspect 4-grams and 5-grams are the best because a lot of words are 4 or 5 letters, so a lot
 # of the n-grams correspond to real words that mean something in reviews. Additionally, while it's
 # likely that a 3-letter word could appear in another word, a 4 or 5-letter word appearing in another
 # word is less likely, so "false positives" are less likely.
 #
 # When I try to do n-grams with both 4-grams and 5-grams as features at the same time, the error
 # goes down to 0.284, a full 1% lower than the average of their respective individual errors.
 # 
 # "That movie was supercalifragilisticexpealadocious", +1
 # n-grams would perform well, as it has seen the substring "super" before and tightly
 # correlated it with positive reviews. Word-extraction would do badly since
 # it probably has't seen supercalifragilisticexpealadocious before and
 # won't have a sense for what it means. "That", "movie", and "was" are up in the air -
 # it's possible that word extraction could classify them as anything. Therefore,
 # n-grams performs better because it can get a sense of what supercalifragilisticexpealadocious
 # means without having seen it before (due to the fact that it knows super) and will give this
 # review a high score, whereas word-extraction may not.


############################################################
# Problem 3h: extra credit features

def extractExtraCreditFeatures(x):
    # BEGIN_YOUR_CODE (around 1 line of code expected)
    return extractExtraCreditFeatures7(x)
    # END_YOUR_CODE

def extractExtraCreditFeatures2(x):
    # BEGIN_YOUR_CODE (around 1 line of code expected)
    words = x.split()
    chain_2 = ["".join([words[i], words[i+1]]) for i in xrange(0, len(words) - 1)]

    all_features = words + chain_2

    return Counter(all_features)
    # END_YOUR_CODE

def extractExtraCreditFeatures3(x):
    # BEGIN_YOUR_CODE (around 1 line of code expected)
    words = x.split()
    chain_2 = [" ".join([words[i], words[i+1]]) for i in xrange(0, len(words) - 1)]

    all_features = words + chain_2

    return Counter(all_features)
    # END_YOUR_CODE

def extractExtraCreditFeatures4(x):
    # BEGIN_YOUR_CODE (around 1 line of code expected)
    words = x.split()
    chain_2 = [" ".join([words[i], words[i+1]]) for i in xrange(0, len(words) - 1)]

    all_features = words + chain_2

    return Counter(all_features)
    # END_YOUR_CODE

def extractExtraCreditFeatures5(x):
    # BEGIN_YOUR_CODE (around 1 line of code expected)
    global en_words
    n_arr = [4, 5]
    no_spaces = x.replace(" ", "").replace("\t", "")
    n_grams_arr = []
    for n in n_arr:
        n_grams = [no_spaces[ind : ind + n] for ind in xrange(0, len(no_spaces) - n + 1) if no_spaces[ind : ind + n] in en_words]
        chain_2 = [" ".join([n_grams[i], n_grams[i+1]]) for i in xrange(0, len(n_grams) - 1)]
        n_grams_arr = n_grams_arr + n_grams + chain_2

    #word_counter = extractWordFeatures(x)
    #final_counter = n_gram_counter | word_counter
    #return final_counter

    return Counter(n_grams_arr)
    # END_YOUR_CODE

def extractExtraCreditFeatures6(x):
# BEGIN_YOUR_CODE (around 1 line of code expected)
    return extractExtraCreditFeatures4(x) | extractExtraCreditFeatures5(x)
    # END_YOUR_CODE

def extractExtraCreditFeatures7(x):
    # BEGIN_YOUR_CODE (around 1 line of code expected)
    global en_words
    

    words = x.split()
    two_grams = [" ".join([words[i], words[i+1]]) for i in xrange(0, len(words) - 1)]

    words_2 = [word for word in words if word not in ['!', '?', '-', ',', '.', '(', ')']]

    feature_dict = Counter(words + two_grams)

    #feature_dict["# words"] = len(words)
    #feature_dict["# english words"] = len([word for word in words_2 if word in en_words])
    #feature_dict["# letters"] = len(list(x))
   # feature_dict["# 1-letter words"] = len([word for word in words_2 if len(word) is 1])
   # feature_dict["# 2-letter words"] = len([word for word in words if len(word) is 2])
  #  feature_dict["# 7-letter words"] = len([word for word in words if len(word) is 7])
    #feature_dict["# 8-letter words"] = len([word for word in words if len(word) is 8])
  #  feature_dict["# 9-letter words"] = len([word for word in words if len(word) is 9])
    feature_dict["# exclamations"] = (x.count('!'))
    feature_dict["# hyphens"] = x.count('-')
    feature_dict["# question marks"] = (x.count('-'))
   # feature_dict["# other punctuation"] = x.count('.') + x.count(',') + x.count('(') + x.count(')')

    return feature_dict
    # END_YOUR_CODE





############################################################
# Problem 4: k-means
############################################################


def kmeans(examples, K, maxIters):
    '''
    examples: list of examples, each example is a string-to-double dict representing a sparse vector.
    K: number of desired clusters. Assume that 0 < K <= |examples|.
    maxIters: maximum number of iterations to run for (you should terminate early if the algorithm converges).
    Return: (length K list of cluster centroids,
            list of assignments, (i.e. if examples[i] belongs to centers[j], then assignments[i] = j)
            final reconstruction loss)
    '''
    # BEGIN_YOUR_CODE (around 35 lines of code expected)
    N = len(examples)
    centroids = [deepcopy(random.choice(examples)) for _ in range(0, K)]
    assignments = [0 for _ in range(0, N)]
    
    prev_loss = 0
    cur_loss = 0

    for _ in xrange(0, maxIters):
        updateAssignments(examples, assignments, N, centroids, K)
        updateCentroids(examples, assignments, N, centroids, K)
        cur_loss = kmeansLoss(examples, assignments, N, centroids, K)
        if (abs(prev_loss - cur_loss) < 0.000001):
            break
        else:
            prev_loss = cur_loss
        print cur_loss

    return [centroids, assignments, cur_loss]

    # END_YOUR_CODE

def kmeans_4c_mod(examples, K, maxIters):
    '''
    examples: list of examples, each example is a string-to-double dict representing a sparse vector.
    K: number of desired clusters. Assume that 0 < K <= |examples|.
    maxIters: maximum number of iterations to run for (you should terminate early if the algorithm converges).
    Return: (length K list of cluster centroids,
            list of assignments, (i.e. if examples[i] belongs to centers[j], then assignments[i] = j)
            final reconstruction loss)
    '''
    # BEGIN_YOUR_CODE (around 35 lines of code expected)
    (examples, assignments) = zip(*examples)

    N = len(examples)
    centroids = [deepcopy(random.choice(examples)) for _ in range(0, K)]
    
    prev_loss = 0
    cur_loss = 0

    for _ in xrange(0, maxIters):
        updateCentroids(examples, assignments, N, centroids, K)
        cur_loss = kmeansLoss(examples, assignments, N, centroids, K)
        if (abs(prev_loss - cur_loss) < 0.000001):
            break
        else:
            prev_loss = cur_loss
        print cur_loss

    return [centroids, assignments, cur_loss]

    # END_YOUR_CODE

def updateAssignments(examples, assignments, N, centroids, K):
    for ex_ind in xrange(0, N):
        norm_sqrs = []
        for u_ind in xrange(0, K):
            u = centroids[u_ind]
            ex = examples[ex_ind]
            norm_sqrs.append(sparseSubNormSquared(ex, u))
        assignments[ex_ind] = min(enumerate(norm_sqrs), key=lambda (ind, val): val)[0]

def updateCentroids(examples, assignments, N, centroids, K):
    # keys are indices in centroids, values are indices of all examples that fall into that centroid
    assign_dict = {u_ind: [] for u_ind in xrange(0, K)} 
    for ex_ind in xrange(0, N):
        u_ind = assignments[ex_ind]
        assign_dict[u_ind].append(ex_ind)

    for (u_ind, ex_inds) in assign_dict.items():
        ex_sum = {}
        for ex_ind in ex_inds:
            increment(ex_sum, 1, examples[ex_ind])
        num_ex = len(ex_inds)
        # Multiply the ex_sum sparse array by 1/(number of examples in this centroid)
        for (key, val) in ex_sum.items():
            ex_sum[key] = val * (1.0 / num_ex)
        # Update the centroid
        centroids[u_ind] = ex_sum

def kmeansLoss(examples, assignments, N, centroids, K):
    loss = 0
    for ex_ind in xrange(0, N):
        u_ind = assignments[ex_ind]
        u = centroids[u_ind]
        ex = examples[ex_ind]
        loss += sparseSubNormSquared(ex, u)
    return loss

def sparseSubNormSquared(d1, d2):
    subNorm = 0
    for key in set(d1.keys() + d2.keys()):
        diff = d1.get(key, 0.0) - d2.get(key, 0.0)
        subNorm += diff**2
    return subNorm






####################
######## Tests #####
####################

#####
# 4b
#####

def test_kmeans_updaters():
    K = 2
    x1 = {0:0, 1:19}
    x2 = {0:-1, 1:20}
    x3 = {0:0, 1:15}
    x4 = {0:5, 1:-5}
    x5 = {0:6, 1:-8}
    x6 = {0:9, 1:-6}
    examples = [x1, x2, x3, x4, x5, x6]
    N = len(examples)
    centroids = [random.choice(examples) for _ in range(0, K)]
    assignments = [0 for _ in range(0, N)]
    updateAssignments(examples, assignments, N, centroids, K)
    updateCentroids(examples, assignments, N, centroids, K)
    cur_loss = kmeansLoss(examples, assignments, N, centroids, K)
    print assignments
    print centroids
    print cur_loss

def test_kmeans1():
    K = 2
    x1 = {0:0, 1:19}
    x2 = {0:-1, 1:20}
    x3 = {0:0, 1:15}
    x4 = {0:5, 1:-5}
    x5 = {0:6, 1:-8}
    x6 = {0:9, 1:-6}
    examples = [x1, x2, x3, x4, x5, x6]
    maxIters = 10
    print kmeans(examples, K, maxIters)

def test_kmeans2():
    K = 2
    numExamples = 100
    fillerWords = 2
    examples = generateClusteringExamples(numExamples, 20, 2)
    print examples
    maxIters = 10
    (centers, assignments, loss) = kmeans(examples, K, maxIters)
    outputClusters("output2.txt", examples, centers, assignments)

def test_kmeans3():
    # clusters will be: bad plot, good plot, bad acting, good acting, bad music, good music
    K = 6
    numExamples = 1000
    fillerWords = 2
    examples = generateClusteringExamples(numExamples, 20, 2)
    print examples
    maxIters = 10
    (centers, assignments, loss) = kmeans(examples, K, maxIters)
    outputClusters("output3.txt", examples, centers, assignments)

def test_kmeans_all():
    test_kmeans_updaters()
    test_kmeans1()
    test_kmeans2()
    test_kmeans3()




#####
# 3c
#####

def wordCountsToString(phi):
    sentence = " "
    for (word, count) in phi.items():
        sentence += (word + " ") * count
    return sentence

def normalizeVec1ToVec2(vec1, vec2):
    magic_key = (vec1.keys())[0]
    magic_num = vec1[magic_key] / vec2[magic_key]
    for key in vec1.keys():
        vec1[key] = vec1[key] / magic_num

def test3c_1():
    weights = {"xxx": 1, "mom": -2, "mad": -1, "bob": 2, "hi": -3, "bye": -2, "jive": 3}
    numExamples = 100
    rawExamples = generateDataset(numExamples, weights)
    # print rawExamples
    trainExamples = [(wordCountsToString(phi), y) for (phi, y) in rawExamples]
    learned_weights = learnPredictor(trainExamples, trainExamples, extractWordFeatures)
    normalizeVec1ToVec2(learned_weights, weights)
    print "Original weights: %r" % weights
    print "Learned weights: %r" % learned_weights

def test3c_2():
    weights = {"xxx": 1, "mom": -2, "mad": -1, "bob": 2, "hi": -3, "bye": -2, "jive": 3}
    numExamples = 500
    rawExamples = generateDataset(numExamples, weights)
    # print rawExamples
    trainExamples = [(wordCountsToString(phi), y) for (phi, y) in rawExamples]
    learned_weights = learnPredictor(trainExamples, trainExamples, extractWordFeatures)
    normalizeVec1ToVec2(learned_weights, weights)
    print "Original weights: %r" % weights
    print "Learned weights: %r" % learned_weights

def test3c_3():
    weights = {"xxx": 1, "mom": -2, "mad": -1, "bob": 2, "hi": -3, "bye": -2, "jive": 3}
    numExamples = 1000
    rawExamples = generateDataset(numExamples, weights)
    # print rawExamples
    trainExamples = [(wordCountsToString(phi), y) for (phi, y) in rawExamples]
    learned_weights = learnPredictor(trainExamples, trainExamples, extractWordFeatures)
    normalizeVec1ToVec2(learned_weights, weights)
    print "Original weights: %r" % weights
    print "Learned weights: %r" % learned_weights

def test3c_0():
    trainExamples = readExamples('polarity.train')
    devExamples = readExamples('polarity.dev')
    weights_dict = {}
    featureExtractor = extractWordFeatures
    weights = learnPredictor(trainExamples, devExamples, featureExtractor)
    print evaluatePredictor(devExamples, makeBinaryPredictor(weights, featureExtractor))

def test3c_all():
    test3c_1()
    print
    test3c_2()
    print
    test3c_3()



#####
# 3f
#####

def test_extractCharacterFeatures():
    print extractCharacterFeatures2(3)("I like tac   os")

def test_ngrams():
    trainExamples = readExamples('polarity.train')
    devExamples = readExamples('polarity.dev')
    weights_dict = {}
    for n in range(4, 6):
        featureExtractor = extractCharacterFeatures2(n)
        weights = learnPredictor(trainExamples, devExamples, featureExtractor)
        weights_dict[n] = evaluatePredictor(devExamples, makeBinaryPredictor(weights, featureExtractor)) 
    print weights_dict



#####
# 3h
#####

def test_extractExtraCreditFeatures():
    print extractExtraCreditFeatures("Hey I like    tacos dude and dudets")

def test_extraCredit():
    trainExamples = readExamples('polarity.train')
    devExamples = readExamples('polarity.dev')
    weights_dict = {}
    featureExtractor = extractExtraCreditFeatures7
    weights = learnPredictor(trainExamples, devExamples, featureExtractor)
    print evaluatePredictor(devExamples, makeBinaryPredictor(weights, featureExtractor))



fp = open('words', 'r')
en_words = {line.rstrip('\n') for line in fp}

#test3c_0()

#test_extractCharacterFeatures()
#test_ngrams()

#test_extractExtraCreditFeatures()
#test_extraCredit()

#test_kmeans_all()