import re
import openai
# from dotenv import load_dotenv
import os
import json
from dotenv import load_dotenv
load_dotenv()
import json
from app.creds.config import OPENAI_MODELForMDMprediction
# import logging
def Json_extractor(json_data):
  start=json_data.find("{")
  end=json_data.rfind("}")
  json_text=json_data[start:end+1]
  json_output=json.loads(json_text)
  return json_output




def get_mdm_level_for_risk_factor(openai_client, context):
    # print("prescription context....",context)
    print("get_mdm_level_for_risk_factor started")

    
    Rule="""
        "MDM Level: Low
         Rules:
            - Low risk of morbidity from additional diagnostic testing or treatment
      
      
        "MDM Level: Moderate
         Rules:

            - Moderate risk of morbidity from additional diagnostic testing or treatment 
            - Decision regarding minor surgery with identified patient or procedure risk factors
            - Decision regarding elective major surgery without identified patient or procedure risk factors
            
        
        
        "MDM Level: High
         Rules:
        
            - Decision regarding elective major surgery with identified patient or procedure risk factors"
            - Decision regarding emergency major surgery"
            - Decision regarding hospitalization or escalation of hospital-level of care"
            - Decision not to resuscitate or to de-escalate care because of poor prognosis"
            - Parenteral controlled substances """

    Prompt = """
    {
        Objective: As a skilled Medical Coder, your responsibility is to assess the provided "Rules" and select the most appropriate complexity level Rule that aligns with the patient's current condition. When evaluating, consider all combinations of the given data (patient's present condition) to determine the risk. Your output should be in JSON format with the following keys: 'MDM Level', 'Rule', and 'Reason'.
        Important Note: on provided patient detail specifically mentioned that surgery is scheduled on current Visit date (Do not consider prior vist performed/sceduled surgery) , avoid selecting surgery-related rules in cases where the context only mentions surgical history or the possibility of  surgeries. Instead, apply the Low-Risk rule, especially when no immediate surgical intervention is planned or confirmed.
        "Medical Parameter": "%s"
        "MDM Rules": "%s",
        "output keys": ["MDM Level", "Rule","Reason"]
    }
    """ % (context,Rule)

    
   

    response = openai_client.chat.completions.create(
      messages=[
          {'role': 'user', 'content': Prompt},
      ],
      model=OPENAI_MODELForMDMprediction ,
      temperature=0
     )
    
    llm_output=(response.choices[0].message.content)

    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens

    # logging.info("Openai Pricing .........")
    # logging.info("Medical Coding Risk")
    # logging.info(f"model name gpt-4-0613")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")


    # print("Openai Pricing .........")
    # print("Medical Coding Risk")
    # print(f"model name gpt-4-0613")
    # print(f"output_token {output_token}")
    # print(f"input token {input_token}")


    print("llm_output for prescription",llm_output)
    mdmlevel,mdm_rule,Reason=get_mdm_category(Json_extractor(llm_output))
    print("mdmlevel....",mdmlevel)
    print("mdmrule....",mdm_rule)
    return mdmlevel, mdm_rule, Reason,llm_output

def get_mdm_category(llm_response):
    
        # if llm_response['Rule'].lower() in llm_response:
        #     rule.append(llm_response['Rule'])
        #     # print("ruleplan",llm_response['Rule'])
        #     return key, rule, llm_response['Reason']
    key=3
    # TODO
    # print("llm_response prescription",llm_response) 
    # for x in llm_response:
    print("mdm level predicted for prescription",llm_response.get('MDM Level',''))
    if llm_response.get('MDM Level','').lower()=="low":
        key=3
    if llm_response.get('MDM Level','').lower()=="moderate":
        key=4
    if llm_response.get('MDM Level','').lower()=="high":
        key=5
        
    # else:
    #     return None
    rules = llm_response.get('Rule',"")
    if isinstance(rules, str):
        if "," in rules:
            rules = rules.split(",")
        else:
            rules = [rules]
    
    

            
    return  key, rules, llm_response.get('Reason',"")
