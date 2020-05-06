const fs = require('fs');
const speech = require('@google-cloud/speech');
const speechToText = require('./speechToText.js');
const TextToSpeech = require('./textToSpeech.js');

const arguments = process.argv.slice(2);
const textToSpeech = new TextToSpeech();
if (arguments[0]) textToSpeech.setOutputLanguage(arguments[0]);

const client = new speech.SpeechClient({
	credentials: JSON.parse(fs.readFileSync('credentials.json')),
});

const speechToTextInputs = {
	client,
	mainLanguage: 'en-US',
	altenrativeLanguages: ['fi-FI', 'en-US'],
	textToSpeech,
};

speechToText(speechToTextInputs);
