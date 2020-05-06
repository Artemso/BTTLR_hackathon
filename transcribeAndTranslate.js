const recorder = require('node-record-lpcm16');
const fs = require('fs');

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
				enableWordTimeOffsets: true,
			},
			audio,
		};
		// Detects speech in the audio file. This creates a recognition job that you
		// can wait for now, or get its result later.
		const [operation] = await client.longRunningRecognize(request);

		// Get a Promise representation of the final result of the job
		const [response] = await operation.promise();
		//Map each transcribed sentence to their translation
		const transcription = async () =>
			Promise.all(
				response.results.map(async (result) => {
					const translation = await translator.translate(
						result.alternatives[0].transcript
					);
					return {
						transcript: result.alternatives[0].transcript,
						//Out of all word timestamps, just find max and min for endTime and startTime
						//So we know beginning of the text part and its end
						startTime: result.alternatives[0].words.reduce(
							(acc, curr) =>
								curr.startTime.nanos < acc ? curr.startTime.nanos : acc,
							0
						),
						endTime: result.alternatives[0].words.reduce(
							(acc, curr) =>
								curr.endTime?.nanos > acc ? curr.endTime?.nanos : acc,
							0
						),
					};
				})
			);
		await transcription().then((result) => {
			const outputFilename = 'translation.json';
			fs.writeFile(outputFilename, JSON.stringify(result, null, 2), (err) => {
				if (err) throw err;
			});
			console.log(`Result saved in ${outputFilename}`);
		});
	} catch (error) {
		console.error(error);
	}
}

module.exports = transcribeAndTranslate;
