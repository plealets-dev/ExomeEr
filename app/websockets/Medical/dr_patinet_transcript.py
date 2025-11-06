from fastapi import APIRouter, WebSocket,WebSocketDisconnect
import numpy as np

import wave
# from app.services.file_upload_azure import upload_to_azure
import os
import tempfile
import soundfile as sf  
from starlette.websockets import WebSocketState
from collections import defaultdict
from app.websockets.utils.LLM.Medical.diagnosis_question import extract_diagnosis_and_next_question
from app.websockets.utils.LLM.Medical.diarize import diarize_transcripted_text
from app.websockets.utils.compare import compare_diagnosis,compare_questions,compare_symptoms
from app.api.utils.audio_file_configuration import save_wav_audio_as_mp3_from_buffer, save_wav_to_artifacts_file, save_mp3_from_buffer
import json
import openai
from app.creds.config import OPENAI_API_KEY
from app.services.utils.gcp_config import inintiate_google_transcript_client
from app.services.gcp_transcript import transcribe_streaming_v2
# from torch.nn.attention import SDPBackend, sdpa_kernel
import asyncio
import time
import uuid
from app.services.save_to_blob import upload_to_blob
from app.services.save_to_mongo import upload_transcription_to_mongo
from datetime import datetime
import struct
import cbor2
from app.services.gcp_transcript import transcription_with_google_v2
from app.websockets.utils.LLM.Medical.signs_symtomps import get_symtoms_
from app.websockets.utils.AudioProcessing.noise_cancellation import audio_processing_main

import os,sys,logging

router = APIRouter()


# Define the sample rate and minimum duration for transcription (in seconds)
SAMPLE_RATE = 44100  # 44 kHz
# MIN_DURATION = 3  # Minimum 5 seconds of audio
MIN_SIZE = 10 # IN KB
CHANNELS = 1
FORMAT=wave.WAVE_FORMAT_PCM




# Global dictionaries for session management
user_audio_buffers_for_v2 = defaultdict(bytes)
active_connections_v2 = {}
session_data = {}

async def initialize_session_data(session_id: str):
    """Initialize session-related data."""
    session_data[session_id] = {
        "previous_symtoms": "",
        "previous_diagnosis": "",
        "previous_questions": "",
        "previous_transcript": "",
        "age": None,
        "gender": "",
        "audio_buffer": b"",
        "last_dialog": "",
        "last_spoked_person": "",
        "ChatSeries" : 1, 
    }

async def cleanup_session(session_id: str):
    """Clean up session-related data."""
    if session_id in session_data:
        del session_data[session_id]
    if session_id in active_connections_v2:
        del active_connections_v2[session_id]
    if session_id in user_audio_buffers_for_v2:
        del user_audio_buffers_for_v2[session_id]

import os,sys,logging



@router.websocket("/v2.0/audio")
async def websocket_audio(websocket: WebSocket):

 
    diagnosis = ""
    questions = ""
    UserId = int()
    previous_diagnosis = ""
    previous_questions = ""
    previous_transcript=""
    age=int()
    gender=""
   

    openai_client = openai.OpenAI(api_key = OPENAI_API_KEY) 
    language_codes = ["ml-IN"]
    google_transcipt_client, config_request = inintiate_google_transcript_client(language_codes, model = "long")
    
    await websocket.accept()
    # Generate a unique session id (could also use tokens, user ID, etc.)
    session_id = str(uuid.uuid4())
    active_connections_v2[session_id] = websocket
    
    await initialize_session_data(session_id)
    # Retrieve session-specific variables
    session = session_data[session_id]

    # initial_message = await websocket.receive_text()

    # try:
    #     user_details = json.loads(initial_message)
    #     print("user_details:",user_details)
    # except json.JSONDecodeError:
    #     await websocket.close(code= 1003)
    #     return
    
    # session["multiLingual"] = user_details.get("multiLingual", False)

    
    # # Start Deepgram transcription if multiLingual is True
    # if session["multiLingual"]:
    #     deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        

    try:
        while True:
            if "ChatSeries" not in session:
                session["ChatSeries"] = 1
            # message = await websocket.receive_text()
            # message_data = json.loads(message)
            unique_chunk_id = str(uuid.uuid4())
            # Extract fields from the received JSON payload
            is_wav_file_byte = False
            # audio_data_bytes = message_data.get("AudioData", None)
            # if audio_data_bytes is None:
            #     is_wav_file_byte = True
            message = await websocket.receive_bytes()

            # Parse header
            header_length = 8  # 4 bytes for total length, 4 bytes for metadata length
            total_length , metadata_length = struct.unpack("!II", message[:header_length])

            # Extract metadata and audio data
            metadata_bytes = message[header_length:header_length + metadata_length]
            current_audio_byte_data = message[header_length + metadata_length:]

            metadata = cbor2.loads(metadata_bytes)
            
            if session["audio_buffer"]:
                # if less than 3 sec audio is came it will store to session audio buffor , next iteration will add with current_audio_byte_data
                current_audio_byte_data = session["audio_buffer"] + current_audio_byte_data



            # Example of dynamic handling of metadata
            # print("Received Metadata:")
            # for key, value in metadata.items():
            #     print(f"{key}: {value}")

            print(f"Audio byte length: {len(current_audio_byte_data)}")

        
            UserId = int(metadata.get("UserId"))
            service = metadata.get("Service")
            purpose = metadata.get("Purpose") #eg from where it coming DSR from Ebantis, Twigo for medical conversation
            if service is None and purpose is None:
                await active_connections_v2[session_id].send_text(f"Service and Pursose is getting None")
                current_audio_byte_data= None
            else:
                OriginalTranscriptNeeded = metadata.get("OriginalTranscriptNeeded", True)
            
                PreviousSymptoms = metadata.get("PreviousSymptoms", "")
                PreviousTranscript = metadata.get("PreviousTranscript", "")
                PreviousQuestions = metadata.get("PreviousQuestions", "")
                PreviousDiagnosis = metadata.get("PreviousDiagnosis", "")
                
                age=metadata.get("Age")
                gender=metadata.get("Gender")
                # ChatSeries = session["ChatSeries"] 
                onlyTranscriptNeeded = metadata.get("isOnlyTranscriptNeeded", True)

                # LastSpokedPerson = message_data.get("LastSpokedPerson", "Patient")
                SelectedLanguage = metadata.get("SelectedLanguage", ["en-US"])
                print("SelectedLanguage", SelectedLanguage)

                
                    # Append incoming audio data to the buffer
            # audio_buffer.extend(audio_bytes)

            # Calculate duration of the audio in seconds
            # duration_seconds = len(current_audio_byte_data) / (SAMPLE_RATE * CHANNELS * 2)  # 2 bytes per sample (16-bit)
            # print("duration_seconds", duration_seconds)
            # bitrate_kbps = 128
            size_in_kb = len(current_audio_byte_data) / 1024
            print(f"Size in Kb: {size_in_kb}")

            #     # Check if the accumulated audio is at least 5 seconds
            if size_in_kb >= MIN_SIZE:
                
                # making session audio buffor to empty
                if session["audio_buffer"]:
                    session["audio_buffer"] = b""
        

                # # Check if the accumulated audio is at least 5 seconds
                # if duration_seconds >= MIN_DURATION:
                # print(f"Processing audio of duration: {duration_seconds:.2f} seconds")
                #TODO need to handle the duration 
                try:
                    

                    # mp3_bianry_io_file = save_wav_audio_as_mp3_from_buffer(audio_buffer, is_wav_file_byte)
                    

                    # Start time
                    start_time = time.time()
                    # audio_process_response = audio_processing_main(current_audio_byte_data)
                    # audio_is_changed = audio_process_response.get("isChanged", False)
                    # enhanced_audio_byte_data = audio_process_response.get("EnhancedAudioData", b"")
                    # message_to_user = audio_process_response.get("MessageToUser", "")

                    # # if len(SelectedLanguage) >=1:
                    # if SelectedLanguage[0] == "en":
                    #     language_codes = SelectedLanguage
                    #     original_transcribed_text = transcription_with_whisper(current_audio_byte_data)
                    #     transcription_result_english = original_transcribed_text
                    #     # since it already transcript result in english 
                    #     translated_text = ""
                    # else:
                    # if audio_is_changed:
                    #     audio_byte_data = enhanced_audio_byte_data
                    # else:
                    audio_byte_data = audio_processing_main(current_audio_byte_data)

                    if audio_byte_data == current_audio_byte_data:
                        print("No enhancement applied.")
                    else:
                        print("Enhanced audio processed.")

                
                    # if message_to_user:
                    #     response_data = {
                    #             "UniqueChatId": unique_chunk_id,
                    #             "UserId": UserId,
                    #             "UserMessage": message_to_user}
                    #     print("sending audio error message to user", response_data)
                    #     await active_connections_v2[session_id].send_text(json.dumps(response_data))

                    
                    # if session["multiLingual"]:
                    #     transcription_result_english = transcribe_audio_using_Deepgram(deepgram, current_audio_byte_data)
                    #     original_transcribed_text = transcription_result_english
                

                    if SelectedLanguage[0] != language_codes[0]:
                        google_transcipt_client, config_request = inintiate_google_transcript_client(SelectedLanguage, model = "latest_long")
                        language_codes = SelectedLanguage

                    translated_text,  original_transcribed_text = transcription_with_google_v2(google_transcipt_client,  audio_byte_data, config_request, language_codes)
                    transcription_result_english = translated_text
                    
                    if transcription_result_english:

                        # else:
                        #     transcription_result = transcription_with_whisper(mp3_bianry_io_file)

                        # print(transcription_result)# Start time
                        # print("Current Chat Series", ChatSeries)
                        # print("Last Spoked Person", last_spoked_person[session_id])
                        if transcription_result_english:
                            
                            # TODO temp removing question mark to aviod confusion 
                            
                            latest_diarized_text_list, last_dialogue = diarize_transcripted_text(openai_client,transcription_result_english, session["last_dialog"], SelectedLanguage[0], OriginalTranscriptNeeded = True)
                            if isinstance(latest_diarized_text_list[0], dict):
                                current_speaker = latest_diarized_text_list[0].get("speaker", "")
                                previous_speaker = session['last_spoked_person']
                                
                                # if last spoked person and from the current first spoked person if patient we are assuming he is continueing 
                                if current_speaker ==  previous_speaker:
                                    print("assuming it is a continue series of exchange as before because it is the same person continuing")
                                    
                                elif previous_speaker == "Patient" and current_speaker == "Doctor":
                                    print("Doctor asked a question, Patient answered. Incrementing ChatSeries.")
                                    session["ChatSeries"] += 1


                                # keep last dialog person for giving previos dialoge to understand llm to better diarizing 
                                session["last_dialog"] = last_dialogue
                                session["last_spoked_person"] = latest_diarized_text_list[-1].get('speaker', '')

                    
                            # Current datetime
                            now = datetime.now()
                            # Format datetime into a readable pattern
                            # Example: "YYYYMMDDHHMMSSmmm" (YearMonthDayHourMinuteSecondMilliseconds)
                            unique_id_with_time = now.strftime("%Y%m%d%H%M%S") + str(int(now.microsecond / 1000)).zfill(3)
                            original_audio_blob_path = f"Twigo/AudioData/{UserId}/{unique_id_with_time}.opus"
                            enhanced_blob_name = f"Twigo/EnhancedAudioData/{UserId}/{unique_id_with_time}.opus"
                            # if audio_is_changed:
                            #     blob_path  = enhanced_blob_name
                            # else:
                            blob_path = original_audio_blob_path

                            response_data = {
                                    "UniqueChatId": unique_chunk_id,
                                    "UserId": UserId,
                                    "ChatSeries": session["ChatSeries"],
                                    "Transcript": latest_diarized_text_list,
                                    "AudioDataPath": blob_path
                                }
                        
                            await active_connections_v2[session_id].send_text(json.dumps(response_data))
                            # Append new entries to result
                            new_entries = "\n".join(f"{entry['speaker']}: {entry['text']}" for entry in latest_diarized_text_list)
                            # updating previous transcript with current transcripted
                            session["previous_transcript"] = f"{session['previous_transcript']}\n {new_entries}" if session["previous_transcript"] else new_entries
                            # print("previous transcript", session["previous_transcript"])
                            #End time
                            end_time = time.time()
                            # Calculate the time taken
                            time_taken = end_time - start_time
                            print(f"Time taken for the transcript and diarization : {time_taken} seconds")

                            ######################################### Get Symtoms #####################################################################
                            #Detect diagnosis
                        
                            current_symptoms = get_symtoms_(openai_client, new_entries)
                            if current_symptoms:
                                if isinstance(current_symptoms, list):
                                    current_symptoms = ",".join(current_symptoms)
                                # print("current symtopms", current_symptoms)
                                # print("session['previous_symtoms']", session['previous_symtoms'])
                                # checking having duplicate symptoms or not
                                if not session["previous_symtoms"]:
                                    session["previous_symtoms"] = PreviousSymptoms

                                final_symtopms = compare_symptoms(current_symptoms, session["previous_symtoms"])
                                
                                print("final symtopms", final_symtopms)
                                response_data = {
                                        "UniqueChatId": unique_chunk_id,
                                        "UserId": UserId,
                                        "ChatSeries": session["ChatSeries"],
                                        "Symptoms": final_symtopms,
                                        "AudioDataPath": blob_path
                                    }
                                await active_connections_v2[session_id].send_text(json.dumps(response_data))
                                session["previous_symtoms"] = f"{session['previous_symtoms']}, {final_symtopms}" if session["previous_symtoms"] else final_symtopms

                                #Start time
                                start_time = time.time()

                                if not session["previous_diagnosis"]:
                                    session["previous_diagnosis"] = PreviousDiagnosis

                                if not session["previous_questions"]:
                                    session["previous_questions"] = PreviousQuestions

                                if not session["previous_transcript"]:
                                    session["previous_transcript"] = PreviousTranscript
                                
                                
                                diagnosis_question = extract_diagnosis_and_next_question(openai_client, session["previous_transcript"] , age, gender)
                                
                                current_diagnosis = diagnosis_question.get('Diagnosis', "")
                                current_questions= diagnosis_question.get('Next Question', "")

                                # Compare current and previous diagnosis, questions, and symptoms
                                diagnosis = compare_diagnosis(current_diagnosis, session["previous_diagnosis"])
                                questions = compare_questions(current_questions, session["previous_questions"])
                                

                                # print("session['previous_diagnosis']", session["previous_diagnosis"])
                                # print("session['previous_questions']", session["previous_questions"])

                                # print("current diagnosis", current_diagnosis)
                                # print("current_questions", current_questions)
                                # print("final diagnosis", diagnosis)
                                # print("final questions", questions)

                                response_data = {
                                        "UniqueChatId": unique_chunk_id,
                                        "UserId": UserId,
                                        "ChatSeries": session["ChatSeries"],
                                        "Diagnosis": diagnosis,  
                                        "Questions": questions ,
                                        "AudioDataPath": blob_path
                                    }
                                
                                # print("response data", response_data)

                                # compressed_data = gzip.compress(json.dumps(response_data).encode('utf-8'))

                                    # Send the JSON response back to the client
                                await active_connections_v2[session_id].send_text(json.dumps(response_data))

                                session["previous_diagnosis"] = f"{session['previous_diagnosis']}\n{diagnosis}" if session["previous_diagnosis"] else diagnosis
                                session["previous_questions"] = f"{session['previous_questions']}\n{questions}" if session["previous_questions"] else questions
                            
                            
                            # # End time
                            # end_time = time.time()
                            # # Calculate the time taken
                            # time_taken = end_time - start_time
                            # print(f"Time taken for the remainings: {time_taken} seconds")
                        

                            
                            
                            
                        
                            
                            # Create a background task to upload the file without blocking the WebSocket
                            # Generate a unique blob name for each chunk (e.g., user ID + timestamp)
                            # print("session............................", session)
                            asyncio.create_task(upload_to_blob(original_audio_blob_path, current_audio_byte_data))
                            # if audio_is_changed:
                            #     asyncio.create_task(upload_to_blob(enhanced_blob_name, enhanced_audio_byte_data))
                            
                            asyncio.create_task(upload_transcription_to_mongo(UserId, unique_id_with_time, original_audio_blob_path, enhanced_blob_name, language_codes,original_transcribed_text, translated_text, service, purpose,  latest_diarized_text_list, isgeneral= False, isAudioEnhanced = False, enhancedDetails  = ""))
                            current_audio_byte_data = None  # Allow Python's garbage collector to clean up
                    else:
                        # Current datetime
                        now = datetime.now()
                        # Format datetime into a readable pattern
                        # Example: "YYYYMMDDHHMMSSmmm" (YearMonthDayHourMinuteSecondMilliseconds)
                        unique_id_with_time = now.strftime("%Y%m%d%H%M%S") + str(int(now.microsecond / 1000)).zfill(3)
                        blob_name = f"Twigo/AudioData/{UserId}/{unique_id_with_time}.opus"
                        enhanced_blob_name = f"Twigo/EnhancedAudioData/{UserId}/{unique_id_with_time}.opus"

                        asyncio.create_task(upload_to_blob(blob_name, current_audio_byte_data))
                        # if audio_is_changed:
                        #     asyncio.create_task(upload_to_blob(enhanced_blob_name, enhanced_audio_byte_data))
                        original_transcribed_text = ""
                        translated_text = ""
                        latest_diarized_text_list = ""
                        asyncio.create_task(upload_transcription_to_mongo(UserId, unique_id_with_time, blob_name, enhanced_blob_name, language_codes, original_transcribed_text, translated_text, service, purpose,  latest_diarized_text_list, ErrorLog= True, isAudioEnhanced = False))
                        await websocket.send_text(json.dumps({"error": f"Error: unable to process the audio: chunk size {size_in_kb}", "AudioBlob": blob_name}))

                except Exception as e:
                    print(f"Error during audio processing: {e}")
                    await websocket.send_text(json.dumps({"error": f"Error: {e}"}))
                    current_audio_byte_data = None  # Reset the buffer on error
            
            else:
                # If less than the minimum duration, you can log or handle in a different way
                print(f"Audio size {size_in_kb:.2f} size is less than the minimum required {MIN_SIZE} in Kb.")
                session["audio_buffer"] += current_audio_byte_data

    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
        await cleanup_session(session_id)
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
            await cleanup_session(session_id)




