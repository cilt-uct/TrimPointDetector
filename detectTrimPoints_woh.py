#!/usr/bin/python
''' Detects the start and end trimpoints of an audio file. '''
import sys
import numpy
import sklearn.cluster
import time
import scipy
import os
from pyAudioAnalysis import audioFeatureExtraction as aF
from pyAudioAnalysis import audioTrainTest as aT
from pyAudioAnalysis import audioBasicIO
import matplotlib.pyplot as plt
from scipy.spatial import distance
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sklearn.discriminant_analysis
from pyAudioAnalysis import audioSegmentation as aS
import itertools as it
import wave
import contextlib

def usage():
    print "This script requires an audio file as a parameter"
    print "\n"
    print "eg. detect"

if len(sys.argv) > 1:

    inputWavFile = sys.argv[1]
    outputTextFile = sys.argv[2]

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

    audio_trim_duration = 0
    with contextlib.closing(wave.open(inputWavFile,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        audio_trim_duration = int(duration*1000)

    speech  = 1 
    chatter = 0 # remove chatter
    other   = 0 # remove other
    threshold = 90 # 1:30

    output_arr = []
    step = "none"
    segment_prev = 0
   
    #print "\n"
    for s in range(len(segs)):
	segment = segs[s]
        diff = int(segment[1]) - int(segment[0])
	#print str(int(segment[0])*1000) +"-"+ str(int(segment[1])*1000)  + " : " + str(classes[s]) + " (" + str(diff) + ")\n"

	if ((chatter == 0) and (str(classes[s]) == "chatter") and (diff >= threshold)) or \
	   ((other == 0) and (str(classes[s]) == "other") and (diff >= threshold)):
		#print str(int(segment[0])*1000) +"-"+ str(int(segment[1])*1000)  + " : " + str(classes[s]) + " (" + str(diff) + ")\n"
		segment_start = int(segment[0])*1000
		segment_end = int(segment[1])*1000

		#print ("step: " + step)
		if (step == "none") and (segment_start >= 5000):
			# first segment 0 - A
			output_arr.append(0)
		
		if (segment_start - segment_prev <= 10000):
			# means that the next chatter/other segment is less than 10 seconds from start of this segment
			# remove the end of the previous segment and add it to this one
			#print ("arr: " + str(output_arr.count()))
			if (len(output_arr) >= 1):
                               output_arr.pop()
		else:	
			output_arr.append(segment_start)
		
		if (audio_trim_duration - segment_end >= 5000):
			# if the end is further away than 5 seconds then we can use this end point
			output_arr.append(segment_end)
		#else:
		#	output_arr.append(audio_trim_duration)

		segment_prev = segment_end
	       	step = str(classes[s])

    if (len(output_arr) == 0):
	output_arr.append(0)
	output_arr.append(audio_trim_duration);

    '''
    print('audio_trim_file=' + inputWavFile +'\n')
    print('audio_trim_out_file=' + outputTextFile +'\n')
    print('audio_trim_duration=' + str(audio_trim_duration) +'\n')
    print('audio_trim_segments=' + str(';'.join(str(e) for e in output_arr)) +'\n')

    print(str(len(output_arr)) +'\n')
    '''

    f = open(outputTextFile, 'w')
    f.write('audio_trim_file=' + inputWavFile +'\n')
    f.write('audio_trim_out_file=' + outputTextFile +'\n')
    f.write('audio_trim_duration=' + str(audio_trim_duration) +'\n')
    f.write('audio_trim_segments=' + str(';'.join(str(e) for e in output_arr)) +'\n')
    f.close()

    #print("audio_trim_file=" + inputWavFile)

    '''
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
    
    #print output
    
else:
    usage()
    sys.exit(os.EX_USAGE)
'''
sys.exit(os.EX_OK) # code 0, all ok
