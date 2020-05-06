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
ffmpeg -i audio.mp3 -f s16le -c:a pcm_s16le audio.raw
# Change audio to text (base64)
base64 audio.raw > audio.txt
# Check sample rate
# try it works play --channels=1 --bits=16 --rate=48000 --encoding=signed-integer \
--endian=little audio.raw

node index.js [txtfile: e.g. audio.txt] [sampleRateHerz: e.g. 48000] [outputLanguage: e.g. fi, cs, en]
# node index.js audio.txt 48000 fi
```
