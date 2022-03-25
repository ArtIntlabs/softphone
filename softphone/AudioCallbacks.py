#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import logging
import numpy as np
import sounddevice as sd
from collections import deque

import time
import torch
from datetime import timedelta

from _sounddevice import ffi as _ffi

logger = logging.getLogger(__name__)


class EchoAudioCB:
    """ Echo phone audio (input -> output).
    """

    def __init__(self, duration_ms=20, sample_rate=48000.0, channel_count=2):
        self.duration_ms = duration_ms
        self.sample_rate = sample_rate
        self.channel_count = channel_count
        self.sample_period_sec = 1.0 / self.sample_rate
        self.samples_per_frame = int((duration_ms / 1000.0) / self.sample_period_sec)
        self.audio_buffer = deque()

    def cb_put_frame(self, frame):  # WRITE
        """ Listen to the audio coming from phone, and write to audio_buffer.
        """
        self.audio_buffer.append(frame)

        # Return an integer; 0 means success, but this does not matter now
        return 0

    def cb_get_frame(self):  # READ
        """ Read from audio_buffer, and send audio to phone speaker.
        """
        if len(self.audio_buffer):
            frame = self.audio_buffer.popleft()
            return frame
        else:
            return None


class SystemAudioCB:
    """ Relay system audio using buffers.
    """

    def __init__(self, duration_ms=20, sample_rate=48000.0, channel_count=2):
        self.duration_ms = duration_ms
        self.sample_rate = sample_rate
        self.channel_count = channel_count
        self.sample_period_sec = 1.0 / self.sample_rate
        self.samples_per_frame = int((duration_ms / 1000.0) / self.sample_period_sec)
        # recording
        self.input_stream = sd.RawInputStream(samplerate=self.sample_rate,
                                              channels=channel_count,
                                              dtype='int16',
                                              blocksize=self.samples_per_frame)
        # play
        self.output_stream = sd.RawOutputStream(samplerate=self.sample_rate,
                                                channels=channel_count,
                                                dtype='int16',
                                                blocksize=self.samples_per_frame)
        self.input_stream.start()
        self.output_stream.start()

    def cb_put_frame(self, frame):  # WRITE
        """ Listen to the audio coming from phone, and write to output_stream.
        """
        self.output_stream.write(frame)

        # Return an integer; 0 means success, but this does not matter now
        return 0

    def cb_get_frame(self):  # READ
        """ Read from input_stream, and send audio to phone speaker.
        """
        ret = self.input_stream.read(self.samples_per_frame)
        raw_samples = bytes(ret[0])
        return raw_samples


class AILAudioCB:
    """Input-Output Stream Callback"""

    def __init__(self, duration_ms=20, sample_rate=48000.0, channel_count=2):
        self.duration_ms = duration_ms
        self.sample_rate = sample_rate
        self.channel_count = channel_count
        self.samples_per_frame = int((duration_ms / 1000.0) * self.sample_rate)

        # self.audio_buffer = deque()
        self.audio_buffer = []

        # play & recording
        self.stream = sd.RawStream(samplerate=self.sample_rate,
                                   channels=channel_count,
                                   dtype='int16',
                                   blocksize=self.samples_per_frame)
        self.stream.start()

        # for VAD
        self.iterator = 0
        self.timer = {'start': time.time()}
        vad_model, vad_utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')

        # self.vad_iterator = vad_utils[3](vad_model)
        get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks = vad_utils
        self.vad_iterator = VADIterator(vad_model)

    def cb_put_frame(self, frame, n_channels=1, vad_seconds=None):  # WRITE
        """ Listen to the audio coming from phone, and write to output_stream."""
        self.audio_buffer.append(frame)  # that frame to vad

        self.iterator += 1

        # '''
        if vad_seconds:
            frame_per_sec = int(vad_seconds / (self.duration_ms / 1000))
            if self.iterator and self.iterator % frame_per_sec == 0:
                self.timer['now'] = time.time()
                buffer = np.array(self.audio_buffer[int(-1 * vad_seconds):])

                np_buffer = np.frombuffer(buffer, np.float32).reshape(n_channels, -1)
                print(128, np_buffer.shape)
                speech_dict = self.vad_iterator(np_buffer)
                print(131, self.iterator, speech_dict)
            self.iterator += 1
        # '''

        # '''
        if vad_seconds:
            frame_per_sec = int(vad_seconds / (self.duration_ms / 1000))
            self.iterator += 1
            if self.iterator % frame_per_sec == 0:
                print(self.iterator)
                self.timer['now'] = time.time()

                sec_audio_buffer = np.array(self.audio_buffer)[-frame_per_sec:]
                sec_audio_buffer = sec_audio_buffer.reshape(n_channels, -1)
                sec_np_buffer = np.frombuffer(sec_audio_buffer, np.float16)

                speech_dict = self.vad_iterator(sec_np_buffer)

                self.find_word = True
                print(self.iterator, speech_dict)
        # '''

        self.stream.write(frame)
        return 0  # Return an integer; 0 means success, but this does not matter now

    def cb_get_frame(self, size=0):  # READ
        """ Read from input_stream, and send audio to phone speaker."""
        ret, _ = self.stream.read(self.samples_per_frame)
        raw_samples = bytes(ret)
        return raw_samples
