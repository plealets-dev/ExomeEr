import openai
import json
from dotenv import load_dotenv
import os 
from app.creds.config import OPENAI_MODELForSpeakerDiarization, OPENAI_API_KEY
load_dotenv()
from app.services.gcp_transcript import translate_client
import logging

# from datetime import datetime



# # Set up logging configuration
# log_filename = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
# os.makedirs("logs", exist_ok=True)
# logging.basicConfig(filename=log_filename, level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')


def diarize_transcripted_text(client, CurrentTranscript: str, PreviousDialog: str, target_language, OriginalTranscriptNeeded):
  

    print("current transcript :", CurrentTranscript)
    print("previous dialoge :", PreviousDialog)
    
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # model_name =os.getenv("OPENAI_MODEL")
    model_name = OPENAI_MODELForSpeakerDiarization
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    """
    Use the OpenAI API to extract symptoms from the transcription text and suggest a follow-up question.
    """
    prompt = f"""
    As the conversation streams in, identify the speaker for each segment of text in real-time. Label each segment as either "Doctor" or "Patient" strictly based on the tone and content of the provided text, considering both the Current Transcript and the Previous Dialog.

    Instruction:

        
        1. Split Mixed Transcripts: If the Current Transcript includes content that appears to come from both the doctor and the patient, break it into smaller, logical segments based on punctuation, tone shifts, or changes in subject matter.

            - Example: A transcript might contain both a patient's answer and the doctor's follow-up question.
        2. Assign Speakers Based on Roles:

            - Patient: Statements about symptoms, feelings, or personal experiences (e.g., "After eating") are likely from the patient.
            - Doctor: Questions or instructions (e.g., "Where do you feel the pain, above or below?") are likely from the doctor.

        3. Context from Previous Dialog: Use the Previous Dialog to decide if a speaker is continuing or if the dialogue has shifted to the other speaker. 
        If the previous speaker was the patient, the doctor is likely to speak next (and vice versa).

        4. Identify Role-Based Segments:

            For statements starting with personal experiences (e.g., "After eating"), assume it is the patient responding.
            For follow-up questions or medical instructions (e.g., "Where do you feel the pain?"), assume it is the doctor speaking.

        5. Handle Ambiguous Cases:
        If a segment cannot be easily attributed to one speaker, rely on the typical conversational roles of a doctor and patient, making a judgment based on the medical context (doctors usually ask questions, and patients usually describe symptoms).
        Compare the Current Transcript with the Previous Dialog to check for repeated text. If any segment from Current Transcript is already present in Previous Dialog, do not include it again in the output.
    Return the results in the following valid JSON format (an array of objects):

        {{
        "DiarizedResult": [
            {{
            "speaker": "Doctor" or "Patient",
            "text": "The statement from the current transcript text"
            }}
        ]
        }}

    Current Transcript: {CurrentTranscript}
    Previous Dialog: {PreviousDialog}
    """

    # Define the messages for the chat model
    messages = [
        {"role": "system", "content": "You are a medical expert. Diarize the provided streaming conversation (Current Transcript) between the doctor and the patient. Label each text segment based on the tone and content of the provided text, considering both the Current Transcript and the Previous Dialog."},
        {"role": "user", "content": str(prompt)}
    ]

    # try:
        # Send the request to GPT-4 in chat completion format
    response =  client.chat.completions.create(
        response_format={ "type": "json_object" },
            model=model_name,  # Use the appropriate model
            messages=messages,
            max_tokens=4096,  # Adjust token limit based on expected length of response
            temperature=0.0,
        )
    
    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens

    # logging.info("Openai Pricing .........")
    # logging.info("Diarization")
    # logging.info(f"model name {model_name}")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")


    json_response = json.loads(response.choices[0].message.content)

    # print(json_response)
    diarized_result = json_response.get("DiarizedResult")
    original_diarized__response= diarized_result.copy()
    if isinstance(original_diarized__response, list):
        last_dialoge = f"{original_diarized__response[-1].get('speaker', '')}: {original_diarized__response[-1].get('text', '')}"

    if target_language != "en-US" and OriginalTranscriptNeeded:
        print("language code for translate back", target_language[:2])
        for each in diarized_result:
            original_text = translate_client.translate(each["text"], source_language= "en", target_language= target_language[:2])
            each["originalTranslation"] = original_text['translatedText']
            each["text"] = each["text"]
            
    else:
        for each in diarized_result:
            # original_text = translate_client.translate(each["text"], source_language= "en", target_language= target_language[:2])
            each["originalTranslation"] = ""

    
    # print("last dialogue", last_dialoge)
    return diarized_result, last_dialoge



# def diarize_transcripted_text(client,transcription_text: str):
    
    

#     print("input text for diarization model", transcription_text)
#     # openai.api_key = os.getenv("OPENAI_API_KEY")
    
#     # model_name =os.getenv("OPENAI_MODEL")
#     model_name = OPENAI_MODELForSpeakerDiarization
#     # openai.api_key = os.getenv("OPENAI_API_KEY")
#     """
#     Use the OpenAI API to extract symptoms from the transcription text and suggest a follow-up question.
#     """
#     prompt = f"""
#     As the conversation streams in, identify the speaker for each segment of text in real-time. Label each segment as either "Doctor" or "Patient" strictly based on the tone and content of the provided text.

#         - Label as "Patient" if the statement reflects a concern, question, or inquiry typically made by a patient.
#         - Label as "Doctor" if it reflects a professional response, advice, or medical explanation.
#         - If the segment is too short or unclear, label it based on your highest confidence judgment of whether it sounds more like a doctor or a patient speaking.
#         - you can just pharphase if having any unclarity on the text

#     Strictly use only the streamed conversation details. Do not infer or add extra context not explicitly stated.

#     Return the results in the following valid JSON format (an array of objects):

#         {{
#         "DiarizedResult": [
#             {{
#             "speaker": "Doctor" or "Patient",
#             "text": "The statement from the conversation"
#             }}
#         ]
#         }}

#     Conversation Details: {transcription_text}
#     """

#     # Define the messages for the chat model
#     messages = [
#         {"role": "system", "content": "You are a medical expert. Diarize the provided streaming conversation between the doctor and the patient. Only label speakers as 'Doctor' or 'Patient' based strictly on the provided conversation data, as it streams in. If the conversation text is too short or unclear, label it based on your highest confidence judgment, either as 'Doctor' or 'Patient'. Do not infer any additional context beyond what is explicitly given"},
#         {"role": "user", "content": str(prompt)}
#     ]

#     # try:
#         # Send the request to GPT-4 in chat completion format
#     response =  client.chat.completions.create(
#         response_format={ "type": "json_object" },
#             model=model_name,  # Use the appropriate model
#             messages=messages,
#             max_tokens=10000,  # Adjust token limit based on expected length of response
#             temperature=0.0,
#         )
#     json_response = json.loads(response.choices[0].message.content)

#     print(json_response)
#     diarized_result = json_response.get("DiarizedResult")
#     return diarized_result

# OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
# # # # Example usage
# client = openai.OpenAI(api_key = OPENAI_API_KEY) 
# text="""Good morning, Mrs. Davis. What brings you in today? Good morning, doctor. I've been feeling extremely tired and light-headed for past few weeks. I'm also having...irregular periods. I see. Let's start with some details. Have you experienced any other symptoms besides sitting and irregular periods? Yes. I've also..."""
# response= diarize_transcripted_text(client,text)
# print(response)