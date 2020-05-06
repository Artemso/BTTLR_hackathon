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
ffmpeg -i 274_275.mp3 274_275.flac
# Change audio to text (base64)
base64 274_275.flac > 274_275.txt
# ffmpeg -i 274_275.flac -hide_banner, e.g. 24000 Hz

node index.js [txtfile: e.g. 274_275_text.txt] [sampleRateHerz: e.g. 24000] [outputLanguage: e.g. fi, cs, en]
# node index.js 274_275.txt 24000 fi
```
