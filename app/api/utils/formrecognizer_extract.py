import re
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import openai
import json
from app.creds.config import azure_endpoint,formrecognizer_key,OPENAI_API_KEY,OPENAI_MODELForExtraction
from pymongo import MongoClient
from app.creds.config import MongoConnectionString

client = MongoClient(MongoConnectionString)
db = client["TwigoCred"]
collection = db["DocTypesConfig"]

def document_extract_form(pdf_bytes):
    """Extract text directly from the uploaded PDF using Azure Form Recognizer."""

    # Azure endpoint and key
    endpoint = azure_endpoint
    key = formrecognizer_key

    # Initialize Form Recognizer client
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    # Send PDF for analysis
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-read", pdf_bytes
    )
    result = poller.result()

    # Extract key-value pairs
    # key_values = {}
    # for kv_pair in result.key_value_pairs:
    #     if kv_pair.key and kv_pair.value:
    #         key = re.sub(r"\W+", " ", kv_pair.key.content).strip()
    #         key_values[key] = kv_pair.value.content
    #         print("keyvalues:" , kv_pair)
    
    # Extract raw text
    raw_text = result.content

    # Combine key-value pairs with raw text for improved extraction accuracy
    combined_text = raw_text
    # if key_values:
    #     combined_text += "\n" + "\n".join([f"{k}: {v}" for k, v in key_values.items()])

    return combined_text


def form_recognize(content,client):
    form_recognize_prompt = f"""
    You are an expert in medical document classification.
    Analyze the text below and classify it as either "Consent Form" or "Discharge Summary".
    
    Text:
    {content}

    Respond **only in valid JSON format** with the following structure:
    {{
        "document_type": "Consent Form" or "Discharge Summary" or "Unknown Document Type"
    }}
    Do not include any additional text, explanations, or formatting outside of the JSON response.
    """
    response = client.chat.completions.create(
        model=OPENAI_MODELForExtraction,
        messages=[
            {
                "role": "user",
                "content": form_recognize_prompt
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


def identify_document_type(text: str, client) -> str:
    text_lower = text.lower()
    # Retrieve keyword mappings from the database
    keywords = collection.find_one({"_id": 1})
    if keywords:
        for key, value in keywords.items():
            if isinstance(value, list) and any(keyword in text_lower for keyword in value):
                # print("doctype:", key)
                return key.lower().replace(" ", "")  
    
    # If DB lookup fails, fallback to AI-based classification
    try:
        recognized_response = form_recognize(text, client)
        recognized_type = recognized_response.get("document_type")
        
        if recognized_type == "Consent Form":
            return "consentform"
        elif recognized_type == "Discharge Summary":
            return "dischargesummary"
        else:
            raise ValueError("AI model returned an unknown document type.")
    except Exception as e:
        raise ValueError(f"Failed to classify document using AI model: {str(e)}")

