import wave
import os
import pydub
from pydub import AudioSegment
import io

SAMPLE_RATE = 44100  # 44 kHz
MIN_DURATION = 5  # Minimum 5 seconds of audio
CHANNELS= 1
FORMAT=wave.WAVE_FORMAT_PCM
RATE = 44100




def save_wav_audio_as_mp3_from_buffer(audio_buffer: bytearray, is_wav_file_byte = False):
    """Convert a bytearray audio buffer to MP3 without writing to disk."""
    try:
        # Use an in-memory buffer to store the WAV data
        # Create a BytesIO buffer to store WAV data
        # if not is_wav_file_byte:
        wav_io = io.BytesIO()
        # Save the bytearray as a WAV file in the memory buffer
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(CHANNELS)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(RATE)  # Sample rate
            wf.writeframes(audio_buffer)

        # Move to the start of the buffer for reading
        wav_io.seek(0)

        # Save the WAV file to disk
        # with open(f"{filename.replace('.mp3', '')}_wav.wav", 'wb') as wav_file:
        #     wav_file.write(wav_io.getbuffer())

        # return wav_io.read()
        # Convert the in-memory WAV to an AudioSegment
        audio = AudioSegment.from_wav(wav_io)
        # else:
        #     audio = AudioSegment.from_wav(audio_buffer)
    
        # Resample the audio to 16000 Hz
        audio = audio.set_frame_rate(44100)
        
        # Create an in-memory buffer for the MP3 output
        mp3_io = io.BytesIO()
        # Export the resampled audio to the in-memory buffer as MP3
        audio.export(mp3_io, format="mp3")
        # file_name = "sample_.mp3"
        # audio.export(f"{filename}.mp3", format="mp3")

        mp3_io.seek(0)  # Move to the start of the buffer for reading
        
        # Return the MP3 binary data
        return mp3_io.read()

    finally:
        
        # Manually close the wav_io buffer to free memory
        wav_io.close()


import io
from pydub import AudioSegment

def save_mp3_from_buffer(audio_buffer: bytearray, is_wav_file_byte=False):
    """
    Processes audio directly from a bytearray containing MP3 data,
    resamples it to 44100 Hz, and exports it as MP3 binary data.

    :param audio_buffer: Bytearray containing MP3 audio data.
    :param is_wav_file_byte: Boolean flag to indicate if the buffer is WAV data.
    :return: Tuple (success: bool, result: bytes or error message).
    """
    # Create an in-memory buffer for the MP3 output
    mp3_io = io.BytesIO()
    try:
        # Convert the bytearray to a BytesIO file-like object
        audio_io = io.BytesIO(audio_buffer)

        # Load audio depending on the file format
        audio_format = "wav" if is_wav_file_byte else "mp3"
        audio = AudioSegment.from_file(audio_io, format=audio_format)

        # Resample the audio to 44100 Hz
        audio = audio.set_frame_rate(44100)

        # Export the resampled audio to the in-memory buffer as MP3
        audio.export(mp3_io, format="mp3")

        # Move to the start of the buffer for reading
        mp3_io.seek(0)

        # Return success and the MP3 binary data
        return True, mp3_io.read()

    except Exception as e:
        # Return failure and the error message
        return False, f"Error converting to MP3: {str(e)}"

    finally:
        # Close the in-memory buffer
        mp3_io.close()



import datetime
async def save_wav_to_artifacts_file(audio_buffer):
    
    directory_path = "app/artifacts"
    
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created.")
    # Create a filename with timestamp
    file_pah = f"{directory_path}/{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.wav"

    # Open a .wav file and set parameters
    with wave.open(file_pah, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # Sample width in bytes (2 bytes = 16 bits)
        wf.setframerate(RATE)
        wf.writeframes(audio_buffer)

    print(f"Saved {file_pah}")
    return file_pah
