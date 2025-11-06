# from deepgram import DeepgramClient, LiveOptions,Deepgram, PrerecordedOptions
# import numpy as np
# import librosa
# from app.creds.config import DEEPGRAM_API_KEY
# import asyncio

# deepgram = DeepgramClient(DEEPGRAM_API_KEY)



# def transcribe_audio_using_Deepgram(deepgram, audio_bytes):
#     """Transcribes audio bytes using Deepgram."""

#     options = PrerecordedOptions(
#             model="nova-2",
#             language="multi",
#             smart_format=True,
#         )

#     source = {"buffer": audio_bytes, "mimetype": "audio/webm; codecs=opus"}

#     response = deepgram.listen.rest.v("1").transcribe_file(source, options)
    
#     # print( response)
#     try:
#         transcript = response.results["channels"][0]["alternatives"][0]["transcript"]
#         print("deepgram response:", transcript)
#         return transcript
#     except (IndexError, KeyError):
#         return "Transcript not found in response."
