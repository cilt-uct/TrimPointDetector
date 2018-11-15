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
import argparse

class Segment(object):

    def __init__(self, start, end, classification):
        self.start = int(start)
        self.end = int(end)
        self.diff = int(end) - int(start)
        self.classification = str(classification)

def get_model_path(wave_file):

    # model used to predict mic model (boundary or lapel)
    mic_model = "model/svmDetectMicTypeModel"
    # lapel speech model
    lapel_model = "model/svmLapelSpeechModel"
    # boundary speech model
    boundary_model = "model/svmNoLapelSpeechModel"

    # run the classification model on the audio file
    [Result, P, classNames] = aT.fileClassification(wave_file, mic_model, "svm")
    Result = int(Result)

    #return boundary_model
    # if the winner class is boundary_speech return
    # the path of the boundary speech model, otherwise
    # return the path of thelapel speech model
    if (classNames[Result] == "boundry_speech"):
        return boundary_model
    else:
        return lapel_model

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            #if dict1[option] == -1:
            #    DebugPrint("skip: %s" % option)
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

parser.add_argument('--non-speech', dest='threshold', type=int, default=90, metavar="(seconds)",
                    help='Threshold value for non-speech segments [sec] (default: 90 >=)')

parser.add_argument('--start-adjust', dest='adjust_speech_start', type=int, default=-20, metavar="(seconds)",
                    help='Adjust the first speech segment start time by a number of seconds [sec] (default: -20)')
parser.add_argument('--end-adjust', dest='adjust_speech_end', type=int, default=30, metavar="(seconds)",
                    help='Adjust the last speech segments end time by a number of seconds [sec] (default: 30)')

parser.add_argument('--start-buffer', dest='buffer_start', type=int, default=3, metavar="(seconds)",
                    help='If the start of the segment list is 0 then use this buffer [sec] (default: 3)')
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

if (args['debug']):
    print('Start processing...')

if not os.path.isfile(args['inputWavFile']):
    print('Cannot locate audio file {}'.format(args['inputWavFile']))

default_modelName = "model/svmNoLapelSpeechModel"
modelName = "model/noModel"

# get the duration of the wave file
duration = 0
audio_trim_duration = 0
audio_trim_hour = 0
auto_trim = 1 # optimistic - we want to auto_trim

with contextlib.closing(wave.open(args['inputWavFile'],'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = int(frames / float(rate))
    audio_trim_duration = int(duration*1000)
    audio_trim_hour = 1 if (int(duration) < 3700) else 0

my_segments = []
model_time = 0
if (audio_trim_hour == 1):

    if (args['debug']):
        print('\tDetecting model...')

    # ONLY do this for recordings that are less than an 60 min
    # so if there is a venue that we have mapped then we are going to use that model
    # else we will use the appropriate mic configuration
    if args['venue'] in ConfigSectionMap("Venues"):
        modelName = 'model/' + ConfigSectionMap("Venues")[ args['venue'] ]

        if not os.path.isfile(modelName):
            modelName = default_modelName
            if not os.path.isfile(modelName):
                print('Cannot locate model file {}'.format(modelName))
    else:
        # detect mic configuration by analyzing input wav file
        modelName = get_model_path(args['inputWavFile'])

    if (args['debug']):
        print ('\tusing: {}'.format(modelName))

    model_time = time.time() - start_time
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
            print('{:>6} - {:>6} ({:>6}) : {}').format(sg[0], sg[1], diff, classes[s])
        my_segments.append(Segment(int(sg[0]), int(sg[1]), str(classes[s])))

if (args['debug']):
    print('found {} segments\n'.format(len(my_segments)))

# Speech and non speech lists
final_list = []
detected_list = []

segments_non_speech = filter(lambda x: (x.diff >= int(args['threshold'])) and (x.classification == "non-speech"), my_segments)
segments_non_speech.sort(key=lambda x: x.end)

segments_speech = filter(lambda x: x.classification == "speech", my_segments)
segments_speech.sort(key=lambda x: x.end)

segments_speech_start = filter(lambda x: (x.start >= int(args['theshold_speech_start'])), segments_speech)
segments_speech_start.sort(key=lambda x: x.end)

segments_speech_end = filter(lambda x: (x.end <= duration - int(args['threshold_speech_end'])), segments_speech)
segments_speech_end.sort(key=lambda x: x.end)

segments_speech_useable = filter(lambda x: (x.start >= int(args['theshold_speech_start'])) and (x.end <= duration - int(args['threshold_speech_end'])), segments_speech)
segments_speech_useable.sort(key=lambda x: x.end)

if (args['debug']):
    print('segments_non_speech')

# default start/end as detected without threshold check
detected_list.append(segments_speech[1].start)
detected_list.append(segments_speech[-1].end)
for c in segments_non_speech:
    if (args['debug']):
        print('{:>6} - {:>6} ({:>6}) : {}').format(c.start, c.end, c.diff, c.classification)
    final_list.append(c.start)
    detected_list.append(c.start)

    tmp_segment = filter(lambda x: x.start == c.end, segments_speech)
    if (len(tmp_segment) > 1):
        #print('\t{:>6} - {:>6} ({:>6}) : {}').format(tmp_segment.start, tmp_segment.end, tmp_segment.diff, tmp_segment.classification)
        print(tmp_segment)

    final_list.append(c.end)
    detected_list.append(c.end)

if (len(segments_speech_start) > 1):
    final_list.append(segments_speech_start[0].start + int(args['adjust_speech_start']))
    if (args['debug']):
        print('\n|{:>6}|{:>6}|{:>6} Start'.format(segments_speech_start[0].start, args['adjust_speech_start'], segments_speech_start[0].start + args['adjust_speech_start']))
else:
    final_list.append(int(args['buffer_start']))
    auto_trim = 0 # start is at 0 - bad start

if (len(segments_speech_end) > 1):
    final_list.append(segments_speech_end[-1].end + int(args['adjust_speech_end']))
    if (args['debug']):
        print('|{:>6}|{:>6}|{:>6} End'.format(segments_speech_end[-1].end, args['adjust_speech_end'], segments_speech_end[-1].start + args['adjust_speech_end']))
else:
    final_list.append(duration)
    auto_trim = 0 # end is length of recording - bad end

# remove duplicates
detected_list = set(detected_list)
detected_list = list(detected_list)
detected_list.sort()

final_list = set(final_list)
final_list = list(final_list)
final_list.sort()

if (final_list[0] <= 0):
    final_list[0] = int(args['buffer_start'])
    auto_trim = 0 # start is at 0 - bad start

if (final_list[-1] > duration):
    final_list[-1] = duration
    auto_trim = 0 # end is length of recording - bad end

if (args['debug']):
    print('\n')
    print(detected_list)
    print(final_list)

stats = {
    'len': len(my_segments),
    'hour': audio_trim_hour, 'duration': audio_trim_duration,
    'speech_no': len(segments_speech), 'speech_ms': sum(c.diff for c in segments_speech),
    'nonspeech_no': len(segments_non_speech), 'nonspeech_ms': sum(c.diff for c in segments_non_speech),
    'nonspeech_used_no': len(segments_speech_useable), 'nonspeech_used_ms': sum(c.diff for c in segments_speech_useable)
}

# first segment is always a x no of seconds from the start...
if (final_list[0] == 0):
    final_list[0] = args['buffer_start']
    stats['good_start'] = 0
    auto_trim = 0 # start is at 0 - bad start
else:
    stats['good_start'] = final_list[0] < args['good_start']

if (final_list[-1] == duration):
    final_list[-1] = duration - args['buffer_end']
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
    print(stats)
    print('modelName: {}'.format(modelName))
    print('audio_trim_autotrim={}'.format("true" if ((stats['hour'] == 1) and (stats['nonspeech_used_no'] == 0) and stats['good_start'] and stats['good_end']) else "false"))
    print(result)

f = open(args['outputTextFile'], 'w')
#f.write('audio_trim_file=' + args['inputWavFile'] +'\n')
#f.write('audio_trim_out_file=' + args['outputTextFile'] +'\n')
f.write('audio_trim_duration={}\n'.format(stats['duration']))
f.write('audio_trim_autotrim={}\n'.format("true" if ((stats['hour'] == 1) and (stats['nonspeech_used_no'] == 0) and stats['good_start'] and stats['good_end']) else "false"))
f.write('audio_trim_ishour={}\n'.format("true" if (stats['hour'] == 1) else "false"))
f.write('audio_trim_good_start={}\n'.format("true" if (stats['good_start']) else "false"))
f.write('audio_trim_good_end={}\n'.format("true" if (stats['good_end']) else "false"))
f.write('audio_trim_detected={}\n'.format('-'.join(str(x) for x in detected_list)))
f.write('audio_trim_segments={}\n'.format(result))
f.write('audio_trim_segments_len={}\n'.format(stats['len']))
f.write('audio_trim_segments_speech={}\n'.format(stats['speech_no']))
f.write('audio_trim_segments_speech_ms={}\n'.format(int(stats['speech_ms']) * 1000))
f.write('audio_trim_segments_notspeech={}\n'.format(stats['nonspeech_no']))
f.write('audio_trim_segments_notspeech_ms={}\n'.format(int(stats['nonspeech_ms']) * 1000))
f.write('audio_trim_segments_notspeech_used={}\n'.format(stats['nonspeech_used_no']))
f.write('audio_trim_segments_notspeech_used_ms={}\n'.format(int(stats['nonspeech_used_ms']) * 1000))
f.write('audio_trim_threshold={}:{};{}\n'.format(args['theshold_speech_start'], args['threshold_speech_end'], args['threshold']))
f.write('audio_trim_adjust={}:{}\n'.format(args['adjust_speech_start'], args['adjust_speech_end']))
f.write('audio_trim_buffer={}:{}\n'.format(args['buffer_start'], args['buffer_end']))
f.write('audio_trim_good={}:{}\n'.format(args['good_start'], args['good_end']))
f.write('audio_trim_model={}\n'.format(modelName.replace("/","_")))
f.write('audio_trim_lapel={}\n'.format("true" if ("NoLapel" not in modelName) else "false"))
f.write('audio_trim_exec_time={};{}\n'.format(round(model_time, 3), round(time.time() - start_time, 3)))
f.close()

sys.exit(os.EX_OK) # code 0, all ok
