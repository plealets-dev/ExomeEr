from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.creds.config import CASESHEETMODEL, OPENAI_API_KEY
import openai
import json

from app.services.medicalCoding.medical_coding_main import medical_coding_main
# Initialize the router
medical_coding = APIRouter()


# Define the request body model
class MedicalRequest(BaseModel):
    casesheet: dict
    pateintID:int


# Define the POST endpoint
openai_client = openai.OpenAI(api_key = OPENAI_API_KEY)


@medical_coding.post("/getMedicalCode")
async def generate_case_sheet_endpoint(request: MedicalRequest):
    # print("enterd")
    # try:
        
    # Create threads and pass arguments using args
    # TODO medical coding 
    medical_coding_response = medical_coding_main(openai_client, request.casesheet)
    # Combine the results
    # combined_result = result1 + result2
    
    return medical_coding_response

    # except json.JSONDecodeError as e:
    #     raise HTTPException(status_code=500, detail=f"Error decoding JSON from OpenAI response in casesheet: {str(e)}")

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")