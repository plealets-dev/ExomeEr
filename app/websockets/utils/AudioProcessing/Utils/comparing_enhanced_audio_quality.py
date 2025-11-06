# import torchaudio
# import torchaudio.transforms
# import torch

# def spectral_analysis(original_waveform, enhanced_waveform):
#     original_spectrogram = torchaudio.transforms.Spectrogram()(original_waveform)
#     enhanced_spectrogram = torchaudio.transforms.Spectrogram()(enhanced_waveform)

#     epsilon = 1e-10
#     log_spec_orig = torch.log(original_spectrogram + epsilon)
#     log_spec_enh = torch.log(enhanced_spectrogram + epsilon)

#     spectral_distance = torch.mean(torch.abs(log_spec_orig - log_spec_enh)).item()

#     clarity_threshold = 2.0
#     return spectral_distance <= clarity_threshold