


# result = trnscript_categorisation(transcripted_text)
    


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
# logging.basicConfig(filename=log_filename, level=print,
#                     format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def find_alternate_prescription(client, prescription):
    # print("transcripted_text",transcripted_text)
    Wanted_keys = [
    "medicinename",
    "dosage",
    "confident",
    "note"
    ]
    
    messages = [
        {
            "role": "user",
            "content": f"""
                You are a helpful assistant specialized in prescription categorisatioin by understanding following {prescription}
                Analyze the provided `prescription`, and found possible alternative for each of the keys in `{', '.join(Wanted_keys)}`, return only the relevant details from the prescription text, filling in each sub-key where applicable. Ensure that **all four main categories** . If there is no relevant information for a sub-key, leave it as an empty string.
                
                OutPut shoud be Json key AlternativeMedicineList contain list of dict with following keys for each medicine
                medicinename: The name of the alternative medicine.
                dosage: The dosage of the medicine, including units
                confident: A confidence score representing the  percentage that how much accuracte  is the alternative.
                note: justify with short note with  why taken this as alternate medicine, who can use it, side effect or benifits
                
                
                prescription Details:
                {prescription}"""
        }
    ]

    response = client.chat.completions.create(
        model= OPENAI_MODELForDiagnosis,
        response_format={ "type": "json_object" },
        messages=messages,
        max_tokens=2000,
        temperature=0,
        top_p=1.0
    )

    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens
    
    # logging.info("Openai Pricing .........")
    # logging.info("Alternate Medicine Data....")
    # logging.info(f"model name {OPENAI_MODELForDiagnosis}")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")

    # Extract and return the result
    # print("yes")
    # print(response.choices[0].message.content)
    result = json.loads(response.choices[0].message.content)
    # print("transcript summary.......", result)
    AlternativeMedicineList = result.get("AlternativeMedicineList", list)
    return AlternativeMedicineList
