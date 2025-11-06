import re
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import openai
import json
from app.creds.config import azure_endpoint,formrecognizer_key,OPENAI_API_KEY,OPENAI_MODELForExtraction


# def document_extract_dischargesummary(pdf_bytes):
#     """Extract text directly from the uploaded PDF using Azure Form Recognizer."""

#     # Azure endpoint and key
#     endpoint = azure_endpoint
#     key = formrecognizer_key

#     # Initialize Form Recognizer client
#     document_analysis_client = DocumentAnalysisClient(
#         endpoint=endpoint, credential=AzureKeyCredential(key)
#     )

#     # Send PDF for analysis
#     poller = document_analysis_client.begin_analyze_document(
#         "prebuilt-read", pdf_bytes
#     )
#     result = poller.result()

#     # Extract key-value pairs
#     key_values = {}
#     for kv_pair in result.key_value_pairs:
#         if kv_pair.key and kv_pair.value:
#             key = re.sub(r"\W+", " ", kv_pair.key.content).strip()
#             key_values[key] = kv_pair.value.content

#     # Extract raw text
#     raw_text = result.content

#     # Combine key-value pairs with raw text for improved extraction accuracy
#     combined_text = raw_text
#     if key_values:
#         combined_text += "\n" + "\n".join([f"{k}: {v}" for k, v in key_values.items()])

#     return combined_text



def extract_information_dischargesummary(document_content, client):
    info_extraction_prompt = f"""
    Extract the following structured JSON format strictly from the provided text content. Populate the fields only with information present in the text. Do NOT generate fabricated data. If a field is missing, mark it as an empty string ("").

    ### Instructions:
    - Identify fields even if terminology varies (e.g., 'Date of Discharge' may appear as 'Discharge Date').
    - Extract numeric values accurately (e.g., age, date, contact numbers).
    - Extract names, procedures, medications, and care details directly from the text; do NOT assume or infer information.
    - Mark absent fields as an empty string ("").
    - Follow the specified JSON structure and ensure correct capitalization and punctuation.

    ### Key Rules for Accuracy:
    1. **Strict Data Matching:** Ensure each extracted value is present in the provided text. No assumptions or approximations.
    2. **Flexible Term Recognition:** Identify fields despite wording differences (e.g., 'Admission Date' may be written as 'Date of Admission').
    3. **No Example JSON Copying:** Avoid replicating any predefined format or placeholder data.
    4. **Data Integrity:** Use original wording from the text whenever possible.

    ### Confidence Score:
    - **All fields must include a confidence score** as a floating-point number (0.0 - 100.0).
    - Confidence should strictly reflect the model’s certainty based on text matching and structure.
    - If confidence cannot be determined, set it to 0.0.

    ### JSON Structure:
    {{
    "insuranceDetails": {{
        "insuranceCompanyName": {{ "value": "", "confidence": 0.0 }},
        "insuredCardIdNumber": {{ "value": "", "confidence": 0.0 }},
        "employeeId": {{ "value": "", "confidence": 0.0 }}
    }},
    "hospitalDetails": {{
        "hospitalName": {{ "value": "", "confidence": 0.0 }},
        "hospitalAddress": {{ "value": "", "confidence": 0.0 }}
    }},
    "patientDetails": {{
        "fullName": {{ "value": "", "confidence": 0.0 }},
        "age": {{ "value": "", "confidence": 0.0 }},
        "gender": {{ "value": "", "confidence": 0.0 }},
        "contactNumber": {{ "value": "", "confidence": 0.0 }},
        "patientMID": {{ "value": "", "confidence": 0.0 }},
        "patientIPID": {{ "value": "", "confidence": 0.0 }}
    }},
    "admissionDischargeDetails": {{
        "dateOfAdmission": {{ "value": "", "confidence": 0.0 }},
        "dateOfDischarge": {{ "value": "", "confidence": 0.0 }},
        "dischargeCondition": {{ "value": "", "confidence": 0.0 }},
        "daysInIcu": {{ "value": "", "confidence": 0.0 }},
        "roomType": {{ "value": "", "confidence": 0.0 }},
        "perDayRoomRent": {{ "value": "", "confidence": 0.0 }}
    }},
    "medicalInformation": {{
        "primaryConsultant": {{ "value": "", "confidence": 0.0 }},
        "consultantDepartment": {{ "value": "", "confidence": 0.0 }},
        "provisionalDiagnosis": {{ "value": "", "confidence": 0.0 }},
        "natureOfIllnessDiseaseWithPresentingComplaint": {{ "value": "", "confidence": 0.0 }},
        "durationOfPresentAilment": {{ "value": "", "confidence": 0.0 }},
        "dateOfFirstConsultation": {{ "value": "", "confidence": 0.0 }},
        "investigationAndMedicalManagement": {{ "value": "", "confidence": 0.0 }},
        "routeOfDrugAdministration": {{ "value": "", "confidence": 0.0 }},
        "nameOfSurgeryIfProvided": {{ "value": "", "confidence": 0.0 }},
        "isItRtaYesNo": {{ "value": "", "confidence": 0.0 }},
        "mandatoryPastHistoryOfAnyChronicIllness": {{ "value": "", "confidence": 0.0 }}
    }},
    "costExpenses": {{
        "expectedCostOfInvestigation": {{ "value": "", "confidence": 0.0 }},
        "icuCharges": {{ "value": "", "confidence": 0.0 }},
        "otCharges": {{ "value": "", "confidence": 0.0 }},
        "professionalFees": {{ "value": "", "confidence": 0.0 }},
        "medicineFees": {{ "value": "", "confidence": 0.0 }},
        "otherHospitalExpensesIfAny": {{ "value": "", "confidence": 0.0 }},
        "allInclusivePackageChargesIfApplicable": {{ "value": "", "confidence": 0.0 }},
        "sumOfTotalExpenses": {{ "value": "", "confidence": 0.0 }}
    }}
    }}
    ### Content to Extract Data From:
    {document_content}
    """
    response = client.chat.completions.create(
        model=OPENAI_MODELForExtraction,
        messages=[
            {
                "role": "user",
                "content": info_extraction_prompt
            }
        ]
    )

    content = response.choices[0].message.content

    # Improved regex to remove JSON code block markers and handle variations
    clean_response = re.sub(r"^```(json)?\n|\n```$", "", content.strip())
    
    try:
        content_json = json.loads(clean_response)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse the model's response as JSON. Verify response format.")

    return content_json
