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
			sampleRateHertz: sampleRateHertz ? sampleRateHertz : 16000,
			mainLanguage: 'en-US',
			alternativeLanguages: ['fi-FI', 'en-US'],
			translator: new Translator(translateClient),
		};
		if (arguments[2]) options.translator.setOutputLanguage(arguments[2]);
		console.log(
			`Translating ${filename} at ${sampleRateHertz} to ${options.translator.outputLanguage}`
		);
		transcribeAndTranslate(options);
	} catch (error) {
		console.error(`Wrong file given: ${error}`);
	}
}
