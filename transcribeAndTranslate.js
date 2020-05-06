const recorder = require('node-record-lpcm16');

async function transcribeAndTranslate({
	client,
	audio,
	sampleRateHertz,
	mainLanguage,
	alternativeLanguages,
	translator,
}) {
	const request = {
		config: {
			encoding: 'LINEAR16',
			sampleRateHertz,
			languageCode: mainLanguage,
			alternativeLanguageCodes: alternativeLanguages,
			model: 'video',
		},
		audio,
	};
	const [response] = await client.recognize(request);
	console.log(JSON.stringify(response));
	const transcription = response.results
		.map((result) => result.alternatives[0].transcript)
		.join('\n');
	console.log('Transcription: ', transcription);
	translator.translate(transcription);
}

module.exports = transcribeAndTranslate;
