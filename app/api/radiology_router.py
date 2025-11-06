import base64
import openai
import os
import tempfile
import io
from PIL import Image
from PyPDF2 import PdfReader
from fastapi import APIRouter, HTTPException, UploadFile
from pdf2image import convert_from_path
from pydantic import BaseModel
from app.creds.config import OPENAI_API_KEY, GENAI_API_KEY
from app.api.utils.Radiology.llm_prediction import analyze_image
from app.api.utils.Radiology.category_classification import detect_category_for_test
from app.api.utils.Radiology.labreports import detect_diagnosis_from_lab_report
from app.api.utils.Radiology.gen_llm_prediction import upload_and_analyze_image
from app.api.utils.Radiology.text_extraction import extract_text_with_textract, extract_text_from_pdf, is_scanned_pdf,process_all_pdf_file
from typing import List,Optional

# Initialize OpenAI client
generate_radiology_router = APIRouter()
client = openai.OpenAI(api_key=OPENAI_API_KEY)

class RadiologyResponse(BaseModel):
    potentialDiagnosis: str
    reason: str
    confidence: float
    category: str
    subCategory: str
    type: Optional[str] = None
@generate_radiology_router.post("/analyze-test", response_model=List[RadiologyResponse])
async def analyze_image_endpoint(files: List[UploadFile], type: int):
    try:    
        responses = []

        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded.")

        allowed_types = ["image/jpeg", "image/png", "image/jfif", "application/pdf"]

        for file in files:
            filename = file.filename.lower()
            print(f"Processing file: {filename}, Content Type: {file.content_type}")
            

            if file.content_type not in allowed_types and not filename.endswith(".jfif"):
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {filename}. Please upload a JPEG, PNG, JFIF, or PDF.")
            
            file_content = await file.read()
            file_io = io.BytesIO(file_content)
            file_io.seek(0)
            

            # Handle JFIF conversion
            if file.content_type == "image/jfif" or filename.endswith(".jfif"):
                image = Image.open(io.BytesIO(file_content))
                image_rgb = image.convert("RGB")
                converted_image_io = io.BytesIO()
                image_rgb.save(converted_image_io, format="JPEG")
                converted_image_io.seek(0)
                file = UploadFile(filename="converted_image.jpg", file=converted_image_io)
            
            if type == 0:  # X-ray Processing
                if file.content_type == "application/pdf":
                    pdf_path = f"./temp_{file.filename}"
                    print("Processing PDF:", pdf_path)
                    with open(pdf_path, "wb") as f:
                        f.write(file_io.read())
                    
                    images = process_all_pdf_file(pdf_path)
                    
                    for i, img in enumerate(images):
                        # Convert image to file-like object
                        image_io = io.BytesIO()
                        img.save(image_io, format="JPEG")
                        image_io.seek(0)

                        # Create UploadFile object
                        temp_file = UploadFile(filename=f"page_{i}.jpg", file=image_io)
                        
                        radiology_response = upload_and_analyze_image(temp_file, GENAI_API_KEY)
                        responses.append(radiology_response)
                      # Remove temporary PDF file
                    os.remove(pdf_path)
                    print(f"Removed temporary file: {pdf_path}")
                    
                else:
                    radiology_response = upload_and_analyze_image(file, GENAI_API_KEY)
                    
                
                    responses.append(radiology_response)
            elif type == 1:  # Lab Report Processing
                if file.content_type != "application/pdf":
                    raise HTTPException(status_code=400, detail="Lab report must be a PDF file.")
                
                with tempfile.NamedTemporaryFile(delete=False, mode="wb") as tmp:
                    tmp.write(file_content)
                    tmp_path = tmp.name

                # Open the PDF with PdfReader
                with open(tmp_path, "rb") as tmp_pdf:
                    reader = PdfReader(tmp_pdf)
                    num_pages = len(reader.pages)

                # Check page count
                if num_pages > 2:
                    raise HTTPException(status_code=400, detail="Unable to process PDF with more than 2 pages.")

                # Check if it's a scanned PDF
                if is_scanned_pdf(file_content):
                    # Extract text using AWS Textract
                    full_text = extract_text_with_textract(file_content)

                    if not full_text:
                        raise HTTPException(status_code=500, detail="Failed to extract text from scanned PDF.")
                else:
                    # Extract text using a normal text extraction method
                    full_text = extract_text_from_pdf(file_content)

                    if not full_text:
                        raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")

                # Perform lab report analysis
                lab_report_analysis = detect_diagnosis_from_lab_report(client, full_text)

                response = [{
                    "potentialDiagnosis": lab_report_analysis.get("potentialDiagnosis", "No diagnosis provided"),
                    "reason": lab_report_analysis.get("reason", "No reason provided"),
                    "confidence": lab_report_analysis.get("confidence", 0.0),
                    "category": lab_report_analysis.get("category", "Unknown"),
                    "subCategory": lab_report_analysis.get("subCategory", "Unknown"),
                }]
                return response
            
            else:
                raise HTTPException(status_code=400, detail="Invalid type specified. Type must be 0 (X-ray) or 1 (Lab report).")

        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")