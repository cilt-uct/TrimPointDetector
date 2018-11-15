# TrimPointDetector
Algorithm that utilises pyAudioAnalysis to detect the start and end trim points for Opencast recorded lectures.

# Dependencies
pyAudioAnalysis (https://github.com/tyiannak/pyAudioAnalysis)

# Example
Usage:

```
python detectTrimpoints.py /path/to/audio-file.wav
```

Result:
```
{'start':'0','end':'3318000'}
```

### In a OpenCast Workflow
Usage:
```
python detectTrimPoints_woh.py -i /path/to/audio-file.wav -o /path/to/autput-file.txt -non-speech 90
```

![Screenshot](screenshot.png)

```
usage: detectTrimPoints_woh.py [-h] [--version] -i wav -o txt
                               [--start-speech seconds)]
                               [--end-speech (seconds)]
                               [--non-speech (seconds)]
                               [--start-adjust (seconds)]
                               [--end-adjust (seconds)]
                               [--start-buffer (seconds)]
                               [--end-buffer (seconds)]
                               [--good-start (seconds)] [--good-end (seconds]

Audio Trim point detector

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --venue               The venue of this recording used for venue specific models
  -i wav, --input wav   The wav file to detect trimpoints from
  -o txt, --output txt  The file to write the properties in
  --start-speech (seconds)
                        Threshold for speech at the start of the recording
                        [sec] (default: 3, >=)
  --end-speech (seconds)
                        Threshold value for speech at the end of the recording
                        [sec] (default: 5, >=)
  --non-speech (seconds)
                        Threshold value for non-speech segments [sec]
                        (default: 90 >=)
  --start-adjust (seconds)
                        Adjust the first speech segment start time by a number
                        of seconds [sec] (default: -20)
  --end-adjust (seconds)
                        Adjust the last speech segments end time by a number
                        of seconds [sec] (default: 30)
  --start-buffer (seconds)
                        If the start of the segment list is 0 then use this
                        buffer [sec] (default: 3)
  --end-buffer (seconds)
                        If the last segment ends at the end of the wav file
                        adjust by this buffer [sec] (default: 1)
  --good-start (seconds)
                        Does the first segment start within this number of
                        seconds, if true then good start [sec] (default: 300 =
                        5min)
  --good-end (seconds)  Does the last segment end within this number of
                        seconds, if true then good end [sec] (default: 600 =
                        10min)
```

Result:
```
audio_trim_duration=3300000
audio_trim_autotrim=false
audio_trim_ishour=true
audio_trim_good_start=true
audio_trim_good_end=true
audio_trim_detected=24-3089-3252-3254
audio_trim_segments=4000-3089000;3252000-3284000;
audio_trim_segments_len=218
audio_trim_segments_speech=109
audio_trim_segments_speech_ms=2423000
audio_trim_segments_notspeech=1
audio_trim_segments_notspeech_ms=163000
audio_trim_segments_notspeech_used=108
audio_trim_segments_notspeech_used_ms=2405000
audio_trim_threshold=3:5;90
audio_trim_adjust=-20:30
audio_trim_buffer=3:1
audio_trim_good=300:600
audio_trim_model=model_svmNoLapelSpeechModel
audio_trim_lapel=false
audio_trim_exec_time=67.93;138.718
```

| Field | Description | Type |
| ----- | ----------- | ---- |
| audio_trim_duration | duration of the wav file in ms | int |
| audio_trim_autotrim | should this recording be autotrimmed | bool |
| audio_trim_ishour | is th recording roughly an hour long | bool |
| audio_trim_good_start | is the first segment within 5min of the start of the recording | bool |
| audio_trim_good_end | is the end of the last segment withing 10min of the duration of the recording | bool |
| audio_trim_detected | Speech segment start, non-speech times and ends with last speech segment, delimited by - | array |
| audio_trim_segments | segment array, delimited by ; | array |
| audio_trim_segments_len | number of all segments | int |
| audio_trim_segments_speech | number of all speeech segments | int |
| audio_trim_segments_speech_ms | duration of all speech segments in ms | int |
| audio_trim_segments_notspeech | number of all non speech segments | int |
| audio_trim_segments_notspeech_ms | duration of all non speech segments in ms | int |
| audio_trim_segments_notspeech_used | number of used non speech segments | int |
| audio_trim_segments_notspeech_used_ms | duration of all used non speech segments in ms | int |
| audio_trim_threshold | speech threshold start : end ; non speech threshold | array |
| audio_trim_adjust | adjust start and end time, delimited by :  | array |
| audio_trim_buffer | trim buffer start and end time, delimited by : | array |
| audio_trim_good | good start and end time, delimited by : | array |
| audio_trim_model | the name of the model that was used when detecting speech | string |
| audio_trim_lapel | was a lapel mic detected | float |
| audio_trim_exec_time | execution time in sec | float |
