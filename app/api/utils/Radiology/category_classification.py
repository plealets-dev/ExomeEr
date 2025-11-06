from app.creds.config import RADIOLOGYMODEL, OPENAI_API_KEY
import json
import re
from app.api.utils.Radiology.image_processing import resize_and_encode_image
from fastapi import UploadFile


def detect_category_for_test(client,radiology_response):
    prompt_for_detect_category = """
    You are an assistant designed to categorize medical findings based on provided categories and subcategories.Analyze the "Potential Diagnosis" and "Reason" fields from the input JSON and classify them into one of the following categories and subcategories. If no matching category or subcategory is found, respond with an empty string for the "Category" field and an empty string for the "Subcategory" field.

    Categories and Subcategories:
    - Skeletal System:
        - Fractures
        - Degenerative changes
        - Bone tumors
    - Respiratory System:
        - Pneumonia
        - Lung cancer
        - Pleural effusion
    - Cardiovascular System:
        - Cardiomegaly
        - Pulmonary hypertension
    - Soft Tissue and Foreign Bodies:
        - Foreign objects
        - Masses
        - Calcifications

    Respond strictly in the following JSON format. (ensure exact adherence to the structure, including capitalization and punctuation) without any additional text or disclaimers::

    {
        "Category": "The main category of the finding (e.g., 'Respiratory System')",
        "Subcategory": "The specific subcategory (e.g., 'Pneumonia') or 'Unclassified'",
    }
    """

    combined_input = f"{prompt_for_detect_category}\n\nInput JSON:\n{json.dumps(radiology_response)}"
        
    mini_model_response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",  # Replace with your specific model ID
            messages=[
                {
                    "role": "user",
                    "content": combined_input
                }
            ]
        )

    ai_response_content = mini_model_response.choices[0].message.content

    clean_response = re.sub(r"^```json\n|\n```$", "", ai_response_content)
    
    mini_model_response_data = json.loads(clean_response)

    return mini_model_response_data
