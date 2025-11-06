import json


def detect_diagnosis_from_lab_report(client,full_text):
    prompt_for_analyzing_lab_report = """
    You are an assistant to the doctor, helping to analyze the provided medical lab results and detect potential abnormalities or conditions.

    Additional Instructions:
    - Provide only a single lab result in the specified JSON structure.
    - The "Reason" should include the key details supporting the diagnosis (e.g., result values outside the reference range, presence of critical levels).
    - The "Confidence" level should represent the degree of certainty (from 0.0 to 100.0), based on the comparison of the result with the reference range and any clinical context provided in the lab report.
    - Categorize the lab result into its main category (e.g., Hematology, Biochemistry, etc.) and subcategory (e.g., CBC, Liver Function Test, etc.).
    
    Respond strictly in the following JSON format (ensure exact adherence to the structure, including capitalization and punctuation):

    {
        "potentialDiagnosis": "A brief description of the detected condition or abnormality", 
        "reason": "The specific observed feature or evidence supporting the diagnosis", 
        "confidence": 80.0,  
        "category": "The main category of the lab result (e.g., Hematology, Biochemistry)",
        "subCategory": "The specific subcategory (e.g., CBC, Liver Function Test)"
    }"""

    mini_model_response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",  
            messages=[
                {
                    "role": "user",
                    "content": prompt_for_analyzing_lab_report
                }
            ]
        )
    
    lab_report_content = mini_model_response.choices[0].message.content
    content_json = json.loads(lab_report_content)
    return content_json