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
    print "Audio Trim point detector build UCT Feb 14 2018 14:41\n"
    print "Usage: detectTrimPoints_woh.py <input audio wave file> <output text file> <use non-speech> <threshold>"

class Segment(object):

    def __init__(self, start, end, classification):
        self.start = int(start)
        self.end = int(end)
        self.diff = int(end) - int(start)
        self.classification = str(classification)

if len(sys.argv) > 1:

    inputWavFile = sys.argv[1]
    outputTextFile = sys.argv[2]

    threshold_speech = int(sys.argv[3]) # 5
    threshold = int(sys.argv[4]) # 1:30

    start_time = time.time()     

    if not os.path.isfile(inputWavFile):
        print "Cannot locate audio file " + inputWavFile

    modelName = "model/svmModel"
    if not os.path.isfile(modelName):
        print "Cannot locate model file " + modelName

    # get the duration of the wave file
    audio_trim_duration = 0
    audio_trim_hour = 0
    with contextlib.closing(wave.open(inputWavFile,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        audio_trim_duration = int(duration*1000)
        audio_trim_hour = 1 if (int(duration) < 3700) else 0
    
    my_segments = []
    
    if (audio_trim_hour == 1):
        modelType = "svm"
        gtFile = ""
        returnVal = aS.mtFileClassification(inputWavFile, modelName, modelType, False, gtFile)
        flagsInd = returnVal[0]
        classNames = returnVal[1]

        flags = [classNames[int(f)] for f in flagsInd]
        (segs, classes) = aS.flags2segs(flags, 1)

        for s in range(len(segs)):
            sg = segs[s]
            #print str(int(sg[0])*1000) +"-"+ str(int(sg[1])*1000)  + " : " + str(classes[s]) + "\n"
            my_segments.append(Segment(int(sg[0]), int(sg[1]), str(classes[s])))

    #print(len(my_segments))

    segments_A = filter(lambda x: x.classification == "speech", my_segments)
    segments_A.sort(key=lambda x: x.end)

    segments_AC = filter(lambda x: x.diff >= threshold_speech, segments_A)
    segments_AC.sort(key=lambda x: x.end)

    final_list = []
    last_speech = int(audio_trim_duration / 1000)
    if len(segments_A) > 2:
        final_list.append(segments_AC[0].start)
        final_list.append(segments_AC[-1].end + 10)
        last_speech = segments_AC[-1].end
    else:
        final_list.append(1)
        final_list.append(last_speech - 1)


    segments_B = filter(lambda x: x.classification == "non-speech", my_segments)
    segments_B.sort(key=lambda x: x.end)

    segments_BC = filter(lambda x: (x.diff >= threshold) and (x.start >= final_list[0]) and (x.end < final_list[-1]), segments_B)
    segments_BC.sort(key=lambda x: x.end)

    stats = {
        'len': len(my_segments),
        'hour': audio_trim_hour, 'duration': audio_trim_duration,
        'speech_no': len(segments_A), 'speech_ms': sum(c.diff for c in segments_A), 
        'nonspeech_no': len(segments_B), 'nonspeech_ms': sum(c.diff for c in segments_B),
        'nonspeech_used_no': len(segments_BC), 'nonspeech_used_ms': sum(c.diff for c in segments_BC)
    }
   
    for c in segments_BC:
        final_list.append(c.start)
        final_list.append(c.end)

    # remove duplicates
    final_list = set(final_list)
    final_list = list(final_list)
    final_list.sort()
    
    # first segment is always a second from the start...
    if (final_list[0] == 0):
        final_list[0] = 1
    
    if (final_list[-1] == int(audio_trim_duration / 1000)):
        final_list[-1] = int(audio_trim_duration / 1000) - 1

    stats['good_start'] = final_list[0] < 300
    stats['good_end'] = final_list[-1] + 600 > int(audio_trim_duration / 1000) 

    final_list = map(lambda x: x * 1000, final_list)

    ''' 
    print (stats)
    print(str(';'.join(str(e) for e in final_list)))
    '''
    
    f = open(outputTextFile, 'w')
    #f.write('audio_trim_file=' + inputWavFile +'\n')
    #f.write('audio_trim_out_file=' + outputTextFile +'\n')
    f.write('audio_trim_duration=' + str(stats['duration']) +'\n')
    f.write('audio_trim_ishour=' + ("true" if (stats['hour'] <= 1) else "false") +'\n')
    f.write('audio_trim_good_start=' + ("true" if (stats['good_start'] <= 1) else "false") +'\n')
    f.write('audio_trim_good_end=' + ("true" if (stats['good_end'] <= 1) else "false") +'\n')
    f.write('audio_trim_segments=' + str(';'.join(str(e) for e in final_list)) +'\n')
    f.write('audio_trim_segments_no=' + str(int(stats['len'])) +'\n')
    f.write('audio_trim_segments_speech_no=' + str(int(stats['speech_no'])) +'\n')
    f.write('audio_trim_segments_speech_ms=' + str(int(stats['speech_ms']) * 1000) +'\n')
    f.write('audio_trim_segments_notspeech_no=' + str(int(stats['nonspeech_no'])) +'\n')
    f.write('audio_trim_segments_notspeech_ms=' + str(int(stats['nonspeech_ms']) * 1000) +'\n')
    f.write('audio_trim_segments_notspeech_used_no=' + str(int(stats['nonspeech_used_no'])) +'\n')
    f.write('audio_trim_segments_notspeech_used_ms=' + str(int(stats['nonspeech_used_ms']) * 1000) +'\n')
    f.write("audio_trim_exec_time=%s\n" % round((time.time() - start_time), 3))
    f.close()
    

else:
    usage()
    sys.exit(os.EX_USAGE)

sys.exit(os.EX_OK) # code 0, all ok


