from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup
from io import BytesIO
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

	def create_segment(self, sid):
		if sid in self.segments.keys():
			tts = gTTS(self.segments[sid].text)
			tts.save(f'{sid}.mp3')
			# sound_raw = BytesIO()
			# tts.write_to_fp(sound_raw)
			# sound = AudioSegment.from_raw(sound_raw)
			# play(sound)

	def match_slot(self, seg):
		if not seg+1 in self.segments.keys():
			os.rename(f'{seg}.mp3', f'fin_{seg}.mp3')
			return
		gap = self.segments[seg+1].start - self.segments[seg].start
		l = get_audio_len(f"{seg}.mp3")
		seg_audio = AudioSegment.from_file(f"{seg}.mp3", format="mp3")
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
			os.rename(f'{seg}.mp3', f'fin_{seg}.mp3')
			return
		alt.export(f"fin_{seg}.mp3", format="mp3")

	# def combine_segments(self, first, second):
	# 	gap = self.segments[second].start - self.segments[first].start
	# 	first_lenght = get_audio_len(f"{first}.mp3")
	# 	sound1 = AudioSegment.from_file(f"{first}.mp3", format="mp3")
	# 	sound2 = AudioSegment.from_file(f"{second}.mp3", format="mp3")
	# 	print(f"Segment {first} Length {first_lenght}")
	# 	print(f"Gap {first}-{second} {gap}")
	# 	if first_lenght > gap:
	# 		rate = first_lenght / gap
	# 		print(f"Adjusting segment {first} to speed rate {rate}")
	# 		alt_sound1 = speedup(sound1, playback_speed=rate)
	# 		result = AudioSegment.empty()
	# 		result += alt_sound1 + sound2
	# 		result.export(f"{first}-{second}.mp3", format="mp3")
	# 	else:
	# 		silence = gap - first_lenght
	# 		silence_duration = silence.total_seconds() * 1000
	# 		print(f"Creating silent segment of {silence_duration} milliseconds")
	# 		silence_audio = AudioSegment.silent(duration=silence_duration)
	# 		result = AudioSegment.empty()
	# 		result += sound1 + silence_audio + sound2
	# 		result.export(f"{first}-{second}.mp3", format="mp3")

	def create_out(self, name):
		for sid in self.segments.keys():
			self.create_segment(sid)
		for sid in self.segments.keys():
			self.match_slot(sid)
		result = AudioSegment.empty()
		for sid in self.segments.keys():
			segment = AudioSegment.from_file(f"fin_{sid}.mp3", format="mp3")
			result += segment
		result.export(f"{name}.mp3", format="mp3")
		l = get_audio_len(f"{name}.mp3")
		print(f"Created {name}.mp3")
		print(f"Final leght {l}")

if __name__ == "__main__":
	mysub = SubTitles('sample.srt')
	mysub.setup()
	# print(mysub.segments[270])
	# mysub.play_segment(270)
	print("Creating audiofile")
	mysub.create_out("sample_out")