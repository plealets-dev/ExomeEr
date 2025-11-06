import os
import io
import numpy as np
import ffmpeg
import torch
import webrtcvad
import noisereduce as nr
from scipy.io import wavfile
from pydub import AudioSegment

SNR_THRESHOLD = 10  # Adjust as needed

def convert_opus_to_wav(opus_bytes):
    """Convert Opus audio bytes to WAV format and validate output."""
    try:
        process = (
            ffmpeg.input('pipe:0')
            .output('pipe:1', format='wav', ar=16000, ac=1)  # Ensure 16kHz, mono
            .run(input=opus_bytes, capture_stdout=True, capture_stderr=True)
        )
        
        wav_bytes = process[0]
        
        # Validate WAV output
        if len(wav_bytes) < 44:  # WAV header is at least 44 bytes
            raise RuntimeError("Invalid WAV output: Too small.")

        return wav_bytes
    except Exception as e:
        raise RuntimeError(f"Error converting Opus to WAV: {e}")
    
    

def convert_wav_to_opus(audio, sample_rate=16000):
    """Convert WAV NumPy array to Opus format (in-memory)."""
    try:
        # Ensure waveform is in 16-bit PCM range
        audio_int16 = np.clip(audio, -1.0, 1.0)  # Clip to [-1,1] range
        audio_int16 = (audio_int16 * 32767).astype(np.int16)  # Convert to int16
        
        # Create an AudioSegment
        audio_segment = AudioSegment(
            audio_int16.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,  # 16-bit PCM
            channels=1        # Mono
        )

        # Export to an in-memory OPUS file
        opus_buffer = io.BytesIO()
        audio_segment.export(opus_buffer, format="opus")
        opus_buffer.seek(0)  # Reset buffer position to start
        
        return opus_buffer.read()  # Return Opus bytes
    except Exception as e:
        raise RuntimeError(f"Error converting WAV to Opus: {e}")
 
    

def calculate_snr(audio, sample_rate):
    """Calculate SNR (Signal-to-Noise Ratio)."""
    try:
        noise_samples = int(sample_rate * 1.0)  # 1s noise
        if len(audio) < noise_samples * 2:
            return None

        noise_segment = audio[:noise_samples]
        signal_segment = audio[noise_samples:]

        noise_power = np.mean(noise_segment ** 2)
        signal_power = np.mean(signal_segment ** 2)

        if noise_power == 0 or signal_power == 0:
            return None

        snr = 10 * np.log10(signal_power / noise_power)
        return snr
    except Exception as e:
        print(f"Error calculating SNR: {e}")
        return None

def apply_webrtc_vad(audio, sample_rate):
    """Apply WebRTC Voice Activity Detection (VAD)."""
    vad = webrtcvad.Vad(3)
    frame_size = int(sample_rate * 0.03)  # 30ms per frame

    denoised_audio = []
    for i in range(0, len(audio), frame_size):
        frame = audio[i:i + frame_size]
        if len(frame) == frame_size and vad.is_speech(frame.tobytes(), sample_rate):
            denoised_audio.extend(frame)

    return np.array(denoised_audio, dtype=np.int16)

def apply_noisereduce(audio, sample_rate):
    """Apply Noisereduce library for noise suppression."""
    audio = np.array(audio, dtype=np.float32)
    reduced_audio = nr.reduce_noise(y=audio, sr=sample_rate)
    return np.array(reduced_audio, dtype=np.int16)


def audio_processing_main(opus_audio_bytes):
    """Main function to process Opus audio for noise reduction."""
    # Convert Opus to WAV
    wav_bytes = convert_opus_to_wav(opus_audio_bytes)

    #  Fix: Read WAV using BytesIO
    wav_io = io.BytesIO(wav_bytes)  
    sample_rate, audio = wavfile.read(wav_io)  # Properly read from BytesIO

    # Compute SNR
    snr = calculate_snr(audio, sample_rate)

    # If SNR is above threshold or can't be calculated, skip enhancement
    if snr is None or snr > SNR_THRESHOLD:
        print(" Background noise is low. Skipping enhancement.")
        return opus_audio_bytes

    print(" Applying noise reduction...")
    audio_vad = apply_webrtc_vad(audio, sample_rate)
    audio_cleaned = apply_noisereduce(audio_vad, sample_rate)

    # Convert cleaned WAV back to Opus
    enhanced_opus_bytes = convert_wav_to_opus(audio_cleaned)

    return enhanced_opus_bytes 


