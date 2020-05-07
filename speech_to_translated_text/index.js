#!/usr/bin/env node

const fs = require('fs');
const _ = require('lodash');
const speech = require('@google-cloud/speech');
const transcribeAndTranslate = require('./transcribeAndTranslate.js');
const Translator = require('./translator.js');
const { Translate } = require('@google-cloud/translate').v2;

const credentials = JSON.parse(fs.readFileSync('../credentials.json'));
const arguments = process.argv.slice(2);

const translateClient = new Translate({
	credentials,
});
const speechClient = new speech.SpeechClient({
	credentials,
});

function readFiles(filenames) {
	// A little bit complicated sorter :D
	// 'audio/longer_part_001.flac',
	// 'audio/longer_part_002.flac'
	// Sorts by the ints at the end of file
	const files = _.sortBy(filenames.split(','), (file) =>
		parseInt(_.first(_.last(file.split('_')).split('.')))
	).filter((name) => !_.isEmpty(name));
	console.log(files);
	return files.map((file) => ({
		name: file,
		content: fs.readFileSync(file).toString('base64'),
	}));
}

if (arguments.length > 0) {
	let file;
	let filenames = arguments[0];
	let sampleRateHertz = arguments[1];
	try {
		const audioData = readFiles(arguments[0]);
		const options = {
			client: speechClient,
			audioData,
			sampleRateHertz: sampleRateHertz ? parseInt(sampleRateHertz) : 16000,
			inputLanguage: arguments[2] ? arguments[2] : 'en-US',
			translator: new Translator(translateClient),
		};
		if (arguments[3]) options.translator.setOutputLanguage(arguments[3]);
		console.log(
			`Translating above files at ${sampleRateHertz} from ${options.inputLanguage} to ${options.translator.outputLanguage} (might take a while...)`
		);
		transcribeAndTranslate(options);
	} catch (error) {
		console.error(`Wrong file given: ${error}`);
	}
}
