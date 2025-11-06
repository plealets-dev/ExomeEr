
from azure.storage.blob import BlobServiceClient
from app.creds.config import MongoConnectionString, DbName, FileStorageConnectionString, ContainerName
import os
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.api.utils.decompress_opus_to_mp3 import decompress_opus_to_mp3
from typing import Generator
from fastapi import APIRouter, HTTPException
connection_string =  FileStorageConnectionString

blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name =  ContainerName


# Function to download audio on demand
def download_audio(blob_path):
    # print("os.path.basename(blob_path)", os.path.basename(blob_path))
    local_file_path = f"app/artifacts/temp_audio/{os.path.basename(blob_path)}"
    if not os.path.exists(local_file_path):
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        with open(local_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
    return local_file_path



get_blob_audio = APIRouter()


@get_blob_audio.get("/v1.0/audiochunk")
def get_blob(blob_path: str, background_tasks: BackgroundTasks):
    local_file_path = download_audio(blob_path)
    
    if not os.path.exists(local_file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    def audio_stream() -> Generator[bytes, None, None]:
        with open(local_file_path, "rb") as audio_file:
            while chunk := audio_file.read(1024 * 64):  # Read in 64 KB chunks
                yield chunk
        # File is automatically closed here after exiting the 'with' block

    # Add the cleanup task to be run in the background after the response is sent
    background_tasks.add_task(os.remove, local_file_path)
    
    return StreamingResponse(audio_stream(), media_type="audio/mpeg")


@get_blob_audio.get("/v2.0/opus/audiochunk")
def get_blob(blob_path: str):
    local_file_path = download_audio(blob_path)
    
    if not os.path.exists(local_file_path):
        return {"error": "File not found"}
    
    def audio_stream():
        try:
            opus_mp3_buffer = decompress_opus_to_mp3(local_file_path)
            yield from opus_mp3_buffer
        finally:
            # Delete the file after streaming
            try:
                os.remove(local_file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
    # try:
    #     os.remove(local_file_path)
    # except:
    #     pass
    return StreamingResponse(audio_stream(), media_type="audio/mpeg")




# Define a generator function to stream the MP3 file
def audio_stream(file_path: str) -> Generator[bytes, None, None]:
    try:
        with open(file_path, "rb") as audio_file:
            while chunk := audio_file.read(1024):  # Read in chunks
                yield chunk
    finally:
        # Remove the file after streaming
        if os.path.exists(file_path):
            os.remove(file_path)

@get_blob_audio.get("/v2.0/audiochunk")
def stream_mp3(blob_path: str):
    
    local_file_path = download_audio(blob_path)
    file_name = blob_path.split("/")[-1]
    if not os.path.exists(local_file_path):
        return {"error": "File not found"}
    
    def audio_stream():
        try:
            with open(local_file_path, "rb") as audio_file:
                yield from audio_file
        finally:
            # Delete the file after streaming
            try:
                os.remove(local_file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
    # Define a generator function to stream the MP3 file
    # file_path = "path_to_your_mp3_file.mp3"  # Replace with your file path
    return StreamingResponse(audio_stream(), media_type="audio/ogg", headers={
    "Content-Disposition": f"attachment; filename={file_name}"})

