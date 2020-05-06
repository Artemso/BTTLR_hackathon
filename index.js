#!/usr/bin/env node

const fs = require('fs');
const speech = require('@google-cloud/speech');
const transcribeAndTranslate = require('./transcribeAndTranslate.js');
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

if (arguments.length > 0) {
	let file;
	let filename = arguments[0];
	let sampleRateHertz = arguments[1];
	try {
		file = fs.readFileSync(filename).toString('base64');
		const audio = {
			content: file,
		};
		const options = {
			client: speechClient,
			audio,
			sampleRateHertz: sampleRateHertz ? parseInt(sampleRateHertz) : 16000,
			inputLanguage: arguments[2] ? arguments[2] : 'en-US',
			translator: new Translator(translateClient),
		};
		if (arguments[3]) options.translator.setOutputLanguage(arguments[3]);
		console.log(
			`Translating ${filename} at ${sampleRateHertz} from ${options.inputLanguage} to ${options.translator.outputLanguage}`
		);
		transcribeAndTranslate(options);
	} catch (error) {
		console.error(`Wrong file given: ${error}`);
	}
}
