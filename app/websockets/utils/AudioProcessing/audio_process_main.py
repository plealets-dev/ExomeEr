# import numpy as np
# from pydub import AudioSegment
# import torchaudio
# import torchaudio.transforms
# from df.enhance import enhance, init_df
# from pydub import AudioSegment
# import torchaudio
# import torchaudio
# import subprocess
# from app.websockets.utils.AudioProcessing.Utils.audio_cofiguration import initialize_vad, detect_speech, calculate_snr
# from app.websockets.utils.AudioProcessing.volume_increase import check_and_increase_volume
# from app.websockets.utils.AudioProcessing.Utils.save_wave_to_opus import save_waveform_as_opus_in_memory
# from app.websockets.utils.AudioProcessing.Utils.comparing_enhanced_audio_quality import spectral_analysis
# import io
# import torch


#  # Initialize DeepFilterNet model
# model, df_state, _ = init_df()
# print("Enhancing audio using DeepFilterNet...")
# # Perform spectral analysis


# # Initialize VAD model
# vad_model, vad_utils = initialize_vad()

# import pyogg
# import numpy as np

# import av
# import io
# import torchaudio

# import av
# import io
# import torch
# import numpy as np
# import torchaudio.functional as F
# import imageio_ffmpeg as ffmpeg

# def decode_webm_to_tensor(webm_binary_data):
#     # Write the webm data to a temporary input buffer
#     input_buffer = io.BytesIO(webm_binary_data)
#     input_buffer.seek(0)

#     # Set up ffmpeg command to decode WebM to raw PCM audio
#     cmd = [
#         ffmpeg.get_ffmpeg_exe(),
#         '-i', 'pipe:0',
#         '-f', 'wav',
#         '-acodec', 'pcm_s16le',
#         '-ar', '44100',  # Sample rate
#         '-ac', '1',      # Mono audio
#         'pipe:1'
#     ]

#     # Run the command and capture output
#     process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     output, error = process.communicate(input=webm_binary_data)

#     if process.returncode != 0:
#         raise RuntimeError(f"FFmpeg error: {error.decode('utf-8')}")

#     # Load the WAV output into a tensor
#     waveform, sample_rate = torchaudio.load(io.BytesIO(output))

#     return waveform, sample_rate



# # Enhance audio using DeepFilterNet
# def audio_processing_main(opus_biarry_data, snr_threshold=10.0, gain_db=10):
#     # waveform, sample_rate = torchaudio.load(input_file)
    
#     # Use ffmpeg to convert OPUS to WAV and output to stdout
#     # process = subprocess.run(
#     #     ["ffmpeg", "-i", input_file, "-f", "wav", "pipe:1", "-y"],
#     #     stdout=subprocess.PIPE,
#     #     stderr=subprocess.PIPE  # Optional: Collect errors
#     # )
    
#     # if process.returncode != 0:
#     #     raise RuntimeError(f"FFmpeg Error: {process.stderr.decode()}")

#     # # Load the WAV data into a buffer
#     # wav_data = io.BytesIO(process.stdout)

#     # # Load the WAV data using torchaudio
#     # waveform, sample_rate = torchaudio.load(wav_data)

#     waveform, sample_rate = decode_webm_to_tensor(opus_biarry_data)
    
#     response = {}
#     is_volume_increased = False

#     speech_timestamps = detect_speech(vad_model, vad_utils, waveform, sample_rate)
#     print("Checking human speech having or not...")
#     if not speech_timestamps:
#         print("No speech detected in the audio.")

#         response["isChanged"] = False
#         response["MessageToUser"] = "No voice detected in the audio. Please try again."
#         return response

#     print("Speech detected. Proceeding with enhancement...")


#     # Volume Check and Increase

#     volume_increased_wave_form = check_and_increase_volume(waveform)
#     if volume_increased_wave_form is not None and torch.any(volume_increased_wave_form):
#         print("volume increased due to less volume detected")
#         is_volume_increased = True

#     print("trying to calculate snr")
#     # Calculate SNR
#     snr = calculate_snr(waveform, sample_rate)
    
#     # if snr is None or snr > snr_threshold:

#     if not snr or snr > snr_threshold:
#         print("Background noise is low. Skipping enhancement.")
#         if is_volume_increased:
#             response["EnhancedAudioData"] = save_waveform_as_opus_in_memory(volume_increased_wave_form, sample_rate, target_dbfs=-8.0, threshold_dbfs=-20.0)
#             response["isChanged"] = True
#             response["MessageToUser"] = "Increased Volume, Your volume is too low. Please speak louder."
#             return response
        
#         response["isChanged"] = False
#         return response


#     else:
#         print("trying to background remove")
#         if is_volume_increased:
#             enhanced_waveform = enhance(model, df_state, volume_increased_wave_form)
#         else:
#             enhanced_waveform = enhance(model, df_state, waveform)

#         # checking quality lossed or gained after removing background 
#         is_background_removed_worked = spectral_analysis(waveform, enhanced_waveform)
#         if is_background_removed_worked:
#             if is_background_removed_worked and volume_increased_wave_form:
#                 response["MessageToUser"] = "Both volume increased and background noise removed successfully. Please note, this may affect the speed."
#             else:
#                 response["MessageToUser"] = "Background noise removed successfully. Please note, this may affect the speed."

#             print("Background noice detected and removed noice")
#             response["EnhancedAudioData"] = save_waveform_as_opus_in_memory(enhanced_waveform, sample_rate, target_dbfs=-8.0, threshold_dbfs=-20.0)
#             response["isChanged"] = True
#             return response
        
#         elif is_volume_increased:
#             response["MessageToUser"] = "Background noise detected. AI couldn't filter it out. incrased volum becasuse it low. Please reduce the noise or speak louder."
#             response["isChanged"] = True
#             response["EnhancedAudioData"] = save_waveform_as_opus_in_memory(volume_increased_wave_form, sample_rate, target_dbfs=-8.0, threshold_dbfs=-20.0)
#             return response
#         else:
#             response["isChanged"] = False
#             response["MessageToUser"] = "Background noise detected. AI couldn't filter it out. Please reduce the noise or speak louder."
#             return response

