#!/usr/bin/python
''' Detects the tstart and end trimpoints of an audio file. '''
import sys
import numpy
import sklearn.cluster
import time
import scipy
import os
import audioFeatureExtraction as aF
import audioTrainTest as aT
import audioBasicIO
import matplotlib.pyplot as plt
from scipy.spatial import distance
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sklearn.discriminant_analysis
import audioSegmentation as aS
import itertools as it

def usage():
    print "This script requires an audio file as a parameter"
    print "\n"
    print "eg. detect"

if len(sys.argv) > 1:
    inputWavFile = sys.argv[1]
    if not os.path.isfile(inputWavFile):
        print "Cannot locate audio file " + inputWavFile

    modelName = "model/svmFinalAll"
    if not os.path.isfile(modelName):
        print "Cannot locate model file " + modelName

    modelType = "svm"
    gtFile = ""
    returnVal = aS.mtFileClassification(inputWavFile, modelName, modelType, False, gtFile)
    flagsInd = returnVal[0]
    classNames = returnVal[1]

    flags = [classNames[int(f)] for f in flagsInd]
    (segs, classes) = aS.flags2segs(flags, 1)

    reversed_segs = segs[::-1]
    reversed_classes = classes[::-1]

    #print "\n"
    #for s in range(len(segs)):
    #    print str(segs[s]) + ": " + str(classes[s]) + "\n"
    #print "\n"

    output = "{"

    for s in range(len(segs)):
        segment = segs[s]
        diff = int(segment[1]) - int(segment[0])
        if str(classes[s]) == "speech" and diff > 3:
            startpoint = segs[s]
            #print "start trim: " + str(int(startpoint[0]*1000))
            output = output + "'start':'" + str(int(startpoint[0]*1000)) + "','"
            break

    for s in range(len(reversed_segs)):
        segment = reversed_segs[s]
        diff = int(segment[1]) - int(segment[0])
        if str(reversed_classes[s]) == "speech" and diff > 5:
            endpoint = reversed_segs[s]
            #print "end trim: " + str((int(endpoint[1]) + 10)*1000)
            output = output + "end':'" + str((int(endpoint[1]) + 10)*1000) + "'}"
            break
    
    print output

else:
    usage()
