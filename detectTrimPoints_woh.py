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
import time

def usage():
    print "This script requires an audio file as a parameter"
    print "\n"
    print "eg. detect"

if len(sys.argv) > 1:

    inputWavFile = sys.argv[1]
    outputTextFile = sys.argv[2]

    speech  = 1 # ALWAYS
    non_speech = sys.argv[3] 

    threshold = int(sys.argv[4]) # 1:30
    start_time = time.time() 	

    if not os.path.isfile(inputWavFile):
        print "Cannot locate audio file " + inputWavFile

    modelName = "model/svmModel"
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

    # get the duration of the wave file
    audio_trim_duration = 0
    with contextlib.closing(wave.open(inputWavFile,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        audio_trim_duration = int(duration*1000)

    output_arr = []
    step = "none"
    segment_prev = 0
    
    stats = [0,0, 0,0] #numpy.zeros((2, 2))


    #print "\n"
    for s in range(len(segs)):
	segment = segs[s]
        diff = int(segment[1]) - int(segment[0])
	#print str(int(segment[0])*1000) +"-"+ str(int(segment[1])*1000)  + " : " + str(classes[s]) + " (" + str(diff) + ")\n"

        if (str(classes[s]) == "speech"):
            stats[0] += 1
            stats[1] += diff        

        if (str(classes[s]) == "non-speech"):
            stats[2] += 1
            stats[3] += diff

	if (non_speech == 0) and (str(classes[s]) == "non-speech") and (diff >= threshold):
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
    print('audio_trim_segments_no=' + str(len(segs)) +'\n')
    print('audio_trim_segments_speech_no=' + str(int(stats[0])) +'\n')
    print('audio_trim_segments_speech_ms=' + str(int(stats[1]) * 1000) +'\n')
    print('audio_trim_segments_notspeech_no=' + str(int(stats[2])) +'\n')
    print('audio_trim_segments_notspeech_ms=' + str(int(stats[3]) * 1000) +'\n')
    print("audio_trim_exec_time=%s\n" % round((time.time() - start_time), 3))
    '''
    #print(stats)
    #print(str(len(output_arr)) +'\n')
    

    f = open(outputTextFile, 'w')
    #f.write('audio_trim_file=' + inputWavFile +'\n')
    #f.write('audio_trim_out_file=' + outputTextFile +'\n')
    f.write('audio_trim_duration=' + str(audio_trim_duration) +'\n')
    f.write('audio_trim_segments=' + str(';'.join(str(e) for e in output_arr)) +'\n')
    f.write('audio_trim_segments_no=' + str(len(segs)) +'\n')
    f.write('audio_trim_segments_speech_no=' + str(int(stats[0])) +'\n')
    f.write('audio_trim_segments_speech_ms=' + str(int(stats[1]) * 1000) +'\n')
    f.write('audio_trim_segments_notspeech_no=' + str(int(stats[2])) +'\n')
    f.write('audio_trim_segments_notspeech_ms=' + str(int(stats[3]) * 1000) +'\n')
    f.write("audio_trim_exec_time=%s\n" % round((time.time() - start_time), 3))
    f.close()

'''
else:
    usage()
    sys.exit(os.EX_USAGE)
'''
sys.exit(os.EX_OK) # code 0, all ok
