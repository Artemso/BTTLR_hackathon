const { Translate } = require('@google-cloud/translate').v2;

class TextToSpeech {
	constructor() {
		this.outputLanguage = 'en-US';
	}

	async translate(transcript) {
		const translator = new Translate();
		let [translations] = await translator.translate(
			transcript,
			this.outputLanguage
		);
		translations = Array.isArray(translations) ? translations : [translations];
		translations.forEach((translation, i) => {
			console.log(
				`${transcript[i]} => (${this.outputLanguage}) ${translation}`
			);
		});
	}

	setOutputLanguage(language) {
		this.outputLanguage = language;
	}
}

module.exports = TextToSpeech;
