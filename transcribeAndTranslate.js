const recorder = require('node-record-lpcm16');
const fs = require('fs');
const _ = require('lodash');

async function translation_chunk(response, translator, startTime) {
	let start = startTime;
	let translations = [];
	for (let result of response.results) {
		const translation = await translator.translate(
			result.alternatives[0].transcript
		);
		const resultStartTime =
			start +
			result.alternatives[0].words.reduce(
				(acc, curr) =>
					curr.startTime.nanos < acc ? curr.startTime.nanos : acc,
				0
			);
		const resultEndTime =
			start +
			result.alternatives[0].words.reduce(
				(acc, curr) => (curr.endTime?.nanos > acc ? curr.endTime?.nanos : acc),
				0
			);
		translations.push({
			translation: translation,
			startTime: resultStartTime,
			endTime: resultEndTime,
		});
		start = resultEndTime;
	}
	return translations;
}

async function translation_all({
	client,
	audioData,
	sampleRateHertz,
	inputLanguage,
	translator,
}) {
	let translations = [];
	let startTime = 0;
	for (let audio of audioData) {
		const request = {
			config: {
				encoding: 'FLAC',
				sampleRateHertz,
				languageCode: inputLanguage,
				enableWordTimeOffsets: true,
				enableAutomaticPunctuation: true,
			},
			audio: { content: audio.content },
			model: 'default',
		};
		console.log(`Transcribing...`);
		// Detects speech in the audio file. This creates a recognition job that you
		// can wait for now, or get its result later.
		const [operation] = await client.longRunningRecognize(request);
		// Get a Promise representation of the final result of the job
		const [response] = await operation.promise();
		// Await a bit to prevent google error for too many requests
		console.log(`Translating ${audio.name} at ${startTime} ns`);
		translation = await translation_chunk(response, translator, startTime);
		if (!_.isEmpty(translation)) {
			startTime = _.last(translation).endTime;
			translations.push(translation);
		}
	}
	return _.flatten(translations).map((t, index) => ({ ...t, index }));
}

async function transcribeAndTranslate(inputData) {
	try {
		const translations = await translation_all(inputData);
		const outputFilename = 'translation.json';
		fs.writeFile(
			outputFilename,
			JSON.stringify(translations, null, 2),
			(err) => {
				if (err) throw err;
			}
		);
		console.log(`Translation result saved in ${outputFilename}`);
	} catch (error) {
		console.error(error);
	}
}

module.exports = transcribeAndTranslate;
