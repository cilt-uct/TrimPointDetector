#!/usr/bin/python
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
import argparse


def get_model_path(wavFile):

    # model used to predict mic model (boundary or lapel)
    mic_model = "model/svmDetectMicTypeModel"
    # lapel speech model
    lapel_model = "model/svmLapelSpeechModel"
    # boundary speech model
    boundary_model = "model/svmNoLapelSpeechModel"
    
    # run the classification model on the audio file
    [Result, P, classNames] = aT.fileClassification(wavFile, mic_model, "svm")
    Result = int(Result)
    
    # if the winner class is boundary_speech return 
    # the path of the boundary speech model, otherwise 
    # return the path of thelapel speech model
    if classNames[Result] == "boundry_speech":
        return boundary_model
    else:
        return lapel_model

# argument handler
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help="path to the audio file")
args = vars(ap.parse_args())
audio_file = args["input"]

# determin speech model for audio file
speech_model = get_model_path(audio_file)

# run predicted speech model to segment audio file
segmentation = aS.mtFileClassification(audio_file, speech_model, "svm", False, gtFile="")