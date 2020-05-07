#!/usr/bin/env python3
#Python 3.7
from encoder.params_model import model_embedding_size as speaker_embedding_size
from synthesizer.inference import Synthesizer
from encoder import inference as encoder
from vocoder import inference as vocoder
from pathlib import Path
import numpy as np
import librosa
import torch
import sys
import json
import os

from scipy.io import wavfile

class   Generate_audio():
    def __init__(self, voice_file, json_text):
        self.voice_file = voice_file
        self.json_text = json_text

    def embed_voice(self):
        encoder.load_model("encoder/saved_models/pretrained.pt")
        in_fpath = Path(self.voice_file)

        ## Computing the embedding
        # First, we load the wav using the function that the speaker encoder provides. This is
        # important: there is preprocessing that must be applied.
        # The following two methods are equivalent:
        # - Directly load from the filepath:
        preprocessed_wav = encoder.preprocess_wav(in_fpath)
        # - If the wav is already loaded:
        original_wav, sampling_rate = librosa.load(in_fpath)
        preprocessed_wav = encoder.preprocess_wav(original_wav, sampling_rate)

        # Then we derive the embedding. There are many functions and parameters that the
        # speaker encoder interfaces. These are mostly for in-depth research. You will typically
        # only use this function (with its default parameters):
        embed = encoder.embed_utterance(preprocessed_wav)
        return embed

    def clone_voice(self, embed):
        synthesizer = Synthesizer("synthesizer/saved_models/logs-pretrained/taco_pretrained")
        vocoder.load_model("vocoder/saved_models/pretrained/pretrained.pt")
        with open(self.json_text) as text_json:
            data = json.load(text_json)
            for x in data:
                text = x['translation']
                # The synthesizer works in batch, so you need to put your data in a list or numpy array
                texts = [text]
                embeds = [embed]
                # If you know what the attention layer alignments are, you can retrieve them here by
                # passing return_alignments=True
                specs = synthesizer.synthesize_spectrograms(texts, embeds)
                spec = specs[0]

                ## Generating the waveform
                print("\nSynthesizing the waveform:")
                # Synthesizing the waveform is fairly straightforward. Remember that the longer the
                # spectrogram, the more time-efficient the vocoder.
                generated_wav = vocoder.infer_waveform(spec)

                ## Post-generation
                # There's a bug with sounddevice that makes the audio cut one second earlier, so we
                # pad it.
                generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate), mode="constant")

                # Save it on the disk
                output_dir = '../output'
                try:
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                except:
                    pass
                fpath = "%s/%02d.wav" % (output_dir, x['index'])
                generated_wav *= 32767 / max(0.01, np.max(np.abs(generated_wav)))
                wavfile.write(fpath, synthesizer.sample_rate, generated_wav.astype(np.int16))


voice_file = sys.argv[1]
json_text = sys.argv[2]

new = Generate_audio(voice_file, json_text)
embed = new.embed_voice()
new.clone_voice(embed)
