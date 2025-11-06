# from fastapi import APIRouter, WebSocket, File, UploadFile

# import numpy as np
# from fastapi.responses import JSONResponse
# from app.models.whisper import pipe
# import torch

# transcript_router = APIRouter()
# #Load Whisper model
# device = "cuda" if torch.cuda.is_available() else "cpu"

# @transcript_router.post("/audio_transcript")
# async def transcribe_audio(language: str, file: UploadFile = File(...)):
#     # Read the uploaded audio file
#     audio_data = await file.read()
#     if language == "english":
#         result = pipe(audio_data, generate_kwargs={"language": language})
#     else:
#         result = pipe(audio_data, generate_kwargs={"language": language})
#     print(result["text"])

#     #Return the transcript as JSON response
#     return JSONResponse(content={"transcript": result["text"]})
