import re

class Metadata:
	duration = None # the duration of a movie or audio file in seconds.
	frame_count = None # the number of frames in a movie or audio file.
	frame_rate = None # the frame rate of a movie in fps.
	frame_height = None	# the height of the movie in pixels.
	frame_width = None	# the width of the movie in pixels.
	
	format = None # the pixel format of the movie.
	
	bit_rate = None # the bit rate of the video in bits per second.
	audio_sample_rate = None # the audio sample rate of the media file in bits per second.
	
	pixel_format = None	
	video_codec = None # the name of the video codec used to encode this movie as a string.
	audio_codec = None # the name of the audio codec used to encode this movie as a string.
	audio_channels = None # the number of audio channels in this movie as an integer.
	has_audio = None # boolean value indicating whether the movie has an audio stream.
	
	def __repr__(self):
		return str(self.__dict__)


class FFMPEGMetadataParser:
	# Input #0, flv, from 'foo.flv':
	INPUT_PATTERN = re.compile(r'^\s*Input #\d+,.*$')
	
	# Duration: 00:51:31.9, start: 0.000000, bitrate: 348 kb/s
	DURATION_PATTERN = re.compile(r'^\s*Duration: (.*?), start: (.*?), bitrate: (.*)$')
	
	# Stream #0.0: Audio: mp3, 44100 Hz, stereo
	AUDIO_STREAM_PATTERN = re.compile(r'^\s*Stream\s+#\d+\.\d+:\s+Audio(.*)$')
	
	# Stream #0.1: Video: vp6f, yuv420p, 368x288,  0.17 fps(r)
	#VIDEO_STREAM_PATTERN = re.compile(r'^\s*Stream\s+#\d+\.\d+:\s+Video(.*)$')
	
	# Stream #0.0[0x31]: Video: mpeg2video, yuv420p, 1280x720, 80000 kb/s, 59.94 fps(r)
	VIDEO_STREAM_PATTERN = re.compile(r'^\s*Stream\s+#\d+\.\d+.*:\s+Video(.*)$')
	
	def __init__(self, filelike):
		self.filelike = filelike
		self.raw_metadata_lines = []
		self.metadata = None
		
	def parse_duration(self, line):
		print 'parse_duration: %s' % line
		metadata = self.metadata
		duration, start, bitrate = self.DURATION_PATTERN.match(line).groups()
		metadata.duration = duration
		metadata.start = start
		metadata.bitrate = bitrate
	
	def parse_audio_stream(self, line):
		print 'parse_audio_stream: %s' % line
		metadata = self.metadata
		audio_codec, sample_rate = [each.strip() for each in self.AUDIO_STREAM_PATTERN.match(line).groups()[0].split(',')][:2]
		metadata.audio_codec = audio_codec
		metadata.sample_rate = sample_rate
		
	def parse_video_stream(self, line):
		print 'parse_video_stream: %s' % line
		metadata = self.metadata
		video_codec, pixel_format, dimension, bit_rate, frame_rate = [each.strip() for each in self.VIDEO_STREAM_PATTERN.match(line).groups()[0].split(',')]
		metadata.video_codec = video_codec
		metadata.pixel_format = pixel_format
		metadata.dimension = dimension
		if frame_rate:
			metadata.frame_rate = frame_rate.split(' ')[0]  # extract first word
		
	def parse_input(self, line):
		print 'parse_input: %s' % line
		metadata = Metadata()
		metadata.format = line.split(',')[1].strip()
		self.metadata = metadata
	
	def parse_line(self, line):
		match_any = True
		if self.INPUT_PATTERN.match(line):
			self.parse_input(line)
		elif self.DURATION_PATTERN.match(line):
			self.parse_duration(line)
		elif self.AUDIO_STREAM_PATTERN.match(line):
			self.parse_audio_stream(line)
		elif self.VIDEO_STREAM_PATTERN.match(line):
			self.parse_video_stream(line)
		else:
			match_any = False
		if match_any:
			self.raw_metadata_lines.append(line)
	
	def get_metadata(self):
		for line in self.filelike:
			self.parse_line(line.strip())
		return self.metadata


def parse_ffmpeg_metadata(filelike):
	return FFMPEGMetadataParser(filelike).get_metadata()
