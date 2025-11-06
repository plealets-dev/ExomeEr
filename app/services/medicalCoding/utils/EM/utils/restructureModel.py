


from app.api.utils.json_to_text import json_to_text



    # custom_group    
groups={
1: {"ParameterName": "INJURY/ILLNESS", "ChartBlocks": ["Presenting Complaint", "Assessment", "Plan of Care"]},
2: {"ParameterName": "PHYSICAL EXAMINATION",  "ChartBlocks": ['Physical Examination']},
3: {"ParameterName": "RADIOLOGY/SCANNING", "ChartBlocks": ["Plan of Care", 'Assessment','Orders']},
4: {"ParameterName": "SURGICAL HISTORY", "ChartBlocks" : ["Past History"]},
5: {"ParameterName": "PAST MEDICAL HISTORY",  "ChartBlocks": ["Past History"]},
6: {"ParameterName": "MEDICATION", "ChartBlocks": ["Prescription", "Current Medication"]},
7: {"ParameterName": "SOCIAL HISTORY", "ChartBlocks" : ["Social History"]}}
   



def restructureData(case_sheet_data, mdm_mapping_dict_by_group, chart_content_by_group, final_mdm_level, restructuredIcds, other_cpt_codes, icd_comma_seperated_string):

    print("other cpt codes", other_cpt_codes)
    cpt_codes = [{

                "codeType": "E&M",
                "cptCode": f"9921{final_mdm_level}",
                "description": "",
                "modifier": "",
                "unit": 1,
                "pointer": "",
                "icdCodes": icd_comma_seperated_string,
                "predictedAccuracy": None,
                "isManual": None,
                "displayOrder": None,
                "comment": None,
                "cptCodePointers": [],
                "cptCodeExamples": []
            }] + other_cpt_codes
    

    orders = json_to_text(case_sheet_data.get("Orders", ""), keyname = "orderName")
    

    #

    # Keys to check
    keys_to_check = ["Personal History", "Family History", "Social History"]

    # Dynamically construct the string for the specified keys
    social_history_content = "\n".join(
        f"{key}: \n {case_sheet_data[key]}"
        for key in keys_to_check
        if case_sheet_data.get(key)  # Include only if the value is not empty
    )



    keys_to_check = ["Prescription", "Current Medication"]
    if case_sheet_data.get("Prescription", []):
        case_sheet_data["Prescription"] = json_to_text(case_sheet_data.get("Prescription", ""), keyname = "medication")
        # print("prescription", prescription)  

    # Dynamically construct the string for the specified keys

    medication_data = "\n".join(
        f"{key}: \n {case_sheet_data[key]}"
        for key in keys_to_check
        if case_sheet_data.get(key)  # Include only if the value is not empty
    )
    
    

   
    response_model = {

   
        "mdmParametersPredictions": [

            {
                "id": 68747,
                "keyParameter": 2,
                "keyParameterName": "INJURY/ILLNESS",
                "aiReasoning": case_sheet_data.get("Presenting Complaint", ""),
                "severity": mdm_mapping_dict_by_group[1]["severity"],
                "displayOrder": 1,
                "mdMRule": mdm_mapping_dict_by_group[1]["mdMRule"],
                "mdMRuleReason": mdm_mapping_dict_by_group[1]["mdMRuleReason"],
                "group": 1,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": chart_content_by_group[1]
            },
            {
                "keyParameter": 7,
                "keyParameterName": "RADIOLOGY/SCANNING",
                "aiReasoning": orders,
                "severity": mdm_mapping_dict_by_group[2]["severity"],
                "displayOrder": 2,
                "mdMRule": mdm_mapping_dict_by_group[2]["mdMRule"],
                "mdMRuleReason": mdm_mapping_dict_by_group[2]["mdMRuleReason"],
                "group": 2,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": chart_content_by_group[3]
            },
            {
            
                "keyParameter": 3,
                "keyParameterName": "PLAN",
                "aiReasoning": case_sheet_data.get("Plan of Care", ""),
                "severity": mdm_mapping_dict_by_group[3]["severity"],
                "displayOrder": 3,
                "mdMRule": mdm_mapping_dict_by_group[3]["mdMRule"],
                "mdMRuleReason": mdm_mapping_dict_by_group[3]["mdMRuleReason"],
                "group": 3,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": chart_content_by_group[3]
            },
            {

                "keyParameter": 13,
                "keyParameterName": "ASSESSMENT",
                "aiReasoning": case_sheet_data.get("Assessment", ""),
                "severity": 1,
                "displayOrder": 4,
                "mdMRule": [],
                "mdMRuleReason": None,
                "group": 1,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": []
            },
            {
                "keyParameter": 12,
                "keyParameterName": "PHYSICAL EXAMINATION",
                "aiReasoning": case_sheet_data.get("Physical Examination", ""),
                "severity": 1,
                "displayOrder": 5,
                "mdMRule": [],
                "mdMRuleReason": None,
                "group": 3,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": chart_content_by_group[2]
            },
            {
                "keyParameter": 10,
                "keyParameterName": "MEDICATION",
                "aiReasoning": medication_data,
                "severity": 1,
                "displayOrder": 6,
                "mdMRule": [],
                "mdMRuleReason": None,
                "group": 3,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": chart_content_by_group[6]
            },
            {
                "keyParameter": 6,
                "keyParameterName": "SCALE & PAIN TYPE",
                "aiReasoning": "",
                "severity": 1,
                "displayOrder": 9,
                "mdMRule": [],
                "mdMRuleReason": None,
                "group": 1,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": []
            },
            {
                "keyParameter": 9,
                "keyParameterName": "SURGICAL HISTORY",
                "aiReasoning": "",
                "severity": 1,
                "displayOrder": 10,
                "mdMRule": [],
                "mdMRuleReason": None,
                "group": 3,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": []
            },
            {
                "keyParameter": 11,
                "keyParameterName": "SOCIAL HISTORY",
                "aiReasoning": social_history_content,
                "severity": 1,
                "displayOrder": 7,
                "mdMRule": [],
                "mdMRuleReason": None,
                "group": 3,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": []
            },
        
            {
                "keyParameter": 8,
                "keyParameterName": "PAST MEDICAL HISTORY",
                "aiReasoning": case_sheet_data.get("Past History", ""),
                "severity": 1,
                "displayOrder": 8,
                "mdMRule": [],
                "mdMRuleReason": None,
                "group": 3,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": []
            },
            
            {
                "keyParameter": 5,
                "keyParameterName": "IMPROVEMENT PERCENTAGE",
                "aiReasoning": "Not Available",
                "severity": 1,
                "displayOrder": 11,
                "mdMRule": [],
                "mdMRuleReason": None,
                "group": 1,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": []
            },
            
            {
                "keyParameter": 1,
                "keyParameterName": "AGE & EMPLOYMENT STATUS",
                "aiReasoning": "",
                "severity": 1,
                "displayOrder": 12,
                "mdMRule": [],
                "mdMRuleReason": "",
                "group": 1,
                "value": [],
                "remarks": None,
                "dependentedParameters": [],
                "mdmParametersBlockItems": []
                
        }],
        "icdCodePredictions": restructuredIcds,
        "cptCodePredictions": cpt_codes

    }

    return response_model
