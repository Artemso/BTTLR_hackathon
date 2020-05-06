const fs = require('fs');

const recorder = require('node-record-lpcm16');

// Imports the Google Cloud client library
const speech = require('@google-cloud/speech');

// Creates a client
const client = new speech.SpeechClient({
	credentials: JSON.parse(fs.readFileSync('credentials.json')),
});

const request = {
	config: {
		encoding: 'LINEAR16',
		sampleRateHertz: 16000,
		languageCode: 'fi-FI',
		alternativeLanguageCodes: ['es-ES', 'en-US'],
	},
	interimResults: false, // If you want interim results, set this to true
};

// Create a recognize stream
const recognizeStream = client
	.streamingRecognize(request)
	.on('error', console.error)
	.on('data', (data) =>
		process.stdout.write(
			data.results[0] && data.results[0].alternatives[0]
				? `Transcription: ${data.results[0].alternatives[0].transcript}\n`
				: '\n\nReached transcription time limit, press Ctrl+C\n'
		)
	);

// Start recording and send the microphone input to the Speech API.
// Ensure SoX is installed, see https://www.npmjs.com/package/node-record-lpcm16#dependencies
recorder
	.record({
		sampleRateHertz: sampleRateHertz,
		threshold: 0,

		verbose: false,
		recordProgram: 'rec', // Try also "arecord" or "sox"
		silence: '10.0',
	})
	.stream()
	.on('error', console.error)
	.pipe(recognizeStream);

console.log('Listening, press Ctrl+C to stop.');
