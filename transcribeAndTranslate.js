const recorder = require('node-record-lpcm16');

async function transcribeAndTranslate({
	client,
	audio,
	sampleRateHertz,
	mainLanguage,
	alternativeLanguages,
	translator,
}) {
	try {
		const request = {
			config: {
				encoding: 'FLAC',
				sampleRateHertz,
				languageCode: mainLanguage,
				alternativeLanguageCodes: alternativeLanguages,
			},
			audio,
		};
		// Detects speech in the audio file. This creates a recognition job that you
		// can wait for now, or get its result later.
		const [operation] = await client.longRunningRecognize(request);

		// Get a Promise representation of the final result of the job
		const [response] = await operation.promise();
		const transcription = response.results
			.map((result) => result.alternatives[0].transcript)
			.join('\n');
		console.log(`Transcription: ${transcription}`);

		await translator.translate(transcription);
	} catch (error) {
		console.error(error);
	}
}

module.exports = transcribeAndTranslate;
