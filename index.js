const fs = require('fs');
const speech = require('@google-cloud/speech');
const speechToText = require('./speechToText.js');
const TextToSpeech = require('./textToSpeech.js');
const { Translate } = require('@google-cloud/translate').v2;

const credentials = JSON.parse(fs.readFileSync('credentials.json'));
const arguments = process.argv.slice(2);

const translateClient = new Translate({
	credentials,
});

const textToSpeech = new TextToSpeech(translateClient);
if (arguments[0]) textToSpeech.setOutputLanguage(arguments[0]);

const speechClient = new speech.SpeechClient({
	credentials,
});

const speechToTextInputs = {
	client: speechClient,
	mainLanguage: 'en-US',
	altenrativeLanguages: ['fi-FI', 'en-US'],
	textToSpeech,
};

speechToText(speechToTextInputs);
