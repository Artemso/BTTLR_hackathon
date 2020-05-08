# [Babel](http://jiricodes.com/babel): Speech To translated Speech

![Tower of Babel](/img/babel.jpeg)

> *The tower of babel is an origin myth explaining why the world's people speak different languages*

Babel uses AI-learning to mimic a foreign speaker’s voice and speech patterns before translating the speaker to your native language.

## About this Project
Babel was created in about 48 hours during [Back to the living room Hackathon](https://backtothelivingroom.tech/). The goal was to create an automated solution for video translation while maitaining the original speaker's voice.

Here's is an example of the result we achieved:
[Original Marketing video in German](https://youtu.be/037nONh0l5M) -> [Babel translation to English (40s)](https://youtu.be/nWnjKjztRTs)

**For more information visit: [Babel's Website](https://jiricodes.com/babel)**
## speech_to_translated_text
A nodeJS app using Google's speech-to-text API translating audio files to translated text json like:
```json
[
  {
    "translation": "marketing mix",
    "startTime": "0.500",
    "endTime": "0.600",
    "index": 0
  },
  {
    "translation": "That sounds happy and colorful, doesn't it?",
    "startTime": "1.100",
    "endTime": "2.500",
    "index": 1
  }
]
```

## text_to_speech
An AI driven software using tensorflow to synthesize voice based on input voice reading above json text.

## sow_speech
A final script merging the read sentence files together using silent padding and tempo adjustments in order to comply with original timestamps.

## Tie it all together with run.sh
1. Extract voice data from the video using `ffmpeg`
2. Split the voice data based on silence & size with `sox`
3. Run `speech_to_translated_text` for the audio files to generate `translation.json`
4. Read original sound data & `translation.json` with `text_to_speech` to output translated speech files
5. Sow those files together with `sow_speech` to one audio file
6. Replace video's audio with the new audio using `ffmpeg`


## Prerequisites before running
Clone repo
```
git clone git@github.com:Artemso/BTTLR_hackathon.git bttlr_hackathon
cd bttlr_hackathon
```

Fill credentials by creating your own google cloud service account and [downloading credentials](https://console.cloud.google.com/apis/credentials)

Then:

```
cp credentials_example.json credentials.json
# fill the credentials to credentials.json
```

Install needed software
```
brew install sox
brew install ffmpeg
# if you don't have node installed, do these
# brew install nvm
# nvm install node
# nvm use node
cd speech_to_translated_text && npm install && cd ..
cd text_to_speech && pip3 install -r requirements.txt && cd ..
pip3 install torch torchvision
pip3 install gTTS
pip3 install pydub
# make sure you have python3.7
```

Download voice models for text to speech from our [shared models](https://drive.google.com/file/d/1n1sPXvT34yXFLT47QZA6FIRGrwMeSsZc/view).

Move those models to their corresponding folders in `text_to_speech`

## Usage

Check samplerate of original file
```
ffmpeg -i FILENAME
```

Run script
```
./run.sh FILENAME SAMPLERATE LANGUAGE_IN LANGUAGE_OUT
# eg. ./run.sh samples/speech.mp4 44100 fr en
```

