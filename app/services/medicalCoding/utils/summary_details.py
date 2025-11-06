

def summary_details(mdm_final, icd_list, cpt_list):

    icd_restructured_list = []
    display_order = 0
    for each in icd_list:
        values = {}
        values["key"] = each.get("code", "")
        values["description"] = [f"{each.get('description', '')} with confident of {each.get('confident', '')}"]
        values["displayOrder"] = display_order
        icd_restructured_list.append(values)
        display_order += 1

    cpt_restructured_list = []
    display_order = 0
    for each in cpt_list:
        values = {}
        values["key"] = each.get("cptCode", "")
        values["description"] = [each.get('description', '')]
        values["displayOrder"] = display_order
        cpt_restructured_list.append(values)
        display_order += 1



    summaryDetails =  [
            {
                "prediction": "ICD",
                "predictedValue": icd_restructured_list
            },
            {
                "prediction": "E&M",
                "predictedValue": [
                    {
                        "key": f"9921{mdm_final}",
                        "description": [],
                        "displayOrder": None
                    }
                ]
            }
           
        ]
    
    if cpt_list:
        summaryDetails.append({
                "prediction": "Other CPT/ HCPC",
                "predictedValue": cpt_restructured_list
            })
    
    return summaryDetails