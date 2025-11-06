import openai
import json
from dotenv import load_dotenv
import os 
from app.creds.config import OPENAI_MODELForDiagnosis
# import logging
# from datetime import datetime



# # Set up logging configuration
# log_filename = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
# os.makedirs("logs", exist_ok=True)
# logging.basicConfig(filename=log_filename, level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')



load_dotenv()

import re
def clean_text(input_string):
    # Remove non-ASCII characters (keeping only English letters, digits, whitespace, and punctuation)
    cleaned_string = re.sub(r'[^\x00-\x7F]+', '', input_string)
    return cleaned_string

def extract_diagnosis_and_next_question(client, transcript_text: str , age:int,gender:str):
    print("trying to get extract_diagnosis_and_next_question using llm")
    transcript_text = clean_text( transcript_text)
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    
    model_name = OPENAI_MODELForDiagnosis
    # model_name = OPENAI_MODEL
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    """
    Analyze the conversation between a doctor and a patient to extract  predict potential diagnoses, and suggest relevant follow-up questions.
    
    Args:
    conversation (str): The conversation between the doctor and patient.
    age (int): The age of the patient.
    gender (str): The gender of the patient.
    
    Returns:
    dict: A JSON object with the following keys:

        - "Diagnosis": A string of potential diagnoses with confidence scores.
        - "Next Question": A string representing the suggested follow-up question for the doctor.
    """
    prompt = f"""
        You are a medical expert. Based on the following conversation between a doctor and a patient, analyze the conversation, identify predict potential diagnoses, and suggest relevant follow-up questions that helps to identify the exact potential doagnose. 
        Consider the patient's age and gender when suggesting follow-up questions.

        Return your response in JSON format with the following structure:

        1. **Diagnosis**: A string of possible diagnoses, each formatted as "Diagnosis (Confidence Score in %)" and separated by commas. 
        Include  most possible diagnoses (maximum 3) based on patient details.
    
        2. **Next Question**: A single concise string suggesting the next follow-up question for the doctor to ask the patient, considering the patient's age ({age}) and gender ({gender}). Avoid asking previously addressed questions.

        Here is the conversation to analyze:

        **Conversation**:{ transcript_text}
        **Patient Age**:{age}
        **Patient Gender**:{gender}"""

    # Define the messages for the chat model
    messages = [
        {"role": "system", "content": "You are a medical expert."},
        {"role": "user", "content": prompt}
    ]

    # try:
        # Send the request to GPT-4 in chat completion format
    response =  client.chat.completions.create(
        response_format={ "type": "json_object" },
            model=model_name,  # Use the appropriate model
            messages=messages,
            max_tokens=10000,  # Adjust token limit based on expected length of response
            temperature=0.0,
        )
    

    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens

    # logging.info("Openai Pricing .........")
    # logging.info("Diagnosis and Next Question")
    # logging.info(f"model name {model_name}")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")

    
    
    


    json_response = json.loads(response.choices[0].message.content)
    
    # print("json_response for next question and Diagnosis", json_response)
    return json_response

# OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
# # # # Example usage
# client = openai.OpenAI(api_key = OPENAI_API_KEY) 
# response= extract_symptoms_and_next_question(client,[{'speaker': 'Doctor', 'text': 'Good morning, Mrs. Davis. What brings you in today?'}, {'speaker': 'Patient', 'text': "Good morning, doctor. I've been feeling extremely tired and light-headed for past few weeks. I'm also having...irregular periods."}, {'speaker': 'Doctor', 'text': "I see. Let's start with some details. Have you experienced any other symptoms besides sitting and irregular periods?"}, {'speaker': 'Patient', 'text': "Yes. I've also..."}],30,"Female")

# print(response)



