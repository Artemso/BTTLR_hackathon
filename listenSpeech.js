const recorder = require('node-record-lpcm16');

function speechToText({
	client,
	mainLanguage,
	alternativeLanguages,
	textToSpeech,
}) {
	const request = {
		config: {
			encoding: 'LINEAR16',
			sampleRateHertz: 16000,
			languageCode: mainLanguage,
			alternativeLanguageCodes: alternativeLanguages,
		},
		interimResults: false,
	};
	// Create a recognize stream
	const recognizeStream = client
		.streamingRecognize(request)
		.on('error', console.error)
		.on('data', (data) => {
			if (data.results[0] && data.results[0].alternatives[0]) {
				process.stdout.write(
					data.results[0] && data.results[0].alternatives[0]
						? `Transcription: ${data.results[0].alternatives[0].transcript}\n`
						: '\n\nReached transcription time limit, press Ctrl+C\n'
				);
				textToSpeech.translate(data.results[0].alternatives[0].transcript);
			}
		});

	recorder
		.record({
			sampleRateHertz: request.config.sampleRateHertz,
			threshold: 0,
			verbose: false,
			recordProgram: 'rec',
			silence: '10.0',
		})
		.stream()
		.on('error', console.error)
		.pipe(recognizeStream);
	console.log('Listening, press Ctrl+C to stop.');
}

module.exports = speechToText;
