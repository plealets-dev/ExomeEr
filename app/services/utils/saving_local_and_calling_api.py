import wave
import datetime
import os 


SAMPLE_RATE = 16000 



def save_audio_to_file(audio_buffer: bytearray):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"merged_audio_{timestamp}.wav"
    directory_name  = "artifacts"
    os.makedirs(directory_name, exist_ok=True)
    local_file_path = f"{directory_name}/{filename}"
    with wave.open(local_file_path, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_buffer)



    return local_file_path

    # Upload to Azure after saving the file
    # upload_to_azure(local_file_path, filename)


    # print(f"Saved audio to {filename}")

    # import requests

    # url = "https://qagenai.exomemed.com/api/audio_transcript"

    # payload = {}
    # files=[
    # ('file',(filename,open(local_file_path,'rb'),'audio/webm'))
    # ]
    # headers = {}

    # response = requests.request("POST", url, headers=headers, data=payload, files=files)

    # print(response.text)