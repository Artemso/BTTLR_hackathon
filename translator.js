class Translator {
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
			return translations.map((translation, i) => translation).join('\n');
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

module.exports = Translator;
