from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.creds.config import CASESHEETMODEL, OPENAI_API_KEY
import openai
import json
from app.api.utils.casesheetUtils.alternative_medicine import find_alternate_prescription

# Initialize the router
alternate_medicine = APIRouter()


# Define the request body model
class PrescriptionRequest(BaseModel):
    medicineDetails: dict
    pateintID:int


# Define the POST endpoint
openai_client = openai.OpenAI(api_key = OPENAI_API_KEY)


@alternate_medicine.post("/getAlternateMedicine")
async def generate_case_sheet_endpoint(request: PrescriptionRequest):
    # print("enterd")
    try:


        medicineDetails = request.medicineDetails

        print("started alternate medicine data fetching")
        
        medicine_details = "\n".join(f"{key}: {value}" for key, value in medicineDetails.items())
        print("medicine_details", medicine_details)
        Alternatvive_prescription = find_alternate_prescription(openai_client, medicine_details)
                 
        
        print("finished alternate medicine data fetching")    
        
        # Combine the results
        # combined_result = result1 + result2
        
        return Alternatvive_prescription

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error decoding JSON from OpenAI response in casesheet: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")