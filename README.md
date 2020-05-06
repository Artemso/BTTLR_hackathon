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
