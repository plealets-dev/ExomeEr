from pydub import AudioSegment
from io import BytesIO
from ffmpy import FFmpeg
import tempfile
import os
import subprocess
from io import BytesIO


def decompress_opus_to_mp3(opus_file_path):
    """
    Converts an Opus file to MP3 and returns it as a BytesIO object.
    """
    try:
        # Use subprocess to call FFmpeg
        process = subprocess.Popen(
            [
                "ffmpeg",
                "-i", opus_file_path,  # Input file
                "-f", "mp3",           # Output format
                "-b:a", "64k",         # Bitrate
                "pipe:1"               # Pipe output to stdout
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = process.communicate()

        if process.returncode != 0:
            print(f"FFmpeg error: {error.decode('utf-8')}")
            return None

        # Write the MP3 output to a BytesIO buffer
        mp3_buffer = BytesIO(output)
        mp3_buffer.seek(0)
        return mp3_buffer

    except Exception as e:
        print(f"Error during decompression: {e}")
        return None
