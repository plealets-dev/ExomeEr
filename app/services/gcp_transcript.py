import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app/creds/an-grit-project-8d4fe7639a90.json"


from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech as cloud_speech_types
import soundfile as sf 
from app.services.utils.gcp_config import chipr_supporting_languages

PROJECT_ID = "an-grit-project"

from google.cloud import translate_v2


# Instantiates Translation client
translate_client = translate_v2.Client()





    


def transcription_with_google_v2(google_transcipt_client, mp3_binarry_data, config_request, language_codes):
    
    """Transcribe the saved WAV file using Whisper."""
    try:
 

        trasncrpt_text, original_text = transcribe_streaming_v2(google_transcipt_client, config_request, mp3_binarry_data, language_codes, target_language= "en")
        # Ensure data is in the expected numpy format
        return trasncrpt_text, original_text
      
    except Exception as e:
        print(f"Google Transcription error: {e}")
        return False, f"Google Transcription error: {e}"
    





def requests(config: cloud_speech_types.RecognitionConfig, audio_requests: list):
    yield config
    yield from audio_requests


def transcribe_streaming_v2(
    client,
    config_request, 
    byte_data,
    language_codes: list,
    target_language: str
) -> cloud_speech_types.StreamingRecognizeResponse:
    """Transcribes audio from an audio file stream using Google Cloud Speech-to-Text API."""
    try: 
        if language_codes[0] in chipr_supporting_languages:
            # Reads a file as bytes
            # with open(stream_file, "rb") as f: D:\Exome\Gritstone.Exome.Genai\app\services\gcp_transcript.py
            #     audio_content = f.read()

            # Set the maximum chunk size to 25600 bytes
            request = cloud_speech_types.RecognizeRequest(
                recognizer=f"projects/{PROJECT_ID}/locations/us-central1/recognizers/_",
                config=config_request,
                content=byte_data,
            )

            # Transcribes the audio into text
            response = client.recognize(request=request)
            transcribed_text = ""
            for result in response.results:
                # print(result)
                if float(result.alternatives[0].confidence) > 0.75:
                    transcribed_text += result.alternatives[0].transcript
                else:
                    print("less than 75 accuracy . skipping transcript:", result.alternatives[0].transcript)
  

    

        else:
            # Reads a file as bytes
            # with open(stream_file_path, "rb") as f:
            #     audio_content = f.read()
            # audio_content, _ = sf.read(stream_file_path)

            # Set the maximum chunk size to 25600 bytes
            MAX_CHUNK_SIZE = 25600

            print("len of audio bytes", len(byte_data))

            # Create a generator that yields chunks of audio not larger than MAX_CHUNK_SIZE
            def generate_chunks(byte_data: bytes, chunk_size: int):
                for i in range(0, len(byte_data), chunk_size):
                    yield byte_data[i:i + chunk_size]

            audio_requests = (
                cloud_speech_types.StreamingRecognizeRequest(audio=chunk)
                for chunk in generate_chunks(byte_data, MAX_CHUNK_SIZE)
            )

            # Transcribes the audio into text
            responses_iterator = client.streaming_recognize(
                requests=requests(config_request, audio_requests)
            )


            # responses = []
            # for response in responses_iterator:
            #     responses.append(response)
            #     for result in response.results:
            #         print(f"Transcript: {result.alternatives[0].transcript}")
            transcribed_text = ""
            
            for response in responses_iterator:
                # Check if there are any results
                if response.results:
                    for result in response.results:
                        if result.alternatives:
                            transcribed_text += result.alternatives[0].transcript

            print(f"Transcription: {transcribed_text}")

        print("language_codes", language_codes)
        if len(language_codes) == 1 and language_codes[0] == "en-US":
            return transcribed_text, ""

        print("transcribed_text", transcribed_text)
        if transcribed_text:
            language_shortcode = language_codes[0][:2]
            # Handling Marathi by Giving Hindi
            
            if language_shortcode == "mr":
                language_shortcode == "hi"
            # Translate the transcribed text into the target language (English)
            translation = translate_client.translate(transcribed_text, source_language= language_shortcode, target_language=target_language)

            print(f"Translation: {translation['translatedText']}")

            return translation['translatedText'], transcribed_text
        else:
            return transcribed_text, ""
    
    except Exception as e:
        print("google trasncript got unexpected error", str(e))
        return False, False

