from azure.storage.fileshare import ShareFileClient, ShareDirectoryClient
from app.creds.config import FileStorageConnectionString, ContainerName, AUDIO_DIRECTORY
import os


 # Define your directory name

def upload_to_azure(local_path, file_name):
    try:
        # Extract the directory path and file name
        # file_name = os.path.basename(filename)
        
        # Create a ShareDirectoryClient for the target directory
        directory_client = ShareDirectoryClient.from_connection_string(
            conn_str=FileStorageConnectionString,
            share_name=ContainerName,
            directory_path=AUDIO_DIRECTORY
        )

        # Create the directory if it does not exist
        directory_client.create_directory()  # This will not raise an error if the directory already exists

        # Create a file client for the file to be uploaded
        file_client = ShareFileClient.from_connection_string(
            conn_str=ContainerName,
            share_name=ContainerName,
            directory_path=AUDIO_DIRECTORY,
            file_name=file_name
        )

        # Upload the file
        with open(local_path, "rb") as data:
            file_client.upload_file(data)

        print(f"Uploaded {file_name} to Azure File Share in '{AUDIO_DIRECTORY}' directory.")

    except Exception as e:
        print(f"Error uploading to Azure: {e}")

