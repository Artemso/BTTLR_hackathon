#!/usr/bin/env python3
#Python 3.7
from gtts import gTTS
from gtts.lang import tts_langs
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup
from tempfile import TemporaryFile
import datetime
import os
import sys
import json

# Constants Definition
SRT_TIME_FORMAT = '%H:%M:%S,%f'
ORG_TIME = datetime.datetime.strptime("00:00:00,000", SRT_TIME_FORMAT)

class TTS_Segment():
	def __init__(self, sid, startTime, endTime, text, seg_audio, lang='en'):
		'''
		Parametres:
		sid - unique id
		float startTime - start in seconds
		float endTime - end in seconds
		str text - text value
		str land - language of the text
		'''
		self.sid = sid
		self.start = startTime
		self.end = endTime
		self.text = text
		# Should check if lang is in SupportedLangs
		self.lang = lang
		self.audio = None
		self.create_audio(seg_audio)
	
	def __str__(self):
		'''
		Needs .srt formatting
		'''
		st = datetime.timedelta(seconds=self.start)
		et = datetime.timedelta(seconds=self.end)
		s = f"{self.sid}\n{st} --> {et}\n{self.text}"
		return s
	
	def __len__(self):
		if self.audio:
			return self.audio.duration_seconds
		else:
			return 0

	def create_audio(self, filename):
		self.audio = AudioSegment.from_file(filename, format='vaw')
		
	
	def adjust_audio_length(self, next_segment_start=None):
		'''
		Adjusts self.audio length to fit a gap between TTS segments.
		params: next_segment_start - float, seconds
		if next_segment_start=None, audio length is intact
		'''
		if not next_segment_start or not self.audio:
			return
		gap = datetime.timedelta(seconds=(next_segment_start - self.start))
		l = datetime.timedelta(seconds=self.__len__())
		if l > gap:
			rate = l / gap
			alt = speedup(self.audio, playback_speed=rate)
		elif l < gap:
			silence = gap - l
			silence_duration = silence.total_seconds() * 1000
			silence_audio = AudioSegment.silent(duration=silence_duration)
			alt = AudioSegment.empty()
			alt += self.audio + silence_audio
		else:
			return
		self.audio = alt

	def add_silent_infront(self, silent_ms):
		silent_audio = AudioSegment.silent(duration=silent_ms)
		alt = AudioSegment.empty()
		alt += silent_audio + self.audio
		self.audio = alt

class TextTrace():
	def __init__(self, filename, lang='en'):
		self.filename = filename
		self.lang = lang
		self.data = None
		self.l = 0
		self.segments = None

	def __len__(self):
		if not self.segments:
			return 0
		else:
			return len(self.segments)

	def read_from_json(self, audio_dir):
		def read_segment(seg):
			sid = seg['index']
			startTime = float(seg['startTime'])
			endTime = float(seg['endTime'])
			text = seg['translation']
			audio_file = os.path.abspath(os.path.join(audio_dir, f"{sid}.wav"))
			if os.path.isfile(audio_file):
				segment = TTS_Segment(sid, startTime, endTime, text, audio_file, self.lang)
			else:
				sys.exit(f"SID {sid} - Audio file error: {audio_file}")
			# print(segment)
			return segment
		
		with open(self.filename) as f:
			self.data = json.load(f)
		tot_len = len(self.data)
		rate = tot_len // 20
		if rate == 0:
			rate = 1
		cnt = 0
		self.segments = dict()
		for item in self.data:
			cnt += 1
			if cnt == rate:
				print('*', end="")
				cnt = 0
			new = read_segment(item)
			self.segments[new.sid] = new
		print()

	def create_out(self, name, audio_type):
		tot_len = len(self.segments)
		rate = tot_len // 20
		if rate == 0:
			rate = 1
		cnt = 0
		result = AudioSegment.empty()
		for sid in self.segments.keys():
			cnt += 1
			if cnt == rate:
				print('*', end="")
				cnt = 0
			if sid+1 in self.segments.keys():
				if sid == 0 and self.segments[sid].start != 0.0:
					self.segments[sid].add_silent_infront(self.segments[sid].start * 1000)
					self.segments[sid].start = 0.0
				self.segments[sid].adjust_audio_length(self.segments[sid+1].start)
			result += self.segments[sid].audio
		result.export(f"{name}", format=audio_type)
		l = datetime.timedelta(seconds=result.duration_seconds)
		print()
		print(f"Created {name}")
		print(f"Final leght {l}")

def usage_exit():
	executable = os.path.basename(__file__)
	sys.exit(f"Usage: ./{executable} <filename.json> <audio_dir> <output_file>")

def supported_langs():
	print(f"Supported Languages")
	for key, val in tts_langs().items():
		print(f"{key} : {val}")
	exit()

def run(filename, audio_dir, out_name):
	basename = os.path.basename(filename)
	print(f"TTS from {basename}")
	mysub = TextTrace(filename)
	print(f"Creating audio segments")
	mysub.read_from_json(audio_dir)
	print("Creating final audiofile")
	basename = os.path.basename(out_name)
	audio_type = basename.split('.')[1]
	mysub.create_out(out_name, audio_type)
	print("Finished")

if __name__ == "__main__":
	# needs Protection from running in different dir
	if len(sys.argv) == 2 and sys.argv[1] == "--languages":
		supported_langs()
	elif len(sys.argv) == 4:
		run(sys.argv[1], sys.argv[2], sys.argv[3])
	else:
		usage_exit()