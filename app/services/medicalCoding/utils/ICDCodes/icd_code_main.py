import os
import openai
import json
 
import os
import openai
import json
from app.creds.config import OPENAI_MODELForICD
 
def icdcode_using_llm(client, context):
    
    
    Prompt = f"""
    {{
        Objective:
        "understand the context predict most matched icd codes and its description"
 
      
        Guidelines:

    1. **Context Analysis:**
       - Carefully analyze the provided context to identify key medical conditions, symptoms, or injuries.
       - Look for specific indicators such as body parts, severity, laterality (e.g., left, right, bilateral), and specificity.

    2. **ICD Code Selection:**
       - Prioritize codes that are the most specific to the context.
       - If multiple codes match the context, prefer codes with more detailed descriptions.
       - Avoid codes marked as "unspecified" if a more specific alternative exists within the same category.
       - Consider laterality and severity, ensuring that codes match these details where applicable.

    3. **Code Exclusion:**
       - Exclude codes that are too general or non-specific unless no specific codes are available.
       - For bilateral conditions, retain the code indicating "bilateral" and remove separate codes for left and right.

    4. **Description Extraction:**
       - Provide a short description for each selected code.
       - The description should accurately summarize the condition, symptom, or injury.

            
    Medical Context: {context}
    Output as Json should contain only key 'IcdCodes'.

    IcdCodes : value contain list of dict contain icd code details (code, description, confident) for each icd codes. confident in percentage , only contain min 1 and maximum three most relevent icd codes
    
    
    }}
    """

   
   
    # Initialize the OpenAI client
 
    # Make the API call
    response = client.chat.completions.create(
        response_format={"type": "json_object"},
      messages=[
          {'role': 'user', 'content': Prompt},
      ],
      model= OPENAI_MODELForICD ,
      temperature=0
     )
    
    # llm_output= response.choices[0].message.content
    try:
        json_response = json.loads(response.choices[0].message.content)
        return json_response
    except Exception as e:        
        print("got unexpected error on get_most_specific_code_using_llm", str(e))   
        return {}



pointer=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']

def restructureIcds(params): #ICD Details will be the output from icd_reasoning
    icd_predictions = []

    # Assuming your list of items is named `icd_list`
    icd_list = params
    # print("icd_list", icd_list)
    # print("icd_detail", icd_detail)

    for i,item in enumerate(icd_list):
        
        # for detail in icd_detail['summaries'][item['icd']]:
        #     pointers.append({"detail":detail})

        icd_prediction = {
            "pointer": pointer[i],
            "icdCode": item['code'],
            "icdDesc": item['description'],
            "predictedAccuracy":item['confident'],
            "displayOrder": 0,
            "icdCodePointers": [],#replace with pointers if AI is used for icd prediction (now icd extracted from chart)
            "icdCodeExamples": None
        }
        icd_predictions.append(icd_prediction)
        # print ("icd_prediction",icd_prediction)

        
    return icd_predictions




def json_to_excel(data):
    result = []
    for key,value in data.items():
        result.append(f"{key}:\n{value}\n")
    return "\n".join(result)

  
def icd_code_main(client, casesheet_data):
    
    context =  "Chief Complaint: {complaint}\n" \
                "History Of illness: {hpi}\n" \
                "Assessment: {assessment}\n" \
                "Plan: {plan}".format(
                                    complaint=casesheet_data.get("Presenting Complaint", ""),
                                    hpi = casesheet_data.get("History of Present Illness", ""),
                                    assessment=casesheet_data.get('Assessment', ''),
                                    plan=casesheet_data.get('Plan of Care', ''))

    restructuredIcds = []
    icd_comma_seperated_string = ""
    icd_code_list = []
    if casesheet_data:

        print("started icd prediction")
        llm_json_response = icdcode_using_llm(client, context)
        icd_code_list = llm_json_response.get("IcdCodes", [])
        if icd_code_list:
            restructuredIcds = restructureIcds(icd_code_list)
            icd_comma_seperated_string = ", ".join([item['code'] for item in icd_code_list])
    
        print("finished icd prediction")
    
    return icd_code_list, restructuredIcds, len(restructuredIcds), icd_comma_seperated_string


