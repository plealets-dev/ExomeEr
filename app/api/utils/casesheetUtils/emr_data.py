



import openai
import os
import json 
from app.creds.config import CASESHEETMODEL, OPENAI_API_KEY


# import logging
# from datetime import datetime



# # Set up logging configuration
# log_filename = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
# os.makedirs("logs", exist_ok=True)
# logging.basicConfig(filename=log_filename, level=print,
#                     format='%(asctime)s - %(levelname)s - %(message)s')



def transcript_to_medical_report(client, current_medication_data):
    print("started transcript_to_medical_report")
    # print("transcripted_text",transcripted_text)
#     all_keys = [
#     "orders",
#     "activeMedication",
#     "pomr",
#     "doctorsSummary",
#     "prescription"
# ]
    
    messages = [
        {
            "role": "user",
            "content": f"""
                You are a helpful assistant specialized in organizing patient-doctor not speaker diarized transcription into the following categories:

               
                 
                **activeMedication**:[{{
                 medicationName : ""
                 dosage : ""
                 route : ""
                 frequency : ""
                 duration : ""
                 notes : ""}}]
                
                i need Active Medication as dict of list
                
                Response contain Json cotani
                
                Case sheet Report:
                {current_medication_data}
                
            """
        }
    ]



    
    response = client.chat.completions.create(
        model= CASESHEETMODEL,
        response_format={ "type": "json_object" },
        messages=messages,
        max_tokens=2000,
        temperature=0,
        top_p=1.0
    )

    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens
    
    # logging.info("Openai Pricing .........")
    # logging.info("EMR Data....")
    # logging.info(f"model name gpt-4o-2024-05-13")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")
    # Extract and return the result
    # print("yes")
    # print(response.choices[0].message.content)
    result = json.loads(response.choices[0].message.content)
    # print("transcript summary.......", result)
    # prescription_text = result
    print("emr data fetching completed")
          
    # result_queue.put(result)
    print("stopped transcript_to_medical_report")
    return result


