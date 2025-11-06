
import re
import openai
# from dotenv import load_dotenv
import os
import json
from dotenv import load_dotenv
import json
import logging
from app.creds.config import OPENAI_MODELForMDMprediction
def Json_extractor(json_data):
  start=json_data.find("{")
  end=json_data.rfind("}")
  json_text=json_data[start:end+1]
  json_output=json.loads(json_text)
  return json_output

load_dotenv()

import openai
import os 


# is_greaterthan_one_year = is_difference_greater_than_six_months(patient_details.get("injuryDate", ""), patient_details.get("visitDate", ""), agile_db_utils.get("ChronicEvaluationDays", 30))
def mdm_paramater_rule_mapping(openaiclient, data):
    # print("complexity context", paramater)
    # if not is_greater_than_an_year or is_greater_than_an_year is None:
        # Acute case 
    model = OPENAI_MODELForMDMprediction  
    
    Rules= """
            MDM Level: Low
            Rules:

                - 1 acute, uncomplicated illness or injury
                - 2 or more self-limited or minor problems
                - Acute, uncomplicated illness or injury requiring hospital inpatient or observation level of care
                

            MDM Level: Moderate
            Rules:
            
                - 1 acute complicated injury
                - 1 acute illness with systemic symptoms
                - 1 undiagnosed new problem with uncertain prognosis
                
            MDM Level: High
            Rules:
                - 1 acute or chronic illness or injury that poses a threat to life or bodily function"""
    
    Objective = """Objective:  You are an unbiased assistant to a Medical Coder. From the given 'MDM Rules' for complexity of problem addressed, go through each rule and select the most appropriate rule that accurately matches the patient's current medical condition. Consider factors such as injury and visit date, injury complication, current pain scale, assessment, and plan, especially emphasizing follow-up visits and stable conditions. Provide the output containing the keys 'MDM Level,' 'Rule,' and 'Reason' in JSON format.

                    Additional Notes:

                    Low MDM Level: Appropriate when the patient has a pain scale of less than 5, and The patient have no pain, the plan does not suggest significant treatments or advice. If the patient shows improvements or feels better, it will fall under the Low MDM level.

                    Moderate MDM Level: Appropriate when significant treatment is mentioned in the assessment/plan,  sees no significant improvement, or if the injury is complicated, which includes multiple treatment options or specialist consultations.
                    
                    
                    MDM Rules: %s

                    Medical Context: %s

                    """ % (Rules, data)    

    
    
    
    # elif is_greater_than_an_year:
        
    
       
    # chronic case


    # Objective = """
    # You are an impartial assistant to a Medical Coder. Your task is to analyze the medical conditions of patients current visit using the provided MDM rules. Follow the instructions below to determine the appropriate MDM level for patient.

    # Instructions:

    # 1. MDM Level: Low

    #     Rules:

    #     - 2 or More Self-Limited or Minor Problems

    #         Apply if the patient has two or more self-limited or minor problems that do not require significant interventions.
        
    #     - 1 Stable Chronic Illness
            
    #         The patient have no pain
    #         minimal improvement or any kind of improvemnt
    #         The patient is not experiencing any pain.
    #         The patient's symptoms are under control.
    #         The condition is not worsening or causing significant new symptoms.
    #         There is no need for major adjustments in the treatment plan.
            

    # 2. MDM Level: Moderate

    #     Rules:

    #         1. 2 or More Stable Chronic Illnesses
            
    #             - Even if the patient has only **one chronic condition**, classify it under "2 or More Stable Chronic Illnesses" if:
    #                 - There are no explicit signs of exacerbation, progression, or side effects of treatment.
    #                 - If there are multiple injuries and they are both chronic and stable, classify it as "2 or more stable chronic illnesses
    #                 - The pain scale (even if high, such as 5 or 6 out of 10) is not mentioned in conjunction with terms indicating worsening, radiating pain, or progression.
    #                 - The management plan includes routine follow-ups, additional physical therapy sessions, or ongoing diagnostic tests (like MRI, surgery) without specific indications of exacerbation or new symptoms.
    #                 - Note: A high pain scale alone does not constitute an exacerbation unless explicitly linked to worsening or progression.
                
    #             - Appropriate when the patient has a pain scale of less than 5, and the plan suggest significant treatments or advice 

    #         2. 1 or More Chronic Illnesses with Exacerbation, Progression, or Side Effects of Treatment
                
    #             - Apply this rule **only when**:
    #                 - The patient has **one or more chronic conditions** with **explicit signs** of:
    #                 - Exacerbation (e.g., "worsening pain," "radiating pain," or "increasing pain")
    #                 - Progression (e.g., "new symptoms," "complications," or "increased severity")
    #                 - Side effects of treatment (e.g., adverse reactions directly linked to a specific treatment)
    #                 - The case must clearly mention these signs for the rule to apply. Do not infer or assume exacerbation, progression, or side effects based on routine management actions or general symptoms like high pain levels.

    #     **Moderate Case Handling:**
    #         - Evaluate each case based on the criteria:
    #         - If the patient has one chronic condition, it should only be classified as "1 or More Chronic Illnesses with Exacerbation, Progression, or Side Effects of Treatment" if it meets the Moderate MDM level criteria with explicit exacerbation signs.
    #         - In the absence of such signs, regardless of pain level or management interventions, classify the case as "2 or More Stable Chronic Illnesses."
                        

    # 3. MDM Level: High

    #     Rules:
        
    #     - Severe Chronic Illness Exacerbation:

    #         Apply if the patient has one or more chronic illnesses with severe exacerbation, progression, or side effects of treatment.
        
    #     - Complex Decision-Making:
        
    #         Apply if the condition or scenario involves more complex decision-making or interventions not covered by the above rules.



    # Medical Context: %s

    # """ % (tett_data)         




    # print("rule for complexity", Rules)

    Prompt = """


    {}


    Output:
    Provide your assessment in JSON format, containing the following keys:

    MDM Level: The complexity level (Low or Moderate or High) based on the patient’s condition.
    Rule: The specific mdm rule that best applies as per the given Instructions.
    Reason: A short note to justifying why the chosen rule was applied.""" .format(Objective)

    # print("prompt", Prompt)
    model = OPENAI_MODELForMDMprediction
    print("running model ", model)

    

    response = openaiclient.chat.completions.create(
    response_format={ "type": "json_object" },
    messages=[
    {'role': 'user', 'content': Prompt},
    ],
    model= model,
    temperature=0
    )

    output_token = response.usage.completion_tokens
    input_token = response.usage.prompt_tokens

    logging.info("Openai Pricing .........")
    logging.info("Medical Coding Complexity Addressed")
    logging.info(f"model name {model}")
    logging.info(f"output_token {output_token}")
    logging.info(f"input token {input_token}")


    print("Openai Pricing .........")
    print("Medical Coding Complexity Addressed")
    print(f"model name {model}")
    print(f"output_token {output_token}")
    print(f"input token {input_token}")


    # print("complexity llm response ", response.choices[0].message.content)

    return (response.choices[0].message.content)





def get_mdm_category(llm_response):
    key =3
    # print("llm response for complexity",llm_response)
    if llm_response.get('MDM Level','').lower()=="low":
        key=3
    if llm_response.get('MDM Level','').lower()=="moderate":
        key=4
    if llm_response.get('MDM Level','').lower()=="high":
        key=5
        
    # else:
    #     return None  
    # print("key",key)
    return key, [llm_response['Rule']],llm_response['Reason'], llm_response
    



def get_complexity_addressed_main(openaiclient, mdm_paramters):
    llm_response=Json_extractor(mdm_paramater_rule_mapping(openaiclient, mdm_paramters))
    # # print("LLM RESPONSE For Complexity", llm_response)
    # keyword_response_content= extract_keywords(f"MDM Complexity Rule: {llm_response.get('Rule', '')} \n Reason:  {llm_response.get('Reason', '')}")
    # if isinstance(keyword_response_content, list):
    #     keyword_response_content = ", ".join(keyword_response_content)
        
    # llm_response["Reason"] = f" \n \n\n Reason: \n {llm_response.get('Reason', '')} \n 'Keywords': {keyword_response_content}"
    llm_response["Reason"] = f"\nReason: \n {llm_response.get('Reason', '')}"
    # key,rule,reason,llm_resp = get_mdm_category(output)
    
    # print("resv..............",resv)
    # resv = extract_keywords(reason)
    final_result = get_mdm_category(llm_response)
    return final_result
    
    