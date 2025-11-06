# import torch
# import numpy as np
# from pydub import AudioSegment
# import io

# def normalize_waveform(waveform):
#     max_val = torch.max(torch.abs(waveform))
#     if max_val > 0:
#         waveform = waveform / max_val
#     return waveform


# def save_waveform_as_opus_in_memory(waveform, sample_rate, threshold_dbfs = -8.0, target_dbfs = -20):
#     # Calculate RMS and current dBFS
#     rms = torch.sqrt(torch.mean(waveform**2))
#     current_dbfs = 20 * torch.log10(rms + 1e-10)
    
#     # Apply gain adjustment if necessary
#     if current_dbfs < threshold_dbfs:
#         print(f"Volume is low ({current_dbfs:.2f} dBFS). Increasing to {target_dbfs} dBFS...")
#         gain_db = target_dbfs - current_dbfs
#         gain_factor = 10 ** (gain_db / 20)
#         waveform = waveform * gain_factor
#         waveform = normalize_waveform(waveform)
#     # Convert the waveform tensor to numpy array
#     waveform_np = np.clip(waveform.numpy(), -1.0, 1.0)
#     waveform_np = waveform.numpy()

#     # Ensure waveform is in 16-bit PCM range
#     waveform_int16 = (waveform_np * 32767).astype(np.int16)
    
#     # Create an AudioSegment
#     audio_segment = AudioSegment(
#         waveform_int16.tobytes(),
#         frame_rate=sample_rate,
#         sample_width=2,  # 16-bit PCM
#         channels=1       # Mono
#     )
    
#     # Export the audio as an OPUS file into memory
#     opus_buffer = io.BytesIO()
#     audio_segment.export(opus_buffer, format="opus")
#     opus_buffer.seek(0)  # Reset buffer position to the beginning
#     print("Waveform saved as OPUS file in memory")

#     return opus_buffer.read()

