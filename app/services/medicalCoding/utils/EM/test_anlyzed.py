import re
# from app.utils.FilePreprocessing.patinet_blocks_extractions import block_extraction_from_pdf
# from app.utils.auto_trigger_depe.db_handling import get_all_unprocessed_records
# from app.utils.auto_trigger_depe.download_file_share_pdf import download_file_from_az
import openai
# from dotenv import load_dotenv
import os
import json
from app.creds.config import OPENAI_MODELForTestAnalysis, OPENAI_API_KEY
# from app.utils.llm_utils.MDM_Mapping.Utils.Radiology.test_check_with_ngram import checking_prevoius_vs_current_test
# from app.utils.llm_utils.MDM_Mapping.Utils.Radiology.reviewed_or_ordered import checking_reviewed_and_ordered
# mdm_level=None
openai_client = openai.OpenAI(api_key = OPENAI_API_KEY)
import logging

import json
def Json_extractor(json_data):
  start=json_data.find("{")
  end=json_data.rfind("}")
  json_text=json_data[start:end+1]
  json_output=json.loads(json_text)
  return json_output

Rule = {

    '2': "Minimal or none",
    "3": {
        "Category1": {
            "1": "Review of prior external note(s) from each unique source*",
            "2": "Review of the result(s) of each unique test*",
            "3": "Ordering of each unique test*"
        },
        "Category2": {
            "1": "Assessment requiring an independent historian(s)"
        }
    },
    "4": {
        "Category1": {
            "1": "Review of prior external note(s) from each unique source*",
            "2": "Review of the result(s) of each unique test*",
            "3": "Ordering of each unique test*",
            "4": "Assessment requiring an independent historian(s)"
        },
        "Category2": {
            "1": "Independent interpretation of a test performed by another physician/other qualified health care professional(not separately reported)"
        },
        "Category3": {
            "1": "Discussion of management or test interpretation with external physician/other qualified health care professional/appropriate source(employer,case or claims manager)"
        }
    },
    "5": {
        "Category1": {
            "1": "Review of prior external note(s) from each unique source*",
            "2": "Review of the result(s) of each unique test*",
            "3": "Ordering of each unique test*",
            "4": "Assessment requiring an independent historian(s)"
        },
        "Category2": {
            "1": "Independent interpretation of a test performed by another physician/other qualified health care professional(not separately reported)"
        },
        "Category3": {
            "1": "Discussion of management or test interpretation with external physician/other qualified health care professional/"
        }
    }
}


def checking_reviewed_and_ordered(context):
    print("review of orders context", context)
    Prompt = """
    {
    "Objective": Analyze the patient document to identify tests that were reviewed or newly ordered specifically during the current visit. Only consider tests such as 'MRI', 'CT', 'EMG', and 'ECG', and exclude others like X-ray. Provide the results in a JSON format with two keys:

            reviewed: a list of applicable tests reviewed during the current visit.
            ordered: a list of applicable tests newly ordered during the current visit.
    
    
    "Medical Context": "%s"
    
    "Note": "Ensure your response is 100 percentage accurate and confident. Do not assume a review unless clearly stated."
    }
    """ % (context)

    
    

    response = openai_client.chat.completions.create(response_format={ "type": "json_object" },
      messages=[
          {'role': 'user', 'content': Prompt},
      ],
      model=OPENAI_MODELForTestAnalysis ,
      temperature=0
    )
    
    json_response = json.loads(response.choices[0].message.content)

    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens

    # logging.info("Openai Pricing .........")
    # logging.info("Medical Coding Data Analyzed: Checking Review and Orders")
    # logging.info(f"model name gpt-4o-2024-05-13")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")


    print("review of orders llm response", json_response)
    reviewed  = json_response.get("reviewed", [])
    ordered = json_response.get("ordered", [])
    return reviewed, ordered





def independent_historian_flag(context):
    # print("context for independent_historian_flag", context)
    Prompt = """
    
        Objective: You are a Medical Coder. From the provided "Medical Context," determine whether an independent historian is involved. An independent historian should be flagged "True" only if it is explicitly mentioned in the context, such as a direct discussion with management or another party. If no independent historian is explicitly mentioned, flag "False." Provide the reasoning for your decision in the "Reason" field, ensuring it is concise and directly related to the presence or absence of the independent historian. The output should be in JSON format.

        Medical Context: %s

        Output Structure:

        "Flag": ["True" or "False"]
        "Reason": [Concise justification for the decision]
        Note: Be 100 percentage confident in your response.
    
    """ % (context)

  

    response = openai_client.chat.completions.create(response_format={ "type": "json_object" },
      messages=[
          {'role': 'user', 'content': Prompt},
      ],
      model= OPENAI_MODELForTestAnalysis ,
      temperature=0
     )
    
    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens

    # logging.info("Openai Pricing .........")
    # logging.info("Medical Coding Data Analyzed: Independent Historian")
    # logging.info(f"model name gpt-4o-2024-05-13")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")

    
    json_response = json.loads(response.choices[0].message.content)
    # print("response for independent_historian_flag", json_response)
    return json_response


############################################################################################################


import re
import openai
# from dotenv import load_dotenv
import os
import json

def independent_interpretation_(context):
    # print("context for independent_interpretation_", context)

    Prompt = """

    {
        Objective: Determine if any MRI, CT, EMG, or ECG tests were reviewed during the current visit and if these were not reviewed in any previous visits.

        Instruction:

            1. Consider Only Specific Tests: Only include MRI, CT, EMG, or ECG tests that were explicitly reviewed during the current visit. Do not include X-ray reviews

            2. Handling Absence of Prior Visits: If no prior visits are explicitly mentioned in the context, assume there are no prior visits. In this case, treat any test (MRI, CT, EMG, or ECG) explicitly reviewed during the current visit as a new review.
            
            3. Exclude Tests Reviewed in Prior Visits: Set the "Flag" to "False" if the same MRI, CT, EMG, or ECG test was explicitly mentioned as reviewed in any explicitly mentioned prior visits. Do not consider tests that were only ordered, or scheduled in prior visits as reviewed. If the test was only performed but not explicitly reviewed in a prior visit, do not consider it as reviewed

        Medical Context:
        "%s"

        Output Json Format:
 
            "Flag": "True" or "False",
            "Reason": "Concise justification for the decision"
            

        Set the "Flag" to "True" only if:

            Current Visit Review: An MRI, CT, EMG, or ECG test was explicitly reviewed during the current visit.

            No Conflicting Prior Reviews:
            
                - Either no prior visits are explicitly mentioned in the context, or
                - If prior visits are mentioned, the same test (MRI, CT, EMG, or ECG) was not explicitly reviewed during any of those visits.

        Important Note: Do not consider tests that were only ordered or scheduled in prior visits as reviewed. Only tests explicitly marked as "reviewed" in prior visits should affect the decision.

    }
    """ % (context)

    

    
    response = openai_client.chat.completions.create(
        response_format={ "type": "json_object" },
      messages=[
          {'role': 'user', 'content': Prompt},
      ],
      model=OPENAI_MODELForTestAnalysis,
      temperature=0
     )
    
    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens



    # logging.info("Openai Pricing .........")
    # logging.info("Medical Coding Data Analyzed: Independent Interpretation")
    # logging.info(f"model name gpt-4o-2024-08-06")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")
   
    json_response = json.loads(response.choices[0].message.content)
    print("independent_interpretation_ llm response", response.choices[0].message.content)
    print("json_response",json_response)
    return json_response



def review_externel_notes_llm_calling(context):
    Prompt = """
    Objective: As a Medical Coder, review the provided "Medical Context" to determine if there is any explicit mention of reviewing prior external notes from each unique source, such as clinics, hospitals, or external providers.
    The output should be in JSON format, including both the "Flag" and "Reason."
    Instructions:

        1.Check for Explicit Mentions:
            - Look for clear statements indicating that prior external notes were reviewed specifically during the current visit.
            
        
        2.Determine the Flag Status:
            - Set "Flag" to "True" only if the context explicitly states that external notes were reviewed during the current visit.
            - Set "Flag" to "False" if there are no explicit mentions of reviewing prior external notes or if the context does not specify each unique external source.
        
        3.Provide a Concise Reason:
            - Ensure the reason is based solely on the presence of direct mentions of external sources. Exclude any terms that might not clearly indicate external providers or clinics.
    
    Medical Context: %s

    Output Structure:

    "Flag": ["True" or "False"]
    "Reason": [Concise justification for the decision]
    Note: Be 100 percentage confident in your response.
    """ % (context)



    response = openai_client.chat.completions.create(response_format={ "type": "json_object" },
      messages=[
          {'role': 'user', 'content': Prompt},
      ],
      model=OPENAI_MODELForTestAnalysis ,
      temperature=0
     )
    
    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens



    # logging.info("Openai Pricing .........")
    # logging.info("Medical Coding Data Analyzed: Review External Notes")
    # logging.info(f"model name gpt-4o-2024-08-06")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")
    
    json_response = json.loads(response.choices[0].message.content)
    return json_response

    
   

def review_results_uniquetest(context):
    print("context",context)
    print("review of orders context", context)
    Prompt = """
    {
    "Objective": As a Medical Coder, determine whether there is an explicit review of the results for each specific radiology test order (e.g., X-ray, CT, MRI) mentioned in the provided Medical Context. The 'Flag' should be set to 'True' only if the review of the results for the specific order(s) is explicitly stated in the **assessment** or **plan** sections. General references to imaging results are not sufficient unless they clearly indicate a review of the specific order(s). If no such explicit review is mentioned, set the 'Flag' to 'False'. Provide a concise and accurate Reason for your selection (do not include the Flag in the Reason). The output should be in JSON format.
    "Medical Context": "%s",
    "output key": ["Flag", "Reason"],
    "Note": "Ensure your response is 100 percentage accurate and confident. Do not assume a review unless clearly stated."
    }
    """ % (context)



    response = openai_client.chat.completions.create(response_format={ "type": "json_object" },
      messages=[
          {'role': 'user', 'content': Prompt},
      ],
      model=OPENAI_MODELForTestAnalysis ,
      temperature=0
    )

    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens



    # logging.info("Openai Pricing .........")
    # logging.info("Medical Coding Data Analyzed: Review Result each unique test")
    # logging.info(f"model name gpt-4o-mini-2024-07-18")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")
    
    json_response = json.loads(response.choices[0].message.content)
    print("review of orders llm response", json_response)
    return json_response



def order_of_uniquetest(context):
    print("order of each unique test context", context)
    Prompt = """
    {
        "Objective": You are a Medical Coder. From the given Medical Context, check if there is an order of any radiology or lab test. If there are multiple items within a single order, count it as one order. If there are multiple separate orders, count each order individually. If there are any orders, set the "Flag" as "True"; otherwise, set it as "False." Provide the count of distinct orders. The output should be in JSON format.
        "Medical Context": "%s"
        "output key":["Flag","Count"]

        Note: you need 100 percentage cofident on your response
    }
    """ % (context)


    response = openai_client.chat.completions.create(response_format={ "type": "json_object" },
      messages=[
          {'role': 'user', 'content': Prompt},
      ],
      model=OPENAI_MODELForTestAnalysis ,
      temperature=0
     )
    
    # output_token = response.usage.completion_tokens
    # input_token = response.usage.prompt_tokens



    # logging.info("Openai Pricing .........")
    # logging.info("Medical Coding Data Analyzed: Review Result each unique test")
    # logging.info(f"model name gpt-4o-2024-05-13")
    # logging.info(f"output_token {output_token}")
    # logging.info(f"input token {input_token}")
    
    json_response = json.loads(response.choices[0].message.content)
    print("order of each unique test llm response", json_response)
    return json_response

def Radiology_mdm_level(independent_historian_flag,independent_interpretation_flag ,review_externel_notes_flag,review_results_uniquetest_flag,order_flag, unique_test_count):
    
   
    independent_historian_flag = str(independent_historian_flag)
    independent_interpretation_flag = str(independent_interpretation_flag)
    review_externel_notes_flag = str(review_externel_notes_flag)
    review_results_uniquetest_flag = str(review_results_uniquetest_flag)
    


    print("independent_historian_flag",independent_historian_flag)
    print("independent_interpretation_flag",independent_interpretation_flag)
    print("review_externel_notes_flag",review_externel_notes_flag)
    print("review_results_uniquetest_flag", review_results_uniquetest_flag)
    print("unique_test_count",unique_test_count)
    
    flag_sum=0
    
   

    # print("order", order)
    # review_externel_notes_flag = True

    # print("unique_test_count, ", unique_test_count)
    # print("independent_historian_flag", independent_historian_flag)
    # print("independent_interpretation_flag", independent_interpretation_flag)
    # print("review_externel_notes_flag", review_externel_notes_flag)
    # print("review_results_uniquetest_flag", review_results_uniquetest_flag)


    flag_sum = sum(1 for value in [independent_historian_flag, independent_interpretation_flag, review_externel_notes_flag, review_results_uniquetest_flag, order_flag] if str(value).lower() == "true")
    # print(sum_total)

    # flag_sum=int(bool(independent_historian_flag))+int(bool(review_externel_notes_flag))+int(bool(review_results_uniquetest_flag))+int(bool(order)) #taking sum of all the flags to check how many of the conditions are satisfied 
    print("flag_sum", flag_sum)
    # print("independent_historian_flag", independent_historian_flag)


    limited_level_flag_sum = sum(1 for value in [review_externel_notes_flag, review_results_uniquetest_flag, order_flag] if str(value).lower() == "true")
    # low_level_flag_sum=int(bool(review_externel_notes_flag))+int(bool(review_results_uniquetest_flag))+int(bool(order)) # specifically for mdm level "low" 

    ################ predicting mdm level accoridng to mdm rules  TODO Category 3: Discussion of management or test interpretation #################
    #testcode 
    # import requests
    # import PyPDF2
    # independent_interpretation_flag = True 
    # print("independent_interpretation_flag = True..............")
    # # wgehyrj
    # if independent_interpretation_flag == "True":
    #     rule.append(Rule[f'{mdm_level}']["Category2"]["1"])
    
                              
        
        
    # #testcode
    # # Fetch the record from the AgileCPT collection
    # record = client.AgileCPT['UnProcessedCharts'].find_one({"keys.EncounterBlocks": {"$exists": True}})
    # print("record.....",record)
    # if record:
    #     # Check if there are at least 8 elements in the 'otherDocuments' array
    #     # other_documents = record.get("otherDocuments", [])
    #     other_documents = record.get("keys", {}).get("EncounterBlocks", {}).get("otherDocuments", [])
    #     print("other_documents..........",other_documents)

        
    #     if len(other_documents) >= 9:
    #         previous_progress_note = other_documents[8]  # 9th element is at index 8
    #         print("previous_progress_note....", previous_progress_note)

    #         # Check if the element has 'PreviousProgressNote' and 'isActive' fields
    #         if previous_progress_note.get("isActive") == True:
    #             print("PreviousProgressNote is active and found.")

    #             #Access the document path
    #             document_path = previous_progress_note.get("documentPath")
                
    #             if document_path:
    #                 # Add the base URL (replace 'https://yourdomain.com/' with your actual domain)
    #                 base_url = "https://yourdomain.com/"
    #                 full_url = base_url + document_path
                    
    #                 print(f"Downloading document from: {full_url}")
                    
    #                 # Function to download the document
    #                 import requests
    #                 response = requests.get(full_url)
                    
    #                 # Save the document to a local file
    #                 with open("previous_progress_note.pdf", 'wb') as file:
    #                     file.write(response.content)
                    
    #                 print("Document downloaded successfully.")
    #             else:
    #                 print("Document path not found.")


    #         else:
    #             print("Either PreviousProgressNote is missing or isActive is not True.")
    #     else:
    #         print("otherDocuments array does not have 8 elements.")
    # else:
    #     print("Record not found.")
    
    
    
    
    
    
    
    if flag_sum >3 and independent_interpretation_flag=="True":
        rule=[]
        mdm_level=5
        rule.append(Rule[f'{mdm_level}']["Category1"]["1"])
        rule.append(Rule[f'{mdm_level}']["Category1"]["2"])
        rule.append(Rule[f'{mdm_level}']["Category1"]["4"])

        if independent_historian_flag=="True":
            rule.append(Rule[f'{mdm_level}']["Category1"]["4"])

        rule.append(Rule[f'{mdm_level}']["Category2"]["1"])

        if unique_test_count>=1:
            rule.append(Rule[f'{mdm_level}']["Category1"]["3"])
        

    elif flag_sum>= 3 or independent_interpretation_flag =="True" or unique_test_count >=3:
        rule=[]
        mdm_level=4
        if review_externel_notes_flag=="True":
            rule.append(Rule[f'{mdm_level}']["Category1"]["1"])
        if review_results_uniquetest_flag=="True":
            rule.append(Rule[f'{mdm_level}']["Category1"]["2"])
        if independent_historian_flag=="True":
            rule.append(Rule[f'{mdm_level}']["Category1"]["4"])

        if independent_interpretation_flag=="True":
            rule.append(Rule[f'{mdm_level}']["Category2"]["1"])

        if unique_test_count>=1:
            rule.append(Rule[f'{mdm_level}']["Category1"]["3"])

    elif flag_sum == 2 and unique_test_count == 2 or independent_interpretation_flag=="True":
        rule=[]
        mdm_level=3

        if unique_test_count>=1:
            rule.append(Rule[f'{mdm_level}']["Category1"]["3"])
        

        if review_externel_notes_flag=="True":
            rule.append(Rule[f'{mdm_level}']["Category1"]["1"])
        if review_results_uniquetest_flag=="True":
            rule.append(Rule[f'{mdm_level}']["Category1"]["2"])
        if independent_historian_flag=="True":
            rule.append(Rule[f'{mdm_level}']["Category1"]["4"])
        if independent_interpretation_flag == "True":
            rule.append(Rule[f'{mdm_level}']["Category2"]["1"])
        
                              
        
        
        # #testcode
        # # Fetch the record from the AgileCPT collection
        #     record = client.AgileCPT['UnProcessedCharts'].find_one({"keys.EncounterBlocks": {"$exists": True}})
        
        #     if record:
        #         # Check if there are at least 8 elements in the 'otherDocuments' array
        #         other_documents = record.get("otherDocuments", [])
                
        #         if len(other_documents) >= 8:
        #             previous_progress_note = other_documents[7]  # 8th element is at index 7
                    
        #             # Check if the element has 'PreviousProgressNote' and 'isActive' fields
        #             if previous_progress_note.get("PreviousProgressNote") and previous_progress_note.get("isActive") == True:
        #                 # Your processing logic when 'PreviousProgressNote' is found and 'isActive' is True
        #                 print("PreviousProgressNote is active and found.")
        #             else:
        #                 print("Either PreviousProgressNote is missing or isActive is not True.")
        #         else:
        #             print("otherDocuments array does not have 8 elements.")
        #     else:
        #         print("Record not found.")
        

        

        

    # elif flag_sum >=3 or unique_test_count>2 or flag_sum==3 or independent_interpretation_flag=="True":
    #     rule=[]
    #     mdm_level=4

    #     if independent_historian_flag=="True":
    #         rule.append(Rule[f'{mdm_level}']["Category1"]["4"])

    #     if review_externel_notes_flag=="True":
    #         rule.append(Rule[f'{mdm_level}']["Category1"]["1"])
    #     if review_results_uniquetest_flag=="True":
    #         rule.append(Rule[f'{mdm_level}']["Category1"]["2"])

    #     if independent_interpretation_flag=="True":
    #         rule.append(Rule[f'{mdm_level}']["Category2"]["1"])
    
    elif limited_level_flag_sum >=2 or  independent_historian_flag=="True" or unique_test_count>1:
        rule=[]
        mdm_level= 3
        if unique_test_count >=1:
            rule.append(Rule[f'{mdm_level}']["Category1"]["3"])

        if review_externel_notes_flag=="True":
            rule.append(Rule[f'{mdm_level}']["Category1"]["1"])
        if review_results_uniquetest_flag=="True":
            rule.append(Rule[f'{mdm_level}']["Category1"]["2"])
        if independent_historian_flag=="True":
            rule.append(Rule[f'{mdm_level}']["Category2"]["1"])
        
    
    elif unique_test_count == 1 or flag_sum ==1:
        rule=[]
        mdm_level= 2
        mdm_rule_level = 3
        if unique_test_count >=1:
            rule.append(Rule[f'{mdm_rule_level}']["Category1"]["3"])
        elif review_externel_notes_flag=="True":
            rule.append(Rule[f'{mdm_rule_level}']["Category1"]["1"])
        elif review_results_uniquetest_flag=="True":
            rule.append(Rule[f'{mdm_rule_level}']["Category1"]["2"])
        elif independent_historian_flag=="True":
            rule.append(Rule[f'{mdm_rule_level}']["Category2"]["1"])
        


    
    else:
        mdm_level = 1
        rule = []

            
    return mdm_level,rule,flag_sum




def get_mdm_level_for_radiology(context,order_context):
    
    print(" started get_mdm_level_for_radiology")

    
    # print("context for radiology...........................",context)
    #radiologyblock count and Reasoning
    # print("prgRadiologyDetails", prgRadiologyDetails)
    
    # count = len(orders_length) 
    
        
    

    ############ flag for presence of each rules and AI Reasoning ####################
    llm=[]
    # interpretation_flag = False
    
    order_of_each_unique_test_response = order_of_uniquetest(context)
    order_flag, orders_count = order_of_each_unique_test_response.get("Flag", False), order_of_each_unique_test_response.get("Count", "")
    llm.append({"Rule":"Ordering of each unique test", "Flag": order_flag, "LLM_Response":orders_count})
    
    independent_historian_response = independent_historian_flag(context)
    historian_flag, historian_flag_reason= independent_historian_response.get("Flag", False), independent_historian_response.get("Reason", "")
    llm.append({"Rule":" Independent historian of tests", "Flag": historian_flag, "LLM_Response":historian_flag_reason})

    # checking same test done by comparing current test and previous with ngram 
    # Eg: filtered_current_trigrams [('mri', 'of', 'low'), ('mri', 'right', 'knee')]
    # filtered_previous_trigrams [('mri', 'of', 'low'), ('mri', 'right', 'knee'), ('emg', 'have', 'done')]
    # True, 2 test(s) are in the current visit and all are mentioned in the previous visit.

    orders,reviews = checking_reviewed_and_ordered(order_context)
 
    # PreviousVisitsContext = f"Previous Visits:\n{PreviousVisitsHPI}\n"
    # tests = ['MRI', 'CT', 'EMG', 'ECG']

    # all_current_trigrams_mentioned_on_previous_flag, len_current_visit_test, len_previous_visit_same_test = checking_prevoius_vs_current_test(CurrnentVisitContext, PreviousVisitsContext, tests)
   
       
        
   
        
    print("just ordered not reviewd", orders)
    if len(reviews) >=  1:
        independent_interpretation_response = independent_interpretation_(context)
        interpretation_flag, interpretation_flag_reason = independent_interpretation_response.get("Flag", False), independent_interpretation_response.get("Reason", "")
    else:
        print("no reviews of test found ['MRI', 'CT', 'EMG', 'ECG']")
        interpretation_flag, interpretation_flag_reason = False, "No review of tests such as MRI, CT, EMG, or ECG was conducted during the current visit."
    # TODO need to check with previous progress note that performed same test review. for now we are assuming test is not mentioned on previos encounter 
    # TODO commanding this for now since it could not handle the case of only ordered 
    # elif not all_current_trigrams_mentioned_on_previous_flag and len_current_visit_test >= 1 and PreviousVisitsHPI.strip() == "N/A":
    #     interpretation_flag, interpretation_flag_reason = "True", "The test has been reviewed, but it could not be found in the prior visit's on the latest. Please consult the previous progress note Manually, which is currently being developed, for further details."


    # print("interpretation_flag",interpretation_flag)
    # print("making to interpretation_flag to false")

    # interpretation_flag = False
    # interpretation_flag_reason = ""

    llm.append({"Rule":"Independent interpretation of tests",
                "Flag":interpretation_flag,
                "LLM_Response":interpretation_flag_reason})
    
    
    # review_externel_notes_response = review_externel_notes_llm_calling(context)
    # externel_notes_flag, externel_notes_flag_reason = review_externel_notes_response.get('Flag', False), review_externel_notes_response.get('Reason', "")
    # print("externel_notes_flag predicted as ", externel_notes_flag)
    # print("making to externel_notes_flag to false")
    externel_notes_flag_reason = ""
    externel_notes_flag = False
    # print("externel_notes_flag", str(externel_notes_flag))
    # llm.append({"Rule":"Review of prior external note(s) from each unique source*",
    #             "Flag":externel_notes_flag,
    #             "LLM_Response":externel_notes_flag_reason})

    if order_flag == "True":
        review_results_uniquetest_response = review_results_uniquetest(order_context)
        results_uniquetest_flag, results_uniquetest_flag_reason= review_results_uniquetest_response.get('Flag', False), review_results_uniquetest_response.get('Reason', "")
        # print("review_results_uniquetest_response", review_results_uniquetest_response)
        llm.append({"Rule":"Review of the result(s) of each unique test",
                    "Flag":results_uniquetest_flag,
                    "LLM_Response":results_uniquetest_flag_reason})
    else:
        print("skipping review unique test because no order performed")
        results_uniquetest_flag = False
        results_uniquetest_flag_reason = ""


    
    # print("total llm response for radiology", llm)
    
    
    #################### mdm rule prediction ###################
    mdmlevel,Rules,flag_sum = Radiology_mdm_level(historian_flag,interpretation_flag ,externel_notes_flag,results_uniquetest_flag, order_flag, orders_count)
    # Rules=",".join(Rules)
    Ai_reason = ""
    ############### combining all the Ai Reasons for each predictions #################
    if str(order_flag) == "True":
        Ai_reason += "\n - " + f"No. of Radiology/Lab orders:  {orders_count}"
    if str(historian_flag)=="True":
        Ai_reason += "\n - " + historian_flag_reason
    if str(interpretation_flag)=="True":
       Ai_reason+= "\n\n - " + interpretation_flag_reason
    if str(externel_notes_flag) =="True":
       Ai_reason+= "\n\n - " + externel_notes_flag_reason
    if str(results_uniquetest_flag)=="True":
       Ai_reason+= "\n\n - " + results_uniquetest_flag_reason
    

    # print("ai reason for radiology", Ai_reason)
    return mdmlevel, Rules, Ai_reason, llm, flag_sum