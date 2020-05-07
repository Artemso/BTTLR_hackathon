# SRT-to-speech

Attempt to recreate audio scene using gTTS and subtitles file (.srt)

## textrace-to-speech
### Requirements
- python3
- pydub
- ffmpeg
	- Win: [here](https://www.wikihow.com/Install-FFmpeg-on-Windows)
	- MacOS: brew install ffmpeg
- gTTS

### Usage
Run
```
./texttrace_to_speech.py <filename> <language>
```
supported Languages
```
./texttrace_to_speech.py --languages
```

### Add to run.sh
```
cd srt_to_speech
./combine_speech.py $JSON_FILE ../output/ $OUTPUT_FILE
cp $OUPUT_FILE someplacesafe
cd ..
```