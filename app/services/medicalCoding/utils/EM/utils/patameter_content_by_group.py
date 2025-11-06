



from app.api.utils.json_to_text import json_to_text



def parameter_content_by_group_main(casesheet_data):
    # custom_group    
    groups={
    1: {"ParameterName": "INJURY/ILLNESS", "ChartBlocks": ["Presenting Complaint", "Assessment", "Plan of Care"]},
    2: {"ParameterName": "PHYSICAL EXAMINATION",  "ChartBlocks": ['Physical Examination']},
    3: {"ParameterName": "RADIOLOGY/SCANNING", "ChartBlocks": ["Plan of Care", 'Assessment','Orders']},
    4: {"ParameterName": "SURGICAL HISTORY", "ChartBlocks" : ["Past History"]},
    5: {"ParameterName": "PAST MEDICAL HISTORY",  "ChartBlocks": ["Past History"]},
    6: {"ParameterName": "MEDICATION", "ChartBlocks": ["Prescription", "Current Medication"]},
    7: {"ParameterName": "SOCIAL HISTORY", "ChartBlocks" : ["Social History"]}}
   


   
    group_sheet_content = {
          
            1 : [],
            2: [],
            3: [],
            4 : [],
            5: [],
            6: [],
            7 : []
        }
    

    for key, value in groups.items():
        for each_key in value["ChartBlocks"]:
            if each_key == "Orders" or  each_key == "Prescription":
                if each_key == "Orders":

                    str_data = json_to_text(casesheet_data.get(each_key, ""), keyname = "orderName")
                elif each_key == "Prescription":
                    str_data = json_to_text(casesheet_data.get(each_key, ""), keyname = "medication")


                mdm_block = {"BlockName":each_key,"BlockContent":str_data,"highlightWords":[]}
            else:
                mdm_block = {"BlockName":each_key,"BlockContent":casesheet_data.get(each_key, ""),"highlightWords":[]}
            
            group_sheet_content[key].append(mdm_block)
            
            


   

                       
    return group_sheet_content