import torch
import torchaudio

import matplotlib.pyplot as plt

audio_path = 'SG.wav'
audio, sr = torchaudio.load(audio_path)
duration = audio.shape[-1] / sr
print(sr, audio.shape)

model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

speech_timestamps = get_speech_timestamps(audio, model, sampling_rate=sr, return_seconds=True, visualize_probs=True)
# plt.show()  # for graph in PyCharm
print(speech_timestamps)

duration_ms = 20  # из настроек AudioCallbacs duration_ms=20
window_size_samples = int((duration_ms / 1000.0) * sr) * 2  # берем 2 окна за 1 стриминговый проход (произвольно)
print(window_size_samples)
vad_iterator = VADIterator(model, sampling_rate=sr, speech_pad_ms=duration_ms)
for i, start in enumerate(range(0, audio.shape[-1], window_size_samples)):  # имитация стримминга
    step = min(start + window_size_samples, audio.shape[-1])
    stream_audio = audio[:, start:step]

    try:
        speech_dict = vad_iterator(stream_audio.squeeze(), return_seconds=True)
        if speech_dict:
            # print(stream_audio.shape)
            print(i, speech_dict)
    except torch.jit.Error as e:
        # print(e)
        pass
