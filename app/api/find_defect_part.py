from fastapi import APIRouter, File, UploadFile
from typing import List
import base64
from openai import OpenAI
from fastapi import APIRouter, HTTPException
from concurrent.futures import ThreadPoolExecutor
import asyncio


import json
from app.creds.config import  OPENAI_API_KEY
import openai


# Initialize the router
find_part_defect_router = APIRouter()


# Initialize OpenAI client
client = openai.OpenAI(api_key = OPENAI_API_KEY)

# Function to encode the image
def encode_image(file: bytes) -> str:
    return base64.b64encode(file).decode("utf-8")

# Function to process each image and get the description
def analyze_image(file_name: str, file_data: bytes):
    base64_image = encode_image(file_data)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a quality analyst tasked with inspecting a given part for defects. Analyze the part and provide a response that clearly states whether the part has any defects. If defects are found, describe the exact defects in concise and clear terms",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens= 100
    )
    # Extract the description from the response
    print(response.choices[0].message.content)
    response_text = response.choices[0].message.content
    is_defect, description = structure_response(response_text)
    return {"image_name": file_name, "isHavingDefect": is_defect,  "description": description}
# Async wrapper for threading
async def analyze_image_async(file_name: str, file_data: bytes):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, analyze_image, file_name, file_data)
    return result

@find_part_defect_router.post("/analyzeImagesToFindDefect")
async def analyze_images(files: List[UploadFile] = File(...)):
    tasks = []
    for file in files:
        file_data = await file.read()
        tasks.append(analyze_image_async(file.filename, file_data))
    
    results = await asyncio.gather(*tasks)
    return results




def structure_response(text):
    # print("transcripted_text",transcripted_text)
    
    messages = [
        {
            "role": "user",
            "content": f"""
                You will receive a text input. Your task is to convert the input into a JSON object with the following structure
                
                {{
                "isDefect": true or false,
                "Description": "short and precise description"
                }}
                Analyze the text to determine if it represents a defect (set isDefect to true) or not (set isDefect to false).
                Extract a concise description summarizing the key points of the text and assign it to the Description field.

                Input: {text}
                """
        }
    ]

    response = client.chat.completions.create(
        model= "gpt-4o-mini",
        response_format={ "type": "json_object" },
        messages=messages,
        max_tokens=200,
        temperature= 0.2,
        top_p=1.0
    )

    result = json.loads(response.choices[0].message.content)
    # print("transcript summary.......", result)
    is_defect = bool(result.get("isDefect", False))
    description = str(result.get("Description", ""))
    return is_defect, description
