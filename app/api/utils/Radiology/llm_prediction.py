from app.creds.config import RADIOLOGYMODEL, OPENAI_API_KEY
import json
import re
from app.api.utils.Radiology.image_processing import resize_and_encode_image
from fastapi import UploadFile, HTTPException

def analyze_image(file:UploadFile,client):
    print("started analyzing image")
    

    base64_image = resize_and_encode_image(file)
    prompt = """
    You are an assistant to the doctor, helping to detect potential diagnoses and analyze the provided X-ray image to identify any abnormalities.

    Additional Instructions:
    - Provide only a single finding in the specified JSON structure.
    - The "Reason" should include the key visual feature or evidence that supports the diagnosis (e.g., location of fracture, appearance of mass).
    - The "Confidence" level should represent the degree of certainty (from 0.0 to 100.0), based on the clarity of the feature and the likelihood of the diagnosis.

    Provide only a single finding in the specified JSON structure.
    The "Reason" should include the key visual feature or evidence that supports the diagnosis (e.g., location of fracture, appearance of mass, contrast differences, etc.).
    The "Confidence" level should represent the degree of certainty (from 0.0 to 100.0), based on the clarity of the feature and the likelihood of the diagnosis.
    Respond strictly in the following JSON format (ensure exact adherence to the structure, including capitalization and punctuation):

    {
    "Potential Diagnosis": "A brief description of the detected condition or abnormality",
    "Reason": "The specific observed feature or evidence supporting the diagnosis",
    "Confidence": 80.0
    }
    """
    
    # Send the request to OpenAI
    response = client.chat.completions.create(
        model=RADIOLOGYMODEL,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "user", "content": f"data:image/jpeg;base64,{base64_image}"},
        ],
    )

    # Parse the content of the response
    content = response.choices[0].message.content
    # if not content.strip():
    #     raise HTTPException(status_code=500, detail="OpenAI API returned an empty response.")
    # try:
    #     content_json = json.loads(content)
    # except json.JSONDecodeError as e:
    #     raise HTTPException(status_code=500, detail=f"Invalid JSON in response: {content}")
    content_json = json.loads(content)
    return content_json
    


