
from app.creds.config import OPENAI_MODELForDictation, OPENAI_API_KEY
import json


def medical_tagging(client, CurrentTranscript: str):
  

    print("current transcript :", CurrentTranscript)
  
    
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # model_name =os.getenv("OPENAI_MODEL")
    model_name = OPENAI_MODELForDictation
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    """
    Use the OpenAI API to extract symptoms from the transcription text and suggest a follow-up question.
    """
    prompt = f"""
   
    Task:
        Process streaming audio transcription data of medical dictation by a doctor. Analyze the transcription to extract relevant information and assign the appropriate tags to each segment.
    Important Notes:
        1. If a segment contains content corresponding to multiple tags, provide all applicable tags as a list. If the segment corresponds to a single tag, provide it as a single item in the list.
        2. Use only the provided tags to label the extracted segments accurately.
    Output Format Example as Json:
            {{ MedicalDictationTags: ["CHIEF COMPLAINT", "CURRENT MEDICATIONS"] }},

    Available Tags:
        - CHIEF COMPLAINT
        - CURRENT MEDICATIONS
        - DISCHARGE MEDICATIONS
        - DISCHARGE PLAN
        - FAMILY HISTORY
        - FINDINGS
        - REVIEW OF SYSTEMS
        - HISTORY OF PRESENT ILLNESS
        - INDICATIONS
        - LABS
        - PAST SURGICAL HISTORY
        - PHYSICAL EXAM
        - RADIOLOGY
        - OTHER

    Input:
       {CurrentTranscript}

    """

    # Define the messages for the chat model
    messages = [
        {"role": "system", "content": "Process streaming medical dictation data, extract and tag segments accurately using only provided tags, ensure coherence in paraphrasing incomplete data, and do not add any extra information not present in the stream"},
        {"role": "user", "content": str(prompt)}
    ]

    # try:
        # Send the request to GPT-4 in chat completion format
    response =  client.chat.completions.create(
        response_format={ "type": "json_object" },
            model=model_name,  # Use the appropriate model
            messages=messages,
            max_tokens=4096,  # Adjust token limit based on expected length of response
            temperature=0.0,
        )
    
   
    json_response = json.loads(response.choices[0].message.content)

    medical_dictation_tagged_response = json_response.get("MedicalDictationTags", [])
    
    # print("last dialogue", last_dialoge)
    return medical_dictation_tagged_response