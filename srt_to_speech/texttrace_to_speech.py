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
	def __init__(self, sid, startTime, endTime, text, lang='en'):
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
		self.create_audio()
	
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

	def create_audio(self):
		'''
		Creates TTS audio to self.audio
		'''
		tmp = TemporaryFile()
		tts = gTTS(self.text, lang=self.lang)
		tts.write_to_fp(tmp)
		tmp.seek(0)
		self.audio = AudioSegment.from_mp3(tmp)
		tmp.close()
	
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

	def read_from_srt(self):
		def read_segment(index):
			sid = int(self.data[index])
			index += 1
			timestamp = self.data[index]
			tmp = timestamp.split()
			startTime = datetime.datetime.strptime(tmp[0], SRT_TIME_FORMAT) - ORG_TIME
			endTime = datetime.datetime.strptime(tmp[2], SRT_TIME_FORMAT) - ORG_TIME
			index += 1
			text = ""
			while index < self.l and self.data[index] != "":
				text += f"{self.data[index]} "
				index += 1
			seg = TTS_Segment(sid, startTime.total_seconds(), endTime.total_seconds(), text, self.lang)
			return seg, index + 1
		self.data = list()
		with open(self.filename) as f:
			for line in f.readlines():
				self.data.append(line.rstrip())
		self.l = len(self.data)
		self.segments = dict()
		i = 0
		while i < self.l:
			ret, i = read_segment(i)
			self.segments[ret.sid] = ret

	def read_from_json(self):
		def read_segment(seg):
			sid = seg['index']
			startTime = seg['startTime'] / 1000000000
			endTime = seg['endTime'] / 1000000000
			text = seg['translation']
			segment = TTS_Segment(sid, startTime, endTime, text, self.lang)
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

	def create_out(self, name):
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
				self.segments[sid].adjust_audio_length(self.segments[sid+1].start)
			result += self.segments[sid].audio
		result.export(f"{name}.mp3", format="mp3")
		l = datetime.timedelta(seconds=result.duration_seconds)
		print()
		print(f"Created {name}.mp3")
		print(f"Final leght {l}")

def usage_exit():
	executable = os.path.basename(__file__)
	sys.exit(f"Usage: ./{executable} <filename> <language>\nfile type - \'srt\' or \'json\' at the moment\nlanguage - one of supported language codes, run ./{executable} --languages for more info")

def supported_langs():
	print(f"Supported Languages")
	for key, val in tts_langs().items():
		print(f"{key} : {val}")
	exit()

def run(filename, lang, ext):
	basename = os.path.basename(filename)
	out = basename.split('.')[0]
	print(f"TTS from {basename}")
	mysub = TextTrace(filename, lang)
	print(f"Creating audio segments")
	if ext == ".srt":
		mysub.read_from_srt()
	elif ext == ".json":
		mysub.read_from_json()
	else:
		sys.exit(f'Unsupported file {basename}')
	print("Creating final audiofile")
	mysub.create_out(f"{out}_audio")
	print("Finished")

if __name__ == "__main__":
	# needs Protection from running in different dir
	if len(sys.argv) == 2 and sys.argv[1] == "--languages":
		supported_langs()
	elif len(sys.argv) == 3:
		if not sys.argv[2] in tts_langs().keys():
			print(f"{sys.argv[2]} is not supported language\n Flag --languages for more information")
			exit()
		ext = os.path.splitext(sys.argv[1])[-1].lower()
		if ext == ".srt" or ext == ".json": 
			run(sys.argv[1], sys.argv[2], ext)
		else:
			usage_exit()
	else:
		usage_exit()