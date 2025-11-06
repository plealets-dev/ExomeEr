import os

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech as cloud_speech_types
from google.api_core.client_options import ClientOptions
PROJECT_ID = "an-grit-project"


# def inintiate_google_transcript_client(): D:\Exome\Gritstone.Exome.Genai\app\services\utils\gcp_config.py
#     # Instantiates a client
#     # Instantiates a client
#     # Instantiates a client
#     client = SpeechClient(
#         client_options=ClientOptions(
#             api_endpoint="us-central1-speech.googleapis.com",
#         )
#     )

#     # client = SpeechClient()

#     recognition_config = cloud_speech_types.RecognitionConfig(
#                     auto_decoding_config= cloud_speech_types.AutoDetectDecodingConfig(),
#                     language_codes =["auto"],
#                     model = "chirp_2"
#                     )
#     streaming_config = cloud_speech_types.StreamingRecognitionConfig(
#         config=recognition_config
#     )


#     config_request = cloud_speech_types.StreamingRecognizeRequest(
#         recognizer=f"projects/{PROJECT_ID}/locations/us-central1/recognizers/_",
#         streaming_config=streaming_config,
#     )
#     return client, config_request




chipr_supporting_languages = [ "en-US", "ml-IN", "hi-IN", "ar-EG", "ta-IN", "mr-IN", "es-US", "es-ES", "fr-CA", "fr-FR"]


def inintiate_google_transcript_client(language_codes =["en-US"], model = "latest_long"):
    # Instantiates a client
    print("language_codes[0]", language_codes[0] )
    if language_codes[0] in chipr_supporting_languages:
        print("speech model chirp model using for ", language_codes[0])
        client = SpeechClient(
            client_options=ClientOptions(
                api_endpoint="us-central1-speech.googleapis.com",
            )
        )

        config = cloud_speech_types.RecognitionConfig(
            auto_decoding_config=cloud_speech_types.AutoDetectDecodingConfig(),
            language_codes=language_codes,  # Set language code to targeted to detect language.
            model="chirp_2",
            features=cloud_speech_types.RecognitionFeatures(
            enable_automatic_punctuation=True))

        return client, config

    

    else:
        client = SpeechClient()
        print("language_code", language_codes)
        recognition_config = cloud_speech_types.RecognitionConfig(
                auto_decoding_config= cloud_speech_types.AutoDetectDecodingConfig(),
                language_codes = language_codes,
                model = model,
                features=cloud_speech_types.RecognitionFeatures(
                enable_automatic_punctuation=True),
                        )
    
    
    
        streaming_config = cloud_speech_types.StreamingRecognitionConfig(
            config=recognition_config
        )


        config_request = cloud_speech_types.StreamingRecognizeRequest(
            recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
            streaming_config=streaming_config,
        )

    return client, config_request



def requests(config: cloud_speech_types.RecognitionConfig, audio_requests: list):
    yield config
    yield from audio_requests



