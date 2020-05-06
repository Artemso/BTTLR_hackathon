class TextToSpeech {
	constructor(translateClient) {
		this.outputLanguage = 'en';
		this.client = translateClient;
	}

	async translate(transcript) {
		try {
			let [translations] = await this.client.translate(
				transcript,
				this.outputLanguage
			);
			translations = Array.isArray(translations)
				? translations
				: [translations];
			translations.forEach((translation, i) => {
				console.log(`${transcript} => (${this.outputLanguage}) ${translation}`);
			});
		} catch (error) {
			if (error && error.response && error.response.body) {
				console.error(error.response.body);
			}
		}
	}

	setOutputLanguage(language) {
		this.outputLanguage = language;
	}
}

module.exports = TextToSpeech;
