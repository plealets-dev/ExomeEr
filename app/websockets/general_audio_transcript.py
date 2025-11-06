



from app.services.utils.gcp_config import inintiate_google_transcript_client
from app.services.gcp_transcript import transcribe_streaming_v2
from starlette.websockets import WebSocketState
from collections import defaultdict
from fastapi import APIRouter, WebSocket,WebSocketDisconnect
import uuid
import json
import gzip
from app.services.save_to_blob import upload_to_blob
from app.services.save_to_mongo import upload_transcription_to_mongo
from datetime import datetime
from app.api.utils.audio_file_configuration import save_wav_audio_as_mp3_from_buffer, save_wav_to_artifacts_file, save_mp3_from_buffer
from app.services.gcp_transcript import transcription_with_google_v2
import asyncio
import wave
import struct
import cbor2


general_transcript_router = APIRouter()


# Define the sample rate and minimum duration for transcription (in seconds)
SAMPLE_RATE = 44100  # 44 kHz
MIN_DURATION = 3  # Minimum 5 seconds of audio
CHANNELS = 1
FORMAT=wave.WAVE_FORMAT_PCM





user_audio_buffers_for_general_v2 = defaultdict(bytes) 
active_connections_v2 = {}
last_dialog_of_each_session_v2 = {}
last_spoked_person_v2 = {}
user_audio_buffers_v2 = defaultdict(bytearray) 

@general_transcript_router.websocket("/v2.0/GritAudioTranscript")
async def websocket_audio(websocket: WebSocket):


    language_codes = ["ml-IN"]
    google_transcipt_client, config_request = inintiate_google_transcript_client(language_codes, model = "long")
    
    await websocket.accept()
    # Generate a unique session id (could also use tokens, user ID, etc.)
    session_id = str(uuid.uuid4())
    audio_buffer = user_audio_buffers_for_general_v2[session_id]
    active_connections_v2[session_id] = websocket
    
    
    last_dialog_of_each_session_v2.update({session_id: ""})
    last_spoked_person_v2.update({session_id: ""})

    try:
        while True:


            message = await websocket.receive_bytes()

            # Parse header
            header_length = 8  # 4 bytes for total length, 4 bytes for metadata length
            total_length , metadata_length = struct.unpack("!II", message[:header_length])

            # Extract metadata and audio data
            metadata_bytes = message[header_length:header_length + metadata_length]
            user_audio_buffers_for_general_v2[session_id] = message[header_length + metadata_length:]

            metadata = cbor2.loads(metadata_bytes)
            

            # Example of dynamic handling of metadata
            print("Received Metadata:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")

            print(f"Audio byte length: {len(audio_buffer)}")


            service = metadata.get("Service")
            purpose = metadata.get("Purpose") #eg from where it coming DSR from Ebantis, Twigo for medical conversation
            if service is None and purpose is None:
                await active_connections_v2[session_id].send_text(f"Service and Pursose is getting None")
                user_audio_buffers_for_general_v2[session_id] = None
            else:
                OriginalTranscriptNeeded = metadata.get("OriginalTranscriptNeeded", True)
            
                # onlyTranscriptNeeded = message_data.get("isOnlyTranscriptNeeded", True)

                # LastSpokedPerson = message_data.get("LastSpokedPerson", "Patient")
                SelectedLanguage = metadata.get("SelectedLanguage", ["en"])
                print("SelectedLanguage", SelectedLanguage)

                
                

                    # Calculate duration of the audio in seconds
                duration_seconds = len(user_audio_buffers_for_general_v2[session_id]) / (SAMPLE_RATE * CHANNELS * 2)  # 2 bytes per sample (16-bit)
            

                # Check if the accumulated audio is at least 5 seconds
                if duration_seconds >= MIN_DURATION:
                    print(f"Processing audio of duration: {duration_seconds:.2f} seconds")
                    
                # try:
                    

                # mp3_bianry_io_file = save_wav_audio_as_mp3_from_buffer(audio_buffer, is_wav_file_byte)
                

                # Start time
                # start_time = time.time()
                # if len(SelectedLanguage) >=1:
                # if SelectedLanguage[0] == "en":
                #     language_codes = SelectedLanguage
                #     original_transcribed_text = transcription_with_whisper(user_audio_buffers_for_general_v2[session_id])
                
                #     # since it already transcript result in english 
                #     translated_text = ""
               
                if SelectedLanguage[0] != language_codes[0]:
                    google_transcipt_client, config_request = inintiate_google_transcript_client(SelectedLanguage, model = "latest_long")
                    language_codes = SelectedLanguage

                translated_text,  original_transcribed_text = transcription_with_google_v2(google_transcipt_client,  user_audio_buffers_for_general_v2[session_id], config_request, language_codes)
                    # transcription_result_english = translated_text
            

                # print(transcription_result)# Start time

                # Create a background task to upload the file without blocking the WebSocket
                            # Generate a unique blob name for each chunk (e.g., user ID + timestamp)
                            
                            
            
                # Current datetime
                now = datetime.now()
                # Format datetime into a readable pattern
                # Example: "YYYYMMDDHHMMSSmmm" (YearMonthDayHourMinuteSecondMilliseconds)
                unique_id_with_time = now.strftime("%Y%m%d%H%M%S") + str(int(now.microsecond / 1000)).zfill(3)
                blob_name = f"Twigo/AudioData/{service}/{purpose}/{unique_id_with_time}.mp3"
                if OriginalTranscriptNeeded:
                    transcript = f"{original_transcribed_text} \n {translated_text}"
                else:
                    transcript = f"{translated_text}"

                response_data = {
                        "Service": service,
                        "Transcript": transcript,
                        "AudioDataPath": blob_name
                    }
                await active_connections_v2[session_id].send_text(json.dumps(response_data))
          
                asyncio.create_task(upload_to_blob(blob_name, user_audio_buffers_for_general_v2[session_id]))
                asyncio.create_task(upload_transcription_to_mongo(session_id , unique_id_with_time, blob_name, language_codes,original_transcribed_text, translated_text, service, purpose, isgeneral = True))
                user_audio_buffers_for_general_v2[session_id] = None
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
        del user_audio_buffers_for_general_v2[session_id]
        del active_connections_v2[session_id]
        del last_dialog_of_each_session_v2[session_id]
        del last_spoked_person_v2[session_id]
        print("Client disconnected")
    except Exception as e:
        print(f"Error during audio processing: {e}")
        # Handle disconnection and errors
        if websocket.client_state == WebSocketState.CONNECTED:
            await active_connections_v2[session_id].send_text(f"Error during processing: {e}")
    finally:
        # Ensure WebSocket is closed gracefully
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()

        if session_id in active_connections_v2:
            await active_connections_v2[session_id].close()
            del active_connections_v2[session_id]

