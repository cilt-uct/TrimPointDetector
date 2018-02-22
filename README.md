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
                        (default: 120 >=)
  --start-adjust (seconds)
                        Adjust the first speech segment start time by a number
                        of seconds [sec] (default: -15)
  --end-adjust (seconds)
                        Adjust the last speech segments end time by a number
                        of seconds [sec] (default: 20)
  --start-buffer (seconds)
                        If the start of the segment list is 0 then use this
                        buffer [sec] (default: 1)
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
audio_trim_duration=3600050
audio_trim_ishour=true
audio_trim_good_start=true
audio_trim_good_end=true
audio_trim_segments=1000-2697000;3010000-3339000;
audio_trim_segments=304
audio_trim_segments_speech=152
audio_trim_segments_speech_ms=2464000
audio_trim_segments_notspeech=152
audio_trim_segments_notspeech_ms=1136000
audio_trim_segments_notspeech_used=1
audio_trim_segments_notspeech_used_ms=313000
audio_trim_exec_time=80.947
```

| Field | Description | Type |
| ----- | ----------- | ---- |
| audio_trim_duration | duration of the wav file in ms | int |
| audio_trim_ishour | is th recording roughly an hour long | bool |
| audio_trim_good_start | is the first segment within 5min of the start of the recording | bool |
| audio_trim_good_end | is the end of the last segment withing 10min of the duration of the recording | bool |
| audio_trim_segments | segment array, delimited by ; | array |
| audio_trim_segments_no | number of all segments | int |
| audio_trim_segments_speech_no | number of all speeech segments | int |
| audio_trim_segments_speech_ms | duration of all speech segments in ms | int |
| audio_trim_segments_notspeech_no | number of all non speech segments | int |
| audio_trim_segments_notspeech_ms | duration of all non speech segments in ms | int |
| audio_trim_segments_notspeech_used_no | number of used non speech segments | int | 
| audio_trim_segments_notspeech_used_ms | duration of all used non speech segments in ms | int |
| audio_trim_exec_time | execution time in sec | float |
