
from app.services.medicalCoding.utils.EM.em_main import E_and_M_main
from app.services.medicalCoding.utils.EM.utils.restructureModel import restructureData
from app.services.medicalCoding.utils.OtherCPT.other_cpt_main import search_cpt_description
from app.services.medicalCoding.utils.ICDCodes.icd_code_main import icd_code_main
from app.services.medicalCoding.utils.summary_details import summary_details

def medical_coding_main(openaiclient, case_sheet_data):
    
    # # TODO 
    # response_model = mdmParametersPredictions(response_model, case_sheet_data)
    casesheet_data, mdm_mapping_dict_by_group, group_sheet_content, final_mdm_level = E_and_M_main(openaiclient, case_sheet_data)
    icd_code_list, restructuredIcds, len_of_icd, icd_comma_seperated_string = icd_code_main(openaiclient, case_sheet_data)
    other_cpt_codes = search_cpt_description(case_sheet_data, len_of_icd, icd_comma_seperated_string)
    
    response_model = restructureData(casesheet_data, mdm_mapping_dict_by_group, group_sheet_content, final_mdm_level, restructuredIcds, other_cpt_codes, icd_comma_seperated_string)
    summary_data = summary_details(final_mdm_level, icd_code_list, other_cpt_codes)
    response_model["summaryDetails"] = summary_data
    return response_model
