const fs = require('fs');
const speech = require('@google-cloud/speech');
const listenSpeech = require('./listenSpeech.js');
const Translator = require('./translator.js');
const { Translate } = require('@google-cloud/translate').v2;

const credentials = JSON.parse(fs.readFileSync('credentials.json'));
const arguments = process.argv.slice(2);

const translateClient = new Translate({
	credentials,
});
const speechClient = new speech.SpeechClient({
	credentials,
});

const options = {
	client: speechClient,
	mainLanguage: 'en-US',
	altenrativeLanguages: ['fi-FI', 'en-US'],
	textToSpeech: new Translator(translateClient),
};

if (arguments[0]) options.textToSpeech.setOutputLanguage(arguments[0]);

listenSpeech(options);
