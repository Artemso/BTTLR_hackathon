#!/usr/bin/env python3
#Python 3.7
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup
from tempfile import TemporaryFile
import datetime
import subprocess
import os

# Constants Definition
SRT_TIME_FORMAT = '%H:%M:%S,%f'

def get_audio_len(filename):
	result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
							"format=duration", "-of",
							"default=noprint_wrappers=1:nokey=1", filename],
							stdout=subprocess.PIPE,
							stderr=subprocess.STDOUT)
	audio_len = datetime.timedelta(seconds=float(result.stdout))
	return audio_len

def adjust_audio_speed(audio, speed=1.0):
	altered_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)})
	return altered_audio.set_frame_rate(audio.frame_rate)

class SubSegment():
	def __init__(self, sid, timestamp, text):
		self.sid = sid
		self.timestamp = timestamp
		self.start = None
		self.end = None
		self.get_start_end()
		self.text = text
	
	def __str__(self):
		return self.text

	def get_start_end(self):
		tmp = self.timestamp.split()
		self.start = datetime.datetime.strptime(tmp[0], SRT_TIME_FORMAT)
		self.end = datetime.datetime.strptime(tmp[2], SRT_TIME_FORMAT)

class SubTitles():
	def __init__(self, filename):
		self.filename = filename
		self.data = None
		self.l = 0
		self.segments = None
		self.segments_audio = None
		self.segments_order = None
	
	def __len__(self):
		if not self.segments:
			return 0
		else:
			return len(self.segments)

	def setup(self):
		def read_segment(index):
			sid = int(self.data[index])
			index += 1
			timestamp = self.data[index]
			index += 1
			text = ""
			while index < self.l and self.data[index] != "":
				text += f"{self.data[index]} "
				index += 1
			seg = SubSegment(sid, timestamp, text)
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
		self.segments_audio = dict()

	def create_segment(self, sid):
		if sid in self.segments.keys():
			tmp = TemporaryFile()
			tts = gTTS(self.segments[sid].text)
			tts.write_to_fp(tmp)
			tmp.seek(0)
			sound = AudioSegment.from_mp3(tmp)
			tmp.close()
			self.segments_audio[sid] = sound

	def match_slot(self, seg):
		if not seg+1 in self.segments.keys():
			return
		gap = self.segments[seg+1].start - self.segments[seg].start
		seg_audio = self.segments_audio[seg]
		l = datetime.timedelta(seconds=seg_audio.duration_seconds)
		if l > gap:
			rate = l / gap
			alt = speedup(seg_audio, playback_speed=rate)
		elif l < gap:
			silence = gap - l
			silence_duration = silence.total_seconds() * 1000
			silence_audio = AudioSegment.silent(duration=silence_duration)
			alt = AudioSegment.empty()
			alt += seg_audio + silence_audio
		else:
			return
		self.segments_audio[seg] = alt

	def create_out(self, name):
		for sid in self.segments.keys():
			self.create_segment(sid)
		for sid in self.segments.keys():
			self.match_slot(sid)
		result = AudioSegment.empty()
		for sid in self.segments.keys():
			result += self.segments_audio[sid]
		result.export(f"{name}.mp3", format="mp3")
		l = datetime.timedelta(result.duration_seconds)
		print(f"Created {name}.mp3")
		print(f"Final leght {l}")

if __name__ == "__main__":
	mysub = SubTitles('sample.srt')
	mysub.setup()
	print("Creating audiofile")
	mysub.create_out("sample_out")