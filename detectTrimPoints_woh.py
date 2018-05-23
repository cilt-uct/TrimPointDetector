#!/usr/bin/python
''' Detects the start and end trimpoints of an audio file. '''
import sys
import numpy
import sklearn.cluster
import time
import scipy
import os
import ConfigParser
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
import argparse

class Segment(object):

    def __init__(self, start, end, classification):
        self.start = int(start)
        self.end = int(end)
        self.diff = int(end) - int(start)
        self.classification = str(classification)

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1    

parser = argparse.ArgumentParser(description='Audio Trim point detector')
parser.add_argument('--version', action='version', version='Audio Trim point detector build UCT May 14 2018 14:53')

parser.add_argument('--venue', dest='venue', type=str, default='none', 
                    help='The venue of this recording used for venue specific models')

parser.add_argument('-i', '--input', dest='inputWavFile', type=str, required=True, metavar="wav",
                    help='The wav file to detect trimpoints from')
parser.add_argument('-o', '--output', dest='outputTextFile', type=str, required=True, metavar="txt",
                    help='The file to write the properties in')

parser.add_argument('--start-speech', dest='theshold_speech_start', type=int, default=3, metavar="(seconds)",
                    help='Threshold for speech at the start of the recording [sec] (default: 3, >=)') 
parser.add_argument('--end-speech', dest='threshold_speech_end', type=int, default=5, metavar="(seconds)",
                    help='Threshold value for speech at the end of the recording [sec] (default: 5, >=)')

parser.add_argument('--non-speech', dest='threshold', type=int, default=120, metavar="(seconds)",
                    help='Threshold value for non-speech segments [sec] (default: 120 >=)')

parser.add_argument('--start-adjust', dest='adjust_speech_start', type=int, default=-15, metavar="(seconds)",
                    help='Adjust the first speech segment start time by a number of seconds [sec] (default: -15)')
parser.add_argument('--end-adjust', dest='adjust_speech_end', type=int, default=20, metavar="(seconds)",
                    help='Adjust the last speech segments end time by a number of seconds [sec] (default: 20)')

parser.add_argument('--start-buffer', dest='buffer_start', type=int, default=1, metavar="(seconds)",
                    help='If the start of the segment list is 0 then use this buffer [sec] (default: 1)')
parser.add_argument('--end-buffer', dest='buffer_end', type=int, default=1, metavar="(seconds)",
                    help='If the last segment ends at the end of the wav file adjust by this buffer [sec] (default: 1)')

parser.add_argument('--good-start', dest='good_start', type=int, default=300, metavar="(seconds)",
                    help='Does the first segment start within this number of seconds, if true then good start [sec] (default: 300 = 5min)')
parser.add_argument('--good-end', dest='good_end', type=int, default=600, metavar="(seconds)",
                    help='Does the last segment end within this number of seconds, if true then good end [sec] (default: 600 = 10min)')

parser.add_argument('-d', '--debug', action='store_true', help='print debug messages')

args = vars(parser.parse_args())
start_time = time.time()

Config = ConfigParser.ConfigParser()
Config.read("config.ini")

if not os.path.isfile(args['inputWavFile']):
    print "Cannot locate audio file " + str(args['inputWavFile'])

default_modelName = "model/svmModel"
modelName = default_modelName

if args['venue'] in ConfigSectionMap("Venues"):
  modelName = 'model/' + ConfigSectionMap("Venues")[ args['venue'] ]

  if not os.path.isfile(modelName):
    modelName = default_modelName
    if not os.path.isfile(modelName):
        print "Cannot locate model file " + modelName

# get the duration of the wave file
audio_trim_duration = 0
audio_trim_hour = 0
auto_trim = 1 # optimistic - we want to auto_trim

with contextlib.closing(wave.open(args['inputWavFile'],'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)
    audio_trim_duration = int(duration*1000)
    audio_trim_hour = 1 if (int(duration) < 3700) else 0

my_segments = []

if (audio_trim_hour == 1):
    modelType = "svm"
    gtFile = ""
    returnVal = aS.mtFileClassification(args['inputWavFile'], modelName, modelType, False, gtFile)
    flagsInd = returnVal[0]
    classNames = returnVal[1]

    flags = [classNames[int(f)] for f in flagsInd]
    (segs, classes) = aS.flags2segs(flags, 1)

    for s in range(len(segs)):
        sg = segs[s]
        diff = int(sg[1]) - int(sg[0])
        if (args['debug']):
            print str(int(sg[0])*1000) +"-"+ str(int(sg[1])*1000)  +"("+ str(diff)  +") : " + str(classes[s]) + "\n"
        my_segments.append(Segment(int(sg[0]), int(sg[1]), str(classes[s])))

#print(len(my_segments))

# Speech
segments_speech = filter(lambda x: x.classification == "speech", my_segments)
segments_speech.sort(key=lambda x: x.end)

segments_speech_start = filter(lambda x: x.diff >= int(args['theshold_speech_start']), segments_speech)
segments_speech_start.sort(key=lambda x: x.end)

segments_speech_end = filter(lambda x: x.diff >= int(args['threshold_speech_end']), segments_speech)
segments_speech_end.sort(key=lambda x: x.end)

final_list = []
last_speech = int(audio_trim_duration / 1000)
if (len(segments_speech_start) > 1):
    final_list.append(segments_speech_start[0].start + int(args['adjust_speech_start']))
    if (args['debug']): 
        print "|%s|%s|" % (segments_speech_start[0].start, int(args['adjust_speech_start']))
else: 
    final_list.append(int(args['buffer_start']))
    auto_trim = 0 # start is at 0 - bad start

if (len(segments_speech_end) > 1):
    final_list.append(segments_speech_end[-1].end + int(args['adjust_speech_end']))
    last_speech = segments_speech_end[-1].end
    if (args['debug']): 
        print "|%s|%s|" % (segments_speech_end[-1].end, int(args['adjust_speech_end']))
else:
    final_list.append(last_speech - int(args['buffer_end']))
    auto_trim = 0 # end is length of recording - bad end

if (args['debug']):
    print final_list 

if (final_list[0] <= 0):
    final_list[0] = int(args['buffer_start'])
    auto_trim = 0 # start is at 0 - bad start

if (final_list[-1] >= int(audio_trim_duration / 1000)):
    final_list[-1] = int(audio_trim_duration / 1000) - int(args['buffer_end'])
    auto_trim = 0 # end is length of recording - bad end    

#print final_list

# Non-Speech
segments_B = filter(lambda x: x.classification == "non-speech", my_segments)
segments_B.sort(key=lambda x: x.end)

segments_BC = filter(lambda x: (x.diff >= int(args['threshold'])) and (x.start >= final_list[0]) and (x.end < final_list[-1]), segments_B)
segments_BC.sort(key=lambda x: x.end)

stats = {
    'len': len(my_segments),
    'hour': audio_trim_hour, 'duration': audio_trim_duration,
    'speech_no': len(segments_speech), 'speech_ms': sum(c.diff for c in segments_speech), 
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

# first segment is always a x no of seconds from the start...
if (final_list[0] == 0):
    final_list[0] = args['buffer_start']
    stats['good_start'] = 0
    auto_trim = 0 # start is at 0 - bad start
else:
    stats['good_start'] = final_list[0] < args['good_start']

if (final_list[-1] == int(audio_trim_duration / 1000)):
    final_list[-1] = int(audio_trim_duration / 1000) - args['buffer_end']
    stats['good_end'] = 0
    auto_trim = 0 # end is length of recording - bad end  
else:
    stats['good_end'] = final_list[-1] + args['good_end'] > int(audio_trim_duration / 1000) 

final_list = map(lambda x: x * 1000, final_list)

result = ''
d = '-'
for e in final_list:
    result = result + str(e) + d
    if (d == '-'):
        d = ';'
    else:
        d = '-'

if (args['debug']):
    print (stats)
    print ('modelName: ' + modelName)
    print ('audio_trim_autotrim=' + ("true" if ((stats['hour'] == 1) and (stats['nonspeech_used_no'] == 0) and stats['good_start'] and stats['good_end']) else "false") +'\n')
    print(str(';'.join(str(e) for e in final_list)))
    print(result)


f = open(args['outputTextFile'], 'w')
#f.write('audio_trim_file=' + args['inputWavFile'] +'\n')
#f.write('audio_trim_out_file=' + args['outputTextFile'] +'\n')
f.write('audio_trim_duration=' + str(stats['duration']) +'\n')
f.write('audio_trim_autotrim=' + ("true" if ((stats['hour'] == 1) and (stats['nonspeech_used_no'] == 0) and stats['good_start'] and stats['good_end']) else "false") +'\n')
f.write('audio_trim_ishour=' + ("true" if (stats['hour'] == 1) else "false") +'\n')
f.write('audio_trim_good_start=' + ("true" if (stats['good_start']) else "false") +'\n')
f.write('audio_trim_good_end=' + ("true" if (stats['good_end']) else "false") +'\n')
f.write('audio_trim_segments=' + result +'\n')
f.write('audio_trim_segments_len=' + str(int(stats['len'])) +'\n')
f.write('audio_trim_segments_speech=' + str(int(stats['speech_no'])) +'\n')
f.write('audio_trim_segments_speech_ms=' + str(int(stats['speech_ms']) * 1000) +'\n')
f.write('audio_trim_segments_notspeech=' + str(int(stats['nonspeech_no'])) +'\n')
f.write('audio_trim_segments_notspeech_ms=' + str(int(stats['nonspeech_ms']) * 1000) +'\n')
f.write('audio_trim_segments_notspeech_used=' + str(int(stats['nonspeech_used_no'])) +'\n')
f.write('audio_trim_segments_notspeech_used_ms=' + str(int(stats['nonspeech_used_ms']) * 1000) +'\n')
f.write('audio_trim-model=' + modelName.replace("/","_") +'\n')
f.write("audio_trim_exec_time=%s\n" % round((time.time() - start_time), 3))
f.close()

sys.exit(os.EX_OK) # code 0, all ok
