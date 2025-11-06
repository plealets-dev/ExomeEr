import os
import json
import google.generativeai as genai
from fastapi import UploadFile
from tempfile import NamedTemporaryFile

def upload_and_analyze_image(file: UploadFile, gen_client):
    """
    Uploads a single X-ray image file and analyzes it using Gemini AI.

    Args:
        file (UploadFile): Uploaded image file.
        gen_client (str): API key for Gemini AI.

    Returns:
        dict: JSON response containing a single medical finding.
    """
    try:
        # Configure the API key
        genai.configure(api_key=gen_client)
        file.file.seek(0)  # Move pointer to start before reading
        # Save the file temporarily
        with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as temp_file:
            temp_file.write(file.file.read())
            temp_file_path = temp_file.name  # Get the temporary file path

        # Upload the file using the correct method (Ensure this method supports file paths)
        uploaded_file = genai.upload_file(temp_file_path, mime_type=file.content_type)
        if not uploaded_file or not uploaded_file.uri:
            return {"error": "File upload to Gemini AI failed"}

        # Construct the request
        contents = [
            {"file_data": {"file_uri": uploaded_file.uri, "mime_type": uploaded_file.mime_type}},
            {
                "text": """
                Analyze the X-ray image to identify the body part and detect abnormalities.

                **Instructions:**
                - Return a single finding in JSON format.
                - Maintain the exact field order.
                - 'Category' should specify the main system affected.
                - 'Subcategory' should specify the abnormality or 'Unclassified' if undefined.
                - 'Reason' must highlight key visual features.
                - 'Confidence' (0-100) represents diagnostic certainty.
                - 'Type'its return a radiology image so fine else give the response are none and reason gives please upload a radiology file.

                **Categories and Subcategories:**

                - **Skeletal System:** Fractures, Degenerative changes (e.g., arthritis, osteoporosis), Bone tumors, Congenital abnormalities (e.g., scoliosis, spina bifida)
                - **Respiratory System:** Pneumonia, Lung cancer, Pleural effusion, COPD, Tuberculosis
                - **Cardiovascular System:** Cardiomegaly, Pulmonary hypertension, Aortic aneurysm, Vascular calcifications
                - **Soft Tissue & Foreign Bodies:** Foreign objects, Masses, Calcifications, Soft tissue swelling
                - **Dental & Oral Structures:** Tooth decay, Impacted teeth, Jaw fractures, Oral tumors, Periodontal disease
                - **Cranial & Facial Structures:** Sinus masses, Skull fractures, Hydrocephalus, Craniosynostosis, Facial trauma
                - **Gastrointestinal System:** Bowel obstruction, Organomegaly (e.g., hepatomegaly, splenomegaly), Abdominal masses, Free air (pneumoperitoneum), Kidney stones
                - **Urinary System:** Kidney stones, Bladder stones, Hydronephrosis
                - **Musculoskeletal Soft Tissue:** Soft tissue calcifications, Muscle tears, Tendon injuries

                **Strict Response Format:**
                                {
                    "potentialDiagnosis": "Detected condition or No diagnosis provided",
                    "reason": "Supporting evidence or No diagnosis provided",
                    "confidence": 85.0 or 0.0,
                    "category": "Main category or Unclassified",
                    "subCategory": "Specific subcategory or Unclassified",
                    "type":X_ray,MRI, Ultrasound,CT scans etc or Unclassified
                }
                """ }
                            
                        ]

        # Run the model
        model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")
        response = model.generate_content(contents)
        

        # Cleanup: Remove temporary file after upload
        os.remove(temp_file_path)

        # Parse JSON response
                # Parse JSON response, removing markdown formatting
        try:
            cleaned_response = response.text.strip().strip("```json").strip("```").strip()
            json_response = json.loads(cleaned_response)
            
            return json_response
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from AI", "raw_response": response.text}

    except Exception as e:
        return {"error": str(e)}
