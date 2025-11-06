

import json
from app.creds.config import OPENAI_MODELForDiagnosis


import re

# import os
# import logging
# from datetime import datetime



# # Set up logging configuration
# log_filename = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
# os.makedirs("logs", exist_ok=True)
# logging.basicConfig(filename=log_filename, level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')


def clean_text(input_string):
    # Remove non-ASCII characters (keeping only English letters, digits, whitespace, and punctuation)
    cleaned_string = re.sub(r'[^\x00-\x7F]+', '', input_string)
    return cleaned_string

def get_symtoms_(openai_client, conversation_for_symtoms):

    model_name = OPENAI_MODELForDiagnosis
    # model_name = OPENAI_MODEL
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    conversation_for_symtoms = clean_text(conversation_for_symtoms)

    prompt = f"""
        You are a medical expert AI. Analyze the following conversation between a doctor and a patient to identify any symptoms explicitly mentioned by the patient. Ensure the following:

            1. Exclude symptoms mentioned in the doctor's questions. Only include symptoms that the patient explicitly states
            2. Correct any spelling mistakes in the transcript that could affect symptom recognition.
            3. Include only symptoms that are directly mentioned or clearly described in the conversation. Do not infer or add symptoms that are not explicitly provided.
            4. Provide your response in JSON format, following this structure:
                            {{
                "Symptoms": "<Array of valid symptoms mentioned in the conversation, or an empty array if no symptoms are identified>"
                }}


        Here is the conversation to analyze:

        **Conversation**:{conversation_for_symtoms}"""

    # Define the messages for the chat model
    messages = [
        {"role": "system", "content": "You are a medical expert."},
        {"role": "user", "content": prompt}
    ]

    # try:
        # Send the request to GPT-4 in chat completion format
    response =  openai_client.chat.completions.create(
        response_format={ "type": "json_object" },
            model=model_name,  # Use the appropriate model
            messages=messages,
            max_tokens=4096,  # Adjust token limit based on expected length of response
            temperature=0.0,
        )
    

    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens
    # logging.info("Openai Pricing .........")
    # logging.info("Symtoms")
    # logging.info(f"model name {model_name}")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")

    json_response = json.loads(response.choices[0].message.content)
    Symptoms = json_response.get("Symptoms", "")
    # print(json_response)
    return Symptoms