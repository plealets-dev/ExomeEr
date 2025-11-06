
import http
import requests
import json
import os
from dotenv import load_dotenv
import re
# from app.utils.FilePreprocessing.pdf_extraction_dependencies import extract_text_from_pdf
# from app.utils.auto_trigger_depe.download_file_share_pdf import download_file_from_az


def getUsercredentials():
    try:
        # load_dotenv()
        # load_dotenv(override=True)
        url = "qaadminnew.talosml.com"
        
        userName= "agilecoder"
        password= "Grit@1234"
        
        
        
        
        print("URL",url)
        print("User Name",userName)
        print("password",password)
 
        # Check if environment variables are set
        if not all([url, userName, password]):
            print(
                "Please make sure all environment variables are set.  username/password"
            )
            return None
 
        conn = http.client.HTTPSConnection(url)
        payload = json.dumps({"userName": userName, "password": password})
        # print("payload----",payload)
        authenticate = "qaagilecpt"  
        # print("origin ", f'https://{authenticate}.talosml.com')
        headers = {
        'Origin': f'https://{authenticate}.talosml.com',
        'Content-Type': 'application/json'
        }
 
        conn.request("POST", "/api/v1/User/Authenticate", payload, headers)
        res = conn.getresponse()
        data = res.read()
        response_json = json.loads(data.decode("utf-8"))
 
        # Extract bearer token
        bearerToken = response_json.get("accessToken")
        # print("bearerToken", bearerToken)
        # Close connection
        conn.close()
 
        if res.status == 200 and bearerToken:
            return bearerToken
        elif res.status == 401:
            print("Unauthorized access from get cred. Please check your credentials.")
            return None
        else:
            print(f"Response for get credential status code from backend: {res.status}")
            return None
    except http.client.HTTPException as e:
        print("An HTTPException occurred while getting the token:", e)
        return None
    except Exception as e:
        print("An error occurred while getting the token:", e)
        return None







def fetch_cpt_values(bearer_token):
    # print(bearer_token)
    backendurl = "qaagilecptapi.talosml.com"  
    url = f"https://{backendurl}/api/v1/CptCode/GetAllOtherCptCodeDetailsByPage"
    print("url............",url)
    authenticate = "qaagilecpt"
    print(authenticate)
    payload = json.dumps({
    "pageIndex": 0,
    "pageSize": 0,
    "isAll": True,
    "searchKeyWord": None
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {bearer_token}',
    'Origin': f'https://{authenticate}.talosml.com',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    
    try:
       
        # print("response",response)
        return  json.loads(response.text)
    except:
        print("not getting the cpt codes from the talos backend: ", response.text)
        return []



def search_cpt_description(casesheet_data, len_of_icd, icd_for_cpt_block):

    context_for_other_cpt =  "Orders: {orders}\n" \
                "Assessment: {assessment}\n" \
                "Plan: {plan}".format(
                                    orders=casesheet_data.get("Orders", ""),
                                    assessment=casesheet_data.get('Assessment', ''),
                                    plan=casesheet_data.get('Plan of Care', ''))
    bearer_token = getUsercredentials()
    # context_for_other_cpt = remove_special_characters(context_for_other_cpt)
    # handling exception
    # super_bill_search = [""]
    context_for_other_cpt =  context_for_other_cpt.replace("sr. no", "")
    cpt_values = fetch_cpt_values(bearer_token)
    # print(cpt_values)
    # return cpt_values["cptCodeDetailsDto"]
    # results = []
    # other_cpt_code_from_context_list = []
    # if cpt_values is None or 'cptCodeDetailsDto' not in cpt_values:
    #     print(results)
    #     return results,[]
    cpt_codes_list = []
    other_cpt_code_from_context_list = []
                               
    # print("apicptcodes",cpt_values['cptCodeDetailsDto'])
    for item in cpt_values['cptCodeDetailsDto']:
        res = []        
        if item and 'orderName' in item and item['orderName']:
            # Strip any leading or trailing whitespace
            item['orderName'] = item['orderName'].strip()
            pattern = r',(?![^()]*\))'
            # Splitting the string for order names - problem
            result = re.split(pattern,item['orderName'])

            # Removing parentheses and stripping whitespace
            order_list = [re.sub(r'[()]', '', item).strip() for item in result]
            name = item['codeDescription']
            for name in order_list[0:]:
                # print("name",name)
                cptnamematch=False
                if not name:
                    cptnamematch=False

                # print("name to lower",name)
                # print("testtt",r'\b' + re.escape(name.lower()) + r'\b')
                
                #original code 
                elif re.search(r'\b' + re.escape(name.lower()) + r'\b', context_for_other_cpt.lower()):
                    # print("matched order name",name)
                    cptnamematch = True
                    
                # * Updated regex with flexibility for special characters and spaces
                # elif re.search(r'\b' + re.escape(name.lower()).replace(r'\ ', r'\s*') + r'\b', context_for_other_cpt, re.IGNORECASE):
                #     print("Matched CPT code word:", name)
                #     cptnamematch = True    
                                        
                
                if cptnamematch:
                    print("cptnamematch",name)
                    print("cptcodematch", item['cptCode'])
                    other_cpt_code_from_context_list.append(item['cptCode'])
                    res.append(item['cptCode'])
                    print("cptcodematch",item['cptCode'])
                    res.append(item["codeDescription"])
                    res.append(name)
                    # Count the occur
                    cpt_codes_list.append(res)
                    
                    break

    restructure_cpt_code_ = restructure_other_cpt(cpt_codes_list, context_for_other_cpt, len_of_icd, icd_for_cpt_block)            
    return restructure_cpt_code_
    



def extract_mg_value(description):
    """
    Extracts the milligram (mg) value from the given description.
    Returns None if no mg value is found.
    """
    # Look for an independent mg value (e.g., "60 mg")
    match = re.search(r'(\d+)\s+mg\b', description)
    if match:
        # print("founddddddddddddddddddd")
        return int(match.group(1))
    return None




def calculate_and_update_unit(cpt_mg_value, context_for_other_cpt):
    # Extract mg values from cpt_code[1] and context_for_other_cpt
    
    context_mg_value = extract_mg_value(context_for_other_cpt)
    print("cpt_mg_value",cpt_mg_value)
    print("context_mg_value",context_mg_value)
    if context_mg_value is not None and cpt_mg_value is not None:
        print("calculation unit", context_mg_value % cpt_mg_value)
    else:
        print("Error: context_mg_value or cpt_mg_value is None.")
    # Check if both mg values are present and if cpt_mg_value is divisible by context_mg_value
    if cpt_mg_value and context_mg_value and context_mg_value % cpt_mg_value == 0:
        # Calculate the quotient
        unit =  context_mg_value // cpt_mg_value 
        return unit
        
    else:
        print("mg found in cpt code description but not in  other cpt code context")
        return 1
    



pointer=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']

def restructure_other_cpt(cpt_codes_list, context_for_other_cpt, len_of_icd, icd_for_cpt_block):
   
    otherCptCode = []
    
   
    if cpt_codes_list:
        
        for cpt_code in cpt_codes_list:
            
            cpt_mg_value = extract_mg_value(cpt_code[1])
            if cpt_mg_value:
                unit=calculate_and_update_unit(cpt_mg_value,context_for_other_cpt)
            else:
                unit=1   
            otherCptCode.append(
                {
                    "codeType": "Other-CPT", 
                    "cptCode": cpt_code[0], 
                    "description": cpt_code[1],
                    "unit": unit,
                    "pointer": ",".join(pointer[0:len_of_icd]),
                    "icdCodes": icd_for_cpt_block,
                    "PredictedAccuracy": None,
                    "cptCodePointers": [{"detail": cpt_code[2]}],
                    "cptCodeExamples": None,
                    "comment": cpt_code[2],
                    "modifier": ""
        })
        
   
    return otherCptCode
    # print("otherCptCode",otherCptCode)
    # return otherCptCode
    
    


# icd_for_cpt_block = "54353"
# len_of_icd = 3
# pointer = "A"            
# casesheet_data =  {"Orders": "Toe X-ray"}                                  
# print(search_cpt_description(casesheet_data, len_of_icd, icd_for_cpt_block))