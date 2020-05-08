# Babel: Speech To translated Speech for Videos
## About this Project
Babel, as we call it, has been created over less than 48 hours during [Back to the living room Hackathon](https://backtothelivingroom.tech/). The goal was to created automated solution for video translation while maitaining the original speaker's voice.
Here is how it turned out:
[Original Marketing video in German](https://youtu.be/037nONh0l5M) -> [Babel translation to English (40s)](https://youtu.be/nWnjKjztRTs)

## Prerequisites
```
git clone git@github.com:Artemso/BTTLR_hackathon.git bttlr_hackathon
cd bttlr_hackathon
cp credentials_example.json credentials.json
# Fill credentials (request from team)
# Or create your own by creating a new google service account
brew install sox
brew install ffmpeg
# if you don't have node installed, do these
# brew install nvm
# nvm install node
# nvm use node
cd speech_to_translated_text && npm install && cd ..
cd RTVC_CPY && pip3 install -r requirements.txt && cd ..
pip3 install torch torchvision
# download models from https://drive.google.com/file/d/1n1sPXvT34yXFLT47QZA6FIRGrwMeSsZc/view
# move those `saved_models` in their corresponding folders to RTVC_CPU
pip3 install gTTS
pip3 install pydub
```

## Usage
```
# Check samplerate of original file
ffmpeg -i FILENAME
./run.sh FILENAME SAMPLERATE LANGUAGE_IN LANGUAGE_OUT
# eg. ./run.sh samples/speech.mp4 44100 en fi
```

