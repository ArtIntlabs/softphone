#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import wave

import torch
import torchaudio
import numpy as np
from softphone.Softphone import Softphone
import logging

logger = logging.getLogger(__name__)
logging.addLevelName(5, "TRACE")


class AIL_Softphone(Softphone):
    def __init__(self, *args, **kwargs):
        super(AIL_Softphone, self).__init__(*args, **kwargs)
        self.start_listen = 0
        self.end_listen = 0
        self.callback = None
        self.sample_rate = None
        self.samples_per_frame = None

    def create_audio_stream(self, audio_callback):
        self.audio_cb_id = self.lib.create_audio_cb(audio_callback)
        self.audio_cb_slot = self.lib.audio_cb_get_slot(self.audio_cb_id)
        self.callback = audio_callback
        self.sample_rate = self.callback.sample_rate
        self.samples_per_frame = self.callback.samples_per_frame  # for vad
        print(30, 'iterator1 = ', self.callback.iterator)

        print(self.callback.samples_per_frame)
        logger.info(f"Created audio callback.")

    def start_listening(self):
        # print(58, self.media_cfg.__dict__)
        self.start_listen = self.current_call.info().call_time
        return self.start_listen

    def stop_listening(self):
        self.end_listen = self.current_call.info().call_time
        return self.end_listen

    def get_buffer(self, n_channels=1, save=None):
        buffer = np.array(self.callback.audio_buffer)

        self.callback.find_word = False

        buffer = buffer.reshape(n_channels, -1)

        if save and self.callback.find_word:
            with wave.open(f'{save}', 'w') as f:
                f.setnchannels(1)
                f.setsampwidth(4)
                f.setframerate(self.sample_rate)
                f.writeframes(buffer)
            logger.info(f"Save audio to {save}.")
        return buffer

    def get_buffer_t(self, n_channels=1, save=None):
        print(61, 'iterator2 = ', self.callback.iterator)
        buffer = np.array(self.callback.audio_buffer)

        if save:
            np_buffer = np.frombuffer(buffer, np.float32)
            np_buffer = np_buffer.reshape(n_channels, -1)

            t_buffer = torch.from_numpy(np_buffer)

            print(64, t_buffer.shape)
            torchaudio.save(f'{save}', t_buffer, self.sample_rate)


        # print(57, len(self.callback.audio_buffer), buffer.shape)
        #
        # ret, _ = self.callback.stream.read(10 * self.samples_per_frame)
        #
        # buffer = np.array(ret)
        # buffer = buffer.reshape(n_channels, -1)
        # print(64, buffer.shape)
        #
        # if save:
        #     with wave.open(f'{save}', 'w') as f:
        #         f.setnchannels(1)
        #         f.setsampwidth(4)
        #         f.setframerate(self.sample_rate)
        #         f.writeframes(buffer)
        #     logger.info(f"Save audio to {save}.")

        return buffer
