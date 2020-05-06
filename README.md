# Speech To Text


## Before first use
```
git clone git@github.com:Artemso/BTTLR_hackathon.git bttlr_hackathon
cd bttlr_hackathon
cp credentials_example.json credentials.json
# Fill credentials (request from team)
```

### Before running the app

#### MacOS install sox & node
```
brew install sox
# if you don't have node installed, do these
# brew install nvm
# nvm install node
# nvm use node
npm install
```

#### Linux install sox & node
```
# Install sox https://at.projects.genivi.org/wiki/display/PROJ/Installation+of+SoX+on+different+Platforms
# Install NVM https://github.com/nvm-sh/nvm#install--update-script
nvm install node
nvm use node
npm install
```

## Usage
```
# Extract video to audio, (brew install ffmpeg)
ffmpeg -i audio.mp3 audio.flac

# Check sample rate & try it works:
play audio.flac

#Run: node index.js [txtfile: e.g. audio.flac] [sampleRateHerz: e.g. 48000] [inputLanguage: e.g. en-US] [outputLanguage: e.g. fi, cs, en]
./index.js russian.flac 44100 ru-RU fi
```

# Artem is sorry for adding RTVC_CPU (MacOS installation guide written by a monkey):

## Apparently, should only work with Python3.7

The GUI was cut out by a barbarian :D

install required modules (may require some tinkering):
```pip3 install -r requirements.txt```

install pytorch:
```pip3 install torch torchvision```

From google drive you would want to install a pretrained model (trained in english!). Just put the files into the respective folders:
```https://drive.google.com/file/d/1n1sPXvT34yXFLT47QZA6FIRGrwMeSsZc/view```

From now on, you should be good.

## Usage

you would want to run the program like that (some examples should be provided):
```python3 demo_cli.py -vsrc <Voice source> -txt <TEXTFILE in JSON format>```

The program should spit generated speech in wav format.
