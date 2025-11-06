# import numpy as np
# from scipy.signal import butter, lfilter
# import torchaudio
# import torchaudio.transforms
# import torch
# from silero_vad import get_speech_timestamps
# import torchaudio
# import io
# import torchaudio
# import subprocess
# import soundfile as sf

# # Initialize Silero VAD
# def initialize_vad():
#     device = torch.device("cpu")
#     vad_model = torch.hub.load(
#         repo_or_dir="snakers4/silero-vad",
#         model="silero_vad",
#         force_reload=False
#     )
#     vad_model = vad_model[0].to(device)
#     utils = {
#         'get_speech_timestamps': get_speech_timestamps,
#     }
#     return vad_model, utils

# # Bandpass filter for noise reduction
# def bandpass_filter(waveform, sr, lowcut=150, highcut=6000):
#     nyquist = 0.5 * sr
#     low = lowcut / nyquist
#     high = highcut / nyquist
#     b, a = butter(6, [low, high], btype='band')
#     filtered_waveform = lfilter(b, a, waveform.numpy(), axis=-1)
#     return torch.tensor(filtered_waveform, dtype=torch.float32)

# # Calculate SNR
# def calculate_snr(waveform, sr, noise_duration=1.0, min_speech_duration=2.0):
#     try: 
#         noise_samples = int(sr * noise_duration)
#         min_speech_samples = int(sr * min_speech_duration)

#         if waveform.size(-1) < noise_samples + min_speech_samples:
#             return None

#         noise_segment = waveform[..., :noise_samples]
#         signal_segment = waveform[..., noise_samples:]

#         noise_power = torch.mean(noise_segment ** 2).item()
#         signal_power = torch.mean(signal_segment ** 2).item()

#         if noise_power == 0 or signal_power == 0:
#             return None

#         snr = 10 * np.log10(signal_power / noise_power)
#         return snr
    
#     except Exception as e:
#         print("getting error on calculating snr", str(e))

# # Perform spectral analysis
# def spectral_analysis(original_waveform, enhanced_waveform, sr):
#     original_spectrogram = torchaudio.transforms.Spectrogram()(original_waveform)
#     enhanced_spectrogram = torchaudio.transforms.Spectrogram()(enhanced_waveform)

#     epsilon = 1e-10
#     log_spec_orig = torch.log(original_spectrogram + epsilon)
#     log_spec_enh = torch.log(enhanced_spectrogram + epsilon)

#     spectral_distance = torch.mean(torch.abs(log_spec_orig - log_spec_enh)).item()

#     clarity_threshold = 2.0
#     return spectral_distance, spectral_distance <= clarity_threshold


# # Detect speech using Silero VAD
# def detect_speech(vad_model, vad_utils, waveform, sample_rate, threshold=0.8, min_duration=0.3, min_energy=1e-4):
#     vad_sample_rate = 16000
#     if sample_rate != vad_sample_rate:
#         resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=vad_sample_rate)
#         waveform = resampler(waveform)

#     speech_timestamps = vad_utils['get_speech_timestamps'](
#         waveform, vad_model, sampling_rate=vad_sample_rate, threshold=threshold
#     )

#     min_samples = int(min_duration * vad_sample_rate)
#     speech_timestamps = [
#         ts for ts in speech_timestamps if (ts['end'] - ts['start']) >= min_samples
#     ]

#     filtered_timestamps = []
#     for ts in speech_timestamps:
#         segment = waveform[:, ts['start']:ts['end']]
#         energy = torch.mean(segment ** 2).item()
#         if energy >= min_energy:
#             filtered_timestamps.append(ts)

#     return filtered_timestamps



# def load_opus_directly(opus_file):
#     # Run ffmpeg to decode the Opus file into WAV format
#     process = subprocess.run(
#         ["ffmpeg", "-i", opus_file, "-f", "wav", "pipe:1", "-y"],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.DEVNULL
#     )
    
#     # Use soundfile to load audio directly from the byte stream
#     audio_stream = io.BytesIO(process.stdout)
#     waveform, sample_rate = sf.read(audio_stream, dtype='float32')
#     return waveform, sample_rate
