from azure.storage.blob.aio import BlobServiceClient
from dotenv import load_dotenv
import os 
load_dotenv()
from app.creds.config import FileStorageConnectionString, ContainerName

# Initialize BlobServiceClient with your connection string
# connection_string = os.environ.get("FileStorageConnectionString")
# ContainerName = os.environ.get("ContainerName")

# print("connection_string", FileStorageConnectionString)
# print("container_name", ContainerName)

blob_service_client = BlobServiceClient.from_connection_string(FileStorageConnectionString)
container_name = ContainerName
# Function to upload the mp3 audio buffer to Azure Blob Storage



async def upload_to_blob(blob_name: str, audio_buffer):
    """Uploads a binary MP3 file to Azure Blob Storage asynchronously."""
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
  

    try:
        # Upload the file asynchronously
        await blob_client.upload_blob(audio_buffer, blob_type="BlockBlob")
        # audio_buffer.clear()  # Use clear() to reset the buffer without creating a new object
        audio_buffer = None
        print(f"Audio chunk uploaded as {blob_name}")
    except Exception as e:
        print(f"Failed to upload {blob_name}: {str(e)}")
