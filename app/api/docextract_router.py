from fastapi import APIRouter, HTTPException , UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List,Union
from pathlib import Path
from app.api.utils.consentform import extract_information_consentform, preprocess_text
from app.api.utils.discharge_summary import extract_information_dischargesummary
from app.api.utils.formrecognizer_extract import document_extract_form,identify_document_type
import openai
from app.creds.config import OPENAI_API_KEY
from PyPDF2 import PdfReader, PdfWriter
import os
import concurrent.futures



extract_document_router = APIRouter()
client = openai.OpenAI(api_key = OPENAI_API_KEY)


class ConfidenceField(BaseModel):
    value: Optional[str] = None
    confidence: float = 0.0

class HospitalDetails(BaseModel):
    hospitalName: ConfidenceField = ConfidenceField()
    hospitalAddress: ConfidenceField = ConfidenceField()

class PatientDetails(BaseModel):
    fullName: ConfidenceField = ConfidenceField()
    age: ConfidenceField = ConfidenceField()
    gender: ConfidenceField = ConfidenceField()
    contactNumber: ConfidenceField = ConfidenceField()
    patientMID: ConfidenceField = ConfidenceField()
    patientIPID: ConfidenceField = ConfidenceField()

class ProcedureDetails(BaseModel):
    procedureName: ConfidenceField = ConfidenceField()
    doctorName: ConfidenceField = ConfidenceField()
    doctorSpecialty: ConfidenceField = ConfidenceField()
    diagnosis: ConfidenceField = ConfidenceField()

class ConsentDetails(BaseModel):
    consentGivenBy: ConfidenceField = ConfidenceField()
    consentDate: ConfidenceField = ConfidenceField()
    consentTime: ConfidenceField = ConfidenceField()
    interpreterName: ConfidenceField = ConfidenceField()
    witnessName: ConfidenceField = ConfidenceField()
    witnessRelationship: ConfidenceField = ConfidenceField()

class InsuranceDetails(BaseModel):
    insuranceCompanyName: ConfidenceField = ConfidenceField()
    insuredCardIdNumber: ConfidenceField = ConfidenceField()
    employeeId: ConfidenceField = ConfidenceField()

class MedicalInformation(BaseModel):
    primaryConsultant: ConfidenceField = ConfidenceField()
    consultantDepartment: ConfidenceField = ConfidenceField()
    provisionalDiagnosis: ConfidenceField = ConfidenceField()
    natureOfIllness: ConfidenceField = ConfidenceField()
    durationOfPresentAilment: ConfidenceField = ConfidenceField()
    dateOfFirstConsultation: ConfidenceField = ConfidenceField()
    investigationAndMedicalManagement: ConfidenceField = ConfidenceField()
    routeOfDrugAdministration: ConfidenceField = ConfidenceField()
    nameOfSurgery: ConfidenceField = ConfidenceField()
    isRta: ConfidenceField = ConfidenceField()
    mandatoryPastHistory: ConfidenceField = ConfidenceField()

class AdmissionDischargeDetails(BaseModel):
    dateOfAdmission: ConfidenceField = ConfidenceField()
    dateOfDischarge: ConfidenceField = ConfidenceField()
    dischargeCondition: ConfidenceField = ConfidenceField()
    daysInIcu: ConfidenceField = ConfidenceField()
    roomType: ConfidenceField = ConfidenceField()
    perDayRoomRent: ConfidenceField = ConfidenceField()

class CostExpenses(BaseModel):
    expectedCostOfInvestigation: ConfidenceField = ConfidenceField()
    icuCharges: ConfidenceField = ConfidenceField()
    otCharges: ConfidenceField = ConfidenceField()
    professionalFees: ConfidenceField = ConfidenceField()
    medicineFees: ConfidenceField = ConfidenceField()
    otherHospitalExpenses: ConfidenceField = ConfidenceField()
    allInclusivePackageCharges: ConfidenceField = ConfidenceField()
    sumOfTotalExpenses: ConfidenceField = ConfidenceField()


class ExtractionResponse(BaseModel):
    hospitalDetails: HospitalDetails = HospitalDetails()  
    patientDetails: PatientDetails = PatientDetails()
    insuranceDetails: InsuranceDetails = InsuranceDetails()
    procedureDetails: ProcedureDetails = ProcedureDetails() 
    consentDetails: ConsentDetails = ConsentDetails()
    admissionDischargeDetails: AdmissionDischargeDetails = AdmissionDischargeDetails()
    medicalInformation: MedicalInformation = MedicalInformation()
    costExpenses: CostExpenses = CostExpenses()

# class ExtractDetailsResponse(BaseModel):
#     document_type: str
#     extracted_data: Union[ExtractionResponse, List[ExtractionResponse]]


@extract_document_router.post("/extract-details",response_model=ExtractionResponse)
async def extract_details_from_pdf(file: UploadFile):
    try:

        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        # Read uploaded file as bytes
        pdf_bytes = await file.read()

        # Call the PDF extraction function
        extracted_form = document_extract_form(pdf_bytes)

        cleaned_content = preprocess_text(extracted_form)

        #Identify the document type
        document_type = identify_document_type(cleaned_content[:300], client)

        # Dispatch to appropriate extraction logic
        if document_type == "consentform":
            response = extract_information_consentform(cleaned_content,client)

        elif document_type == "dischargesummary":
            response = extract_information_dischargesummary(cleaned_content,client)
           
        
        # if document_type == "consentform":
        #     multiple_forms = split_consent_forms(extracted_form)
 
        #     with concurrent.futures.ThreadPoolExecutor() as executor:
        #         response = list(executor.map(lambda form: extract_information_consentform(form, client), multiple_forms))
 
        #     return JSONResponse(content={"document_type": document_type, "extracted_data": response})
 
        else:
            raise ValueError("Unknown document type.")
        
        return JSONResponse(content={"document_type": document_type, "extracted_data": response})
        # Return extracted data as JSON response
        # return JSONResponse(content={"document_type": document_type, "extracted_data": response})
        

    except ValueError as ve:
        # Handle invalid PDF format or empty content errors
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        # Catch unexpected errors and provide detailed output
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


# from pymongo import MongoClient
# from io import BytesIO


# mongo_client = MongoClient("mongodb+srv://talosqaadmin:QACo5uPhm43548@talos-qastag.uq6zldl.mongodb.net/")  
# db = mongo_client["TwigoCred"]
# collection = db["ExtractedDoc"]


# @extract_document_router.post("/extract-details", response_model=ExtractDetailsResponse)
# async def extract_details_from_pdf(file: UploadFile):
#     try:
#         if not file.filename.endswith(".pdf"):
#             raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

#         pdf_bytes = await file.read()
#         doc = fitz.open(stream=pdf_bytes, filetype="pdf")
#         extracted_results = []

#         for i in range(0, len(doc), 7):
#             sub_doc = fitz.open()
#             for j in range(i, min(i + 7, len(doc))):
#                 sub_doc.insert_pdf(doc, from_page=j, to_page=j)

#             file_index = (i // 7) + 1
#             filename = f"doc{file_index}.pdf"

#             # Save the chunk to memory
#             chunk_stream = BytesIO()
#             sub_doc.save(chunk_stream)
#             chunk_stream.seek(0)
#             chunk_bytes = chunk_stream.getvalue()

#             # Extract text and process
#             chunk_text = document_extract_form(chunk_bytes)
#             cleaned_content = preprocess_text(chunk_text)
#             document_type = identify_document_type(cleaned_content[:300], client)

#             if document_type == "consentform":
#                 extracted_data = extract_information_consentform(cleaned_content, client)
#             elif document_type == "dischargesummary":
#                 extracted_data = extract_information_dischargesummary(cleaned_content, client)
#             else:
#                 raise ValueError(f"Unknown document type in {filename}")

#             # Save to MongoDB immediately
#             collection.insert_one({
#                 "filename": filename,
#                 "document_type": document_type,
#                 "pdf_content": chunk_bytes,  # Store chunked PDF
#                 "extracted_data": extracted_data  # Store structured info
#             })

#             # Append for API response
#             extracted_results.append({
#                 "file": filename,
#                 "document_type": document_type,
#                 "extracted_data": extracted_data
#             })

#         return JSONResponse(content={"results": extracted_results})

#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

