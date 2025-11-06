import openai
import json

from dotenv import load_dotenv
import os 
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.creds.config import CASESHEETMODEL, OPENAI_API_KEY
from app.api.utils.casesheetUtils.casesheet_main import casesheet_main_data
from app.api.utils.casesheetUtils.emr_data import transcript_to_medical_report
import threading
import time
import queue
from app.api.utils.json_to_text import json_to_text

# Initialize the router
generate_case_sheet_router = APIRouter()

# # Load environment variables when the app starts
# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")
# model_name = os.getenv("OPENAI_MODEL")


import re
def clean_text(input_string):
    # Remove non-ASCII characters (keeping only English letters, digits, whitespace, and punctuation)
    cleaned_string = re.sub(r'[^\x00-\x7F]+', '', input_string)
    return cleaned_string

# Define the request body model
class TranscriptRequest(BaseModel):
    transcripted_text: str
    pateintID:int
# Define the POST endpoint
openai_client = openai.OpenAI(api_key = OPENAI_API_KEY)

@generate_case_sheet_router.post("/generate_case_sheet")
async def generate_case_sheet_endpoint(request: TranscriptRequest):
    # print("enterd")
    try:
        
        # Create threads and pass arguments using args

        case_sheet_data = casesheet_main_data(openai_client, request.transcripted_text)
        # Combine the results
        # combined_result = result1 + result2
        
        response = {
             "pateintID":request.pateintID,
             "casesheet":case_sheet_data
        }
        return response

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error decoding JSON from OpenAI response in casesheet: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Define the request body model
class EMRRequest(BaseModel):
    casesheet: dict
    pateintID:int

@generate_case_sheet_router.post("/emr")
async def generate_case_sheet_endpoint(request: EMRRequest):
    # print("enterd")
    try:
        
        # Create threads and pass arguments using args
        # case_sheet_string_data = json_to_text(request.casesheet)

        case_sheet_data = request.casesheet
        current_medication = case_sheet_data.get("Current Medication", "")
        print("current_medication", current_medication)
        if current_medication:
            emr_data = transcript_to_medical_report(openai_client, current_medication)
            
            # Combine the results
            # combined_result = result1 + result2
            
            response = {
                "pateintID":request.pateintID,
                "emr":emr_data
            }
            return response
        else:
            response = {
                "pateintID":request.pateintID,
                "emr": {
                    "activeMedication": []
                }
            }
            return response


    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error decoding JSON from OpenAI response in casesheet: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
