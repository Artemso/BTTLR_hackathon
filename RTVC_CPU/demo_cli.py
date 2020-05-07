from encoder.params_model import model_embedding_size as speaker_embedding_size
from utils.argutils import print_args
from synthesizer.inference import Synthesizer
from encoder import inference as encoder
from vocoder import inference as vocoder
from pathlib import Path
import numpy as np
import librosa
import argparse
import torch
import sys
import json

from pydub import AudioSegment
from pydub.playback import play

from scipy.io import wavfile


    


class   Generate_audio():
    def __init__(self):
        pass
    def get_args(self):
        ## Info & args
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument("-e", "--enc_model_fpath", type=Path, 
                            default="encoder/saved_models/pretrained.pt",
                            help="Path to a saved encoder")
        parser.add_argument("-s", "--syn_model_dir", type=Path, 
                            default="synthesizer/saved_models/logs-pretrained/",
                            help="Directory containing the synthesizer model")
        parser.add_argument("-v", "--voc_model_fpath", type=Path, 
                            default="vocoder/saved_models/pretrained/pretrained.pt",
                            help="Path to a saved vocoder")
        parser.add_argument("--low_mem", action="store_true", help=\
            "If True, the memory used by the synthesizer will be freed after each use. Adds large "
            "overhead but allows to save some GPU memory for lower-end GPUs.")
        args = parser.parse_args()
        return args
    
    def clone_voice(self, args, voice_sample, json_file):
        encoder.load_model(args.enc_model_fpath)
        synthesizer = Synthesizer(args.syn_model_dir.joinpath("taco_pretrained"), low_mem=args.low_mem)
        vocoder.load_model(args.voc_model_fpath)

        num_generated = 0
        in_fpath = Path(voice_sample)

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
        written_files = []
        with open(json_file) as text_json:
            data = json.load(text_json)
            for key in data:
                text = key['translation']
                # The synthesizer works in batch, so you need to put your data in a list or numpy array
                texts = [text]
                embeds = [embed]
                # If you know what the attention layer alignments are, you can retrieve them here by
                # passing return_alignments=True
                specs = synthesizer.synthesize_spectrograms(texts, embeds)
                spec = specs[0]
                print("Created the mel spectrogram")
                
                
                ## Generating the waveform
                print("Synthesizing the waveform:")
                # Synthesizing the waveform is fairly straightforward. Remember that the longer the
                # spectrogram, the more time-efficient the vocoder.
                generated_wav = vocoder.infer_waveform(spec)
                
                
                ## Post-generation
                # There's a bug with sounddevice that makes the audio cut one second earlier, so we
                # pad it.
                generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate), mode="constant")
                    
                # Save it on the disk
                fpath = "%02d.wav" % num_generated
                written_files.append(fpath)
                generated_wav *= 32767 / max(0.01, np.max(np.abs(generated_wav)))
                wavfile.write(fpath, synthesizer.sample_rate, generated_wav.astype(np.int16))
                num_generated += 1
            print('Done!')
            return written_files
        
    def     combine_segments(self, file_list):
        print(file_list)


new = Generate_audio()
args = new.get_args()
written_files = new.clone_voice(args, 'rus2.m4a', 'textfile.json')
new.combine_segments(written_files)