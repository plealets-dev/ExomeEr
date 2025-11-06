
from app.services.medicalCoding.utils.EM.problem_of_complexity import get_complexity_addressed_main

from app.services.medicalCoding.utils.EM.test_anlyzed import get_mdm_level_for_radiology
from app.services.medicalCoding.utils.EM.risk import get_mdm_level_for_risk_factor
from app.services.medicalCoding.utils.EM.utils.patameter_content_by_group import parameter_content_by_group_main


def E_and_M_main(openai_client, casesheet_data):
    mdm_mapping_dict_by_group = {
            1: {
                "mdMRule": [],
                "mdMRuleReason": "",
                "severity": 2
            },

            2: {
                "mdMRule": [],
                "mdMRuleReason": "",
                "severity": 1

            },

            3: {
                "mdMRule": [],
                "mdMRuleReason": "",
                "severity": 2
            }
            
        }
    
    
    if casesheet_data:

        complaint=casesheet_data.get("Presenting Complaint", ""),
        hpi = casesheet_data.get("History of Present Illness", ""),
        assessment=casesheet_data.get('Assessment', ''),
        plan=casesheet_data.get('Plan of Care', '')

        if complaint or hpi or assessment or plan:
            # problem of complexity 
            # casesheet_str_data = json_to_excel(casesheet_data)
            problem_context =  "Presenting Complaint: {complaint}\n" \
                        "History Of illness: {hpi}\n" \
                        "Assessment: {assessment}\n" \
                        "Plan: {plan}".format(
                                            complaint=casesheet_data.get("Presenting Complaint", ""),
                                            hpi = casesheet_data.get("History of Present Illness", ""),
                                            assessment=casesheet_data.get('Assessment', ''),
                                            plan=casesheet_data.get('Plan of Care', ''))

            
            
            
            MdmSeverityLevel, mdm_rule, reason, llm_response_injury =  get_complexity_addressed_main(openai_client , problem_context)
            mdm_mapping_dict_by_group[1]["severity"] = MdmSeverityLevel
            mdm_mapping_dict_by_group[1]["mdMRule"] = [mdm_rule]
            mdm_mapping_dict_by_group[1]["mdMRuleReason"] = reason


        


        order_context = casesheet_data.get("Orders", "")                                           
        

        if order_context:

            # Data Analyzed
            context =  "Orders: {orders}\n" \
                                "Assessment: {assessment}\n" \
                                "Plan: {plan}".format(
                                                        orders=casesheet_data.get("Orders", ""),
                                                        assessment=casesheet_data.get('Assessment', ''),
                                                        plan=casesheet_data.get('Plan of Care', ''))
            MdmSeverityLevel, mdm_rule, reason, llm_radiology,flag_sum =  get_mdm_level_for_radiology(context,order_context)
            mdm_mapping_dict_by_group[2]["severity"] = MdmSeverityLevel
            mdm_mapping_dict_by_group[2]["mdMRule"] = mdm_rule
            mdm_mapping_dict_by_group[2]["mdMRuleReason"] = reason

        # Extract parameters from casesheet_data
        prescription = casesheet_data.get("Prescription", "")
        assessment = casesheet_data.get("Assessment", "")
        plan_of_care = casesheet_data.get("Plan of Care", "")

        # Check if all are null or empty
        if prescription or assessment or plan_of_care:
        # Risk Factor
            context_for_risk_factor =  "Prescription: {Prescription}\n" \
                                "Assessment: {assessment}\n" \
                                "Plan: {plan}".format(  Prescription = prescription,
                                                        assessment= assessment,
                                                        plan= plan_of_care)
            


            MdmSeverityLevel, mdm_rule,reason,llm_risk_factor =  get_mdm_level_for_risk_factor(openai_client, context_for_risk_factor)

            mdm_mapping_dict_by_group[3]["severity"] = MdmSeverityLevel
            mdm_mapping_dict_by_group[3]["mdMRule"] = mdm_rule
            mdm_mapping_dict_by_group[3]["mdMRuleReason"] = reason

    
    # Define list_of_levels from your data
    list_of_levels = [mdm_mapping_dict_by_group[1]["severity"],  
                    mdm_mapping_dict_by_group[2]["severity"], 
                    mdm_mapping_dict_by_group[3]["severity"]]
               
    print("list of each columns level is: ", list_of_levels)
    final_mdm_level = process_list(list_of_levels)
    print("final mdm level is: ", final_mdm_level)

    group_sheet_content = parameter_content_by_group_main(casesheet_data)
    # chart content by group

   
    return casesheet_data, mdm_mapping_dict_by_group, group_sheet_content, final_mdm_level





def json_to_excel(data):
    result = []
    for key,value in data.items():
        result.append(f"{key}:\n{value}\n")
    return "\n".join(result)




def process_list(input_list):
    # Sort the list in ascending order
    sorted_list = sorted(input_list)
    
    # Check if the first two elements are the same
    if sorted_list[0] == sorted_list[1]:
        return sorted_list[0]  # Return the element
        
    # If not, return the second least element
    return sorted_list[1]
