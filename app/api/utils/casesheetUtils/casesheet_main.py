from app.creds.config import CASESHEETMODEL, OPENAI_API_KEY
import json
import re
# import logging
# from datetime import datetime
# import os

# # Set up logging configuration
# log_filename = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
# os.makedirs("logs", exist_ok=True)
# logging.basicConfig(filename=log_filename, level=print,
#                     format='%(asctime)s - %(levelname)s - %(message)s')


def casesheet_main_data(client, transcripted_text):
    print("started casesheet_main_data")
    model_name = CASESHEETMODEL
        

    # Regex pattern to extract only English lines
    # english_text = re.sub(r'[^\x00-\x7F]+', '', transcripted_text)

    # Optional: Remove leading/trailing whitespace
    # english_text = '\n'.join([line.strip() for line in english_text.splitlines() if line.strip()])
    # Clean up the text
    # Remove unwanted spaces, repeated punctuation, and extra commas
    # cleaned_text = re.sub(r'(?<!\w)[,.\s]+|[,.\s]+(?!\w)', ' ', english_text)
    # cleaned_text = re.sub(r'\s{2,}', ' ', cleaned_text).strip()
    # print("english case sheet paylad", cleaned_text)

    # print("english_text", english_text)
    # Define the prompt for OpenAI
    prompt = f"""
        
        Create a detailed doctor's case sheet based on the following doctor_patient_conversation.It cotain streamed conversation between doctor and patient data may in accurate. Extract relevant medical details such as:

        Presenting Complaint
        History of Present Illness
        Past History
        Social History
        Family History
        Menstrual History 
        Physical Examination
        Current Medication 
        Allergy
        Previous Treatment
        Previous Investigation
        Assessment
        Plan of Care
        
        Along with above details I need Prescription and Orders (Radiology/Lab/Procedures) as list of dict contain  for each orders/prescription with following details (if provided on the context else '') 
        
        Prescription:[{{
                 medication : ""
                 dosage : ""
                 frequency : ""
                 duration : ""
                 route : ""
                 "note": ""}}]
        
        Orders:[{{
            orderType : ""
            orderName : ""
            purpose : ""
            }}]
        

        Additional note:

            Do not include non-Radiology, non-Lab, or non-Procedure orders in the response

            If any information is not mentioned, It's value should be '' . Ensure all values are returned as strings.

            Return the response in JSON format, with each key as a string and the corresponding value also as a string.

        doctor_patient_conversation: {transcripted_text}
    """

    # Define the messages for the chat model
    messages = [
        {"role": "system", "content": "You are a medical expert."},
        {"role": "user", "content": prompt}
    ]

    # Send the request to GPT-4 in chat completion format
    response =  client.chat.completions.create(
    response_format={ "type": "json_object" },
        model=model_name,  # Use the appropriate model
        messages=messages,
        max_tokens=10000,  # Adjust token limit based on expected length of response
        temperature=0.0
    )

    
    json_response = json.loads(response.choices[0].message.content)

    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens
    
    # logging.info("Openai Pricing .........")
    # logging.info("Casesheet Data....")
    # logging.info(f"model name {CASESHEETMODEL}")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")

    # empty handling orders and prescription 
    orders  = json_response.get("Orders", [])
    if orders:
        if isinstance(orders, list):
            if not orders[0].get("orderName", ""):
                json_response["Orders"] = []
        else:
            print("orders from casesheet got unexpected type", type(orders))
            json_response["Orders"] = []


    prescription   = json_response.get("Prescription", [])
    
    if prescription:
        if isinstance(prescription, list):
            if not prescription[0].get("medication", ""):
                json_response["Prescription"] = []
        else:
            print("orders from casesheet got unexpected type", type(prescription))
            json_response["Prescription"] = []







    # Remove keys with None or empty string values
    cleaned_data = {key: value for key, value in json_response.items() if value not in (None, "", "None.", "None", "none", "None known.")}
    return cleaned_data
    # print("stoped casesheet_main_data")
   