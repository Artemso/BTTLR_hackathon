const recorder = require('node-record-lpcm16');
const fs = require('fs');

async function translation(response, translator) {
	return Promise.all(
		response.results.map(async (result, index) => {
			const translation = await translator.translate(
				result.alternatives[0].transcript
			);
			return {
				index,
				translation: translation,
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
}

async function transcribeAndTranslate({
	client,
	audio,
	sampleRateHertz,
	inputLanguage,
	alternativeLanguages,
	translator,
}) {
	try {
		const request = {
			config: {
				// Using flac, all audio / video files would be transformed
				// with ffmpeg to .flac file
				encoding: 'FLAC',
				sampleRateHertz,
				languageCode: inputLanguage,
				enableWordTimeOffsets: true,
				enableAutomaticPunctuation: true,
			},
			audio,
			model: 'default',
		};
		// Detects speech in the audio file. This creates a recognition job that you
		// can wait for now, or get its result later.
		const [operation] = await client.longRunningRecognize(request);
		// Get a Promise representation of the final result of the job
		const [response] = await operation.promise();
		// Map each transcribed sentence to their translation and write the result
		// into a file
		await translation(response, translator).then((result) => {
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
