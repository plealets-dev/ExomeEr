#  # Apply gain and normalize
# import torch
# from pydub import AudioSegment
# import numpy as np
# import io
# # Apply gain to waveform
# def apply_gain(waveform, gain_db):
#     gain_factor = 10 ** (gain_db / 20)
#     return waveform * gain_factor



# # Normalize waveform
# def normalize_waveform(waveform):
#     max_val = torch.max(torch.abs(waveform))
#     if max_val > 0:
#         waveform = waveform / max_val
#     return waveform


# # def volume_increasing(enhanced_waveform, sample_rate, gain_db=10):

# #     mp3_io = io.BytesIO()

# #     enhanced_waveform = apply_gain(enhanced_waveform, gain_db)
# #     enhanced_waveform = normalize_waveform(enhanced_waveform)

# #     # Save enhanced audio
# #     refined_numpy = (enhanced_waveform.squeeze().numpy() * 32767).astype(np.int16)
# #     refined_audio = AudioSegment(
# #         refined_numpy.tobytes(), frame_rate=sample_rate, sample_width=2, channels=1
# #     )

# #     # Export the resampled audio to the in-memory buffer as MP3
# #     refined_audio.export(mp3_io, format="mp3")

# #     # Move to the start of the buffer for reading
# #     mp3_io.seek(0)

# #     return mp3_io.read()


# def check_and_increase_volume(waveform, target_dbfs=-8.0, threshold_dbfs=-20.0):
#     try:

#         """Check if the volume is low and increase it to a target level."""
#         rms = torch.sqrt(torch.mean(waveform**2))  # Calculate RMS
#         current_dbfs = 20 * torch.log10(rms + 1e-10)  # Convert RMS to dBFS
        

#         if current_dbfs < threshold_dbfs:
#             try:
#                 print(f"Volume is low ({current_dbfs:.2f} dBFS). Increasing to {target_dbfs} dBFS...")
#                 gain_db = target_dbfs - current_dbfs
#                 print("gain db", gain_db)
#                 gain_factor = 10 ** (gain_db / 20)
#                 print("gain factor", gain_factor)
#                 waveform = waveform * gain_factor
#                 print("modified wave form on volumn increase ")

#                 waveform = normalize_waveform(waveform)
#                 return waveform 
#             except Exception as e:
#                 print("getting error for increase volume", str(e))
        
#         else:
#             print(f"Volume is sufficient ({current_dbfs:.2f} dBFS). No adjustment needed.")
#     except Exception as e:
#         print("getting error on increase volume ", str(e))
#         return None