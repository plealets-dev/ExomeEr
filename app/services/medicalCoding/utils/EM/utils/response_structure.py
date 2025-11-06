response_model = {

    
    "icdCodePredictions": [
        {
    
            "pointer": "A",
            "icdCode": "S60.122D",
            "icdDesc": "Contusion of left index finger with damage to nail, subsequent encounter",
            "predictedAccuracy": 100,
            "isManual": None,
            "displayOrder": 0,
            "icdCodePointers": [],
            "icdCodeExamples": []
        }
    ],
    "cptCodePredictions": [
        {

            "codeType": "E&M",
            "cptCode": "99213",
            "description": "",
            "modifier": "25",
            "unit": 1,
            "pointer": "A",
            "icdCodes": "S60.122D",
            "predictedAccuracy": None,
            "isManual": None,
            "displayOrder": None,
            "comment": None,
            "cptCodePointers": [],
            "cptCodeExamples": []
        },
        {
    
            "codeType": "Other-CPT",
            "cptCode": "90714",
            "description": "Tetanus and diptheria toxoids adsorbed(Td),presrvative free,when administered to individuals 7 years or older for intramuscular use",
            "modifier": "",
            "unit": 1,
            "pointer": "A",
            "icdCodes": "S60.122D",
            "predictedAccuracy": None,
            "isManual": None,
            "displayOrder": None,
            "comment": "Tetanus Vaccine",
            "cptCodePointers": [
                {
                    "detail": "Tetanus Vaccine"
                }
            ],
            "cptCodeExamples": []
        },
        {

            "codeType": "Other-CPT",
            "cptCode": "90471",
            "description": "Immunization administration(includes percutaneous intradermal,subcutaneous,or intramuscular injections);1 vaccine(single or combination vaccine/toxoid)",
            "modifier": "",
            "unit": 1,
            "pointer": "A",
            "icdCodes": "S60.122D",
            "predictedAccuracy": None,
            "isManual": None,
            "displayOrder": None,
            "comment": "Tetanus Vaccine",
            "cptCodePointers": [
                {
    
                    "detail": "Tetanus Vaccine"
                }
            ],
            "cptCodeExamples": []
        }
    ],

    "summaryDetails": [
        {
            "prediction": "ICD",
            "predictedValue": [
                {
                    "key": "S60.122D",
                    "description": [],
                    "displayOrder": 0
                }
            ]
        },
        {
            "prediction": "E&M",
            "predictedValue": [
                {
                    "key": "99213",
                    "description": [],
                    "displayOrder": None
                }
            ]
        },
        {
            "prediction": "CPT",
            "predictedValue": [
                {
                    "key": "90714",
                    "description": [
                        "Tetanus Vaccine"
                    ],
                    "displayOrder": None
                },
                {
                    "key": "90471",
                    "description": [
                        "Tetanus Vaccine"
                    ],
                    "displayOrder": None
                },

            ]
        }
    ],
"mdmParametersPredictions": [

    {
        "id": 68747,
        "keyParameter": 2,
        "keyParameterName": "INJURY/ILLNESS",
        "aiReasoning": "pt. will get tetatnus\n Reason: Tetanus vaccine",
        "severity": 3,
        "displayOrder": 1,
        "mdMRule": [
            "1 Stable Chronic Illness"
        ],
        "mdMRuleReason": "discharged present in chart ",
        "group": 1,
        "value": [],
        "remarks": None,
        "dependentedParameters": [],
        "mdmParametersBlockItems": [
            {
            
                "blockName": "History of Present Illness",
                "blockContent": "\npatient is a 29 year old male.\n11/9/24 - pt. here for initial visit for smashed his left finger. pt. is a mechanic and was working with metal pipes,\nwhen one of them fell on his finger. he states that he is having pain of 8-9/10, denies numbness/tingling/electric\nshock. he denies prior injuries or health conditions or bleeding disorder. pt. states he only took 1 paracetamol\nyesterday.\n11/12/24 pain and pressure not helped w meds notes last tetanus ~4 yrs ago. tolerating meds and mod duty\ndenies ssi f/c dc\nxray neg , reviewed images today w/o note of none abnormality\n11/16/24 f/u encounter for contusion of finger nail, left index finger neg for fx. procedure trephination /pressure\nreleased fron nail serosanguinous drainage.\ntoday - states the nail is stable, not moving or does not think is coming out. pt. states that he did not get\nantibiotic as pharmacy closed, re-prescribed to preferred pharmacy. some swelling and pain on bending finger,\notherwise denies any other concerns. pt. notes itching, prescribed antibiotic cream. pt. managing normal duty.\n11/22/24\ntoday - pt. will get tetatnus. pt. has been using antibiotic cream and medications, helping him. pt. is managing\nwork. pt. does not need medicine refill. pt. is ready to be discharged.\npast medical history\nno known past medical history\nsurgical history\nno known surgical history\nallergy\nno known drug allergies.\nvaldivia velasquez, luis armando dob:09-14-1995\n",
                "highlightWords": [
                    "tetatnus",
                    "pt",
                    "tetanus",
                    "get"
                ]
            },
            {
        
                "blockName": "Assessment",
                "blockContent": "F/u encounter for contusion of finger nail, left index finger neg for Fx , \nprocedure trephination /pressure released fron nail serosanguinous drainage gave relief , PE  nail w instability may be partially detatched \nConservative measures with prophylaxis antibiotic expected to resolve the condition\nCondition resolved. \nPt. Discharged today",
                "highlightWords": [
                    "pt"
                ]
            },
            {

                "blockName": "Plan",
                "blockContent": "Tetanus injection\nDischarge to full duty",
                "highlightWords": [
                    "tetanus"
                ]
            }
        ]
    },
    {
        "keyParameter": 7,
        "keyParameterName": "RADIOLOGY/SCANNING",
        "aiReasoning": "Orders: valdivia velasquez, luis armando dob:09-14-1995\n*tetanus vaccine\ntests:\ncompleted: yes.",
        "severity": 1,
        "displayOrder": 2,
        "mdMRule": [],
        "mdMRuleReason": "",
        "group": 2,
        "value": [],
        "remarks": None,
        "dependentedParameters": [],
        "mdmParametersBlockItems": []
    },
    {
       
        "keyParameter": 3,
        "keyParameterName": "PLAN",
        "aiReasoning": "Plan: Tetanus injection\nDischarge to full duty",
        "severity": 3,
        "displayOrder": 3,
        "mdMRule": [
            "Low risk of morbidity from additional diagnostic testing or treatment"
        ],
        "mdMRuleReason": "The patient's condition has been resolved with conservative measures and a prophylaxis antibiotic. No additional diagnostic testing or treatment is required. The patient is discharged to full duty and no surgery or hospitalization is planned.",
        "group": 3,
        "value": [],
        "remarks": None,
        "dependentedParameters": [],
        "mdmParametersBlockItems": []
    },
    {

        "keyParameter": 13,
        "keyParameterName": "ASSESSMENT",
        "aiReasoning": "Assessment: F/u encounter for contusion of finger nail, left index finger neg for Fx , \nprocedure trephination /pressure released fron nail serosanguinous drainage gave relief , PE  nail w instability may be partially detatched \nConservative measures with prophylaxis antibiotic expected to resolve the condition\nCondition resolved. \nPt. Discharged today",
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
        "aiReasoning": "Left nail /cuticles swollen w pressure, Blue deformity, no swelling, no ecchymosis, or any open wounds",
        "severity": 1,
        "displayOrder": 5,
        "mdMRule": [],
        "mdMRuleReason": None,
        "group": 3,
        "value": [],
        "remarks": None,
        "dependentedParameters": [],
        "mdmParametersBlockItems": [
            {
                "id": 43632,
                "mdmPredictionId": 68756,
                "blockName": "Physical Examination",
                "blockContent": " HAND EXAM\nA.\tLATERALITY:\t\t        Left nail /cuticles swollen w pressure\nB.\tVISUAL INSPECTION:\tBlue deformity, no swelling, no ecchymosis, or any open wounds.\nC.\tPALPATION:\t\t        No tenderness to palpation.\nD.\tACTIVE RANGE OF MOTION:\n        DIGITS 2-5\n               MCP FLEXION \t0 to 90 degrees\n               MCP EXTENSION\t0 degrees\n               MCP ABDUCTION\t0 to 25 degrees\n               MCP ADDUCTION\t0 to 20 degrees\n               PIP FLEXION     \t0 to 100 degrees\n               PIP EXTENSION   \t0 degrees\n               DIP FLEXION   \t0 to 70 degrees\n               DIP EXTENSION \t0 degrees\n         THUMB\n               MCP FLEXION  \t0 to 60 degrees\n               MCP EXTENSION \t0 degrees\n               MCP ABDUCTION\t0 to 50 degrees\n               MCP ADDUCTION\t0 to 8 centimeters\n               IP FLEXION\t\t0 to 80 degrees\n               IP EXTENSION\t0 degrees\nE.\tNEUROVASCULAR:\t5/5 motor strength, no sensory deficit to light touch, and brisk capillary refill less than 2 seconds throughout the hand.\nG.\tCONTRALATERAL SIDE: Exam is normal.",
                "highlightWords": [
                    "swelling",
                    "pressure",
                    "cuticles",
                    "blue",
                    "ecchymosis",
                    "left",
                    "wounds",
                    "deformity",
                    "open",
                    "nail",
                    "swollen"
                ]
            }
        ]
    },
    {
        "keyParameter": 10,
        "keyParameterName": "MEDICATION",
        "aiReasoning": "Prescription: \nN/A \n Current Medication:\n bacitracin 500 unit/gram topical ointment 1 gram twice a day, tylenol 8 hour 650 mg tablet,extended release 1 tablet every 8 hours prn",
        "severity": 1,
        "displayOrder": 6,
        "mdMRule": [],
        "mdMRuleReason": None,
        "group": 3,
        "value": [],
        "remarks": None,
        "dependentedParameters": [],
        "mdmParametersBlockItems": [
            {
                "id": 43631,
                "mdmPredictionId": 68754,
                "blockName": "Current Medication",
                "blockContent": "\nbacitracin 500 unit/gram topical ointment 1 gram twice a day\ntylenol 8 hour 650 mg tablet,extended release 1 tablet every 8 hours prn\n",
                "highlightWords": [
                    "every",
                    "bacitracin",
                    "extended",
                    "hour",
                    "ointment",
                    "twice",
                    "unitgram",
                    "gram",
                    "day",
                    "hours",
                    "topical",
                    "tylenol",
                    "tablet",
                    "prn",
                    "release",
                    "mg"
                ]
            }
        ]
    },
    {
        "keyParameter": 6,
        "keyParameterName": "SCALE & PAIN TYPE",
        "aiReasoning": "",
        "severity": 1,
        "displayOrder": 7,
        "mdMRule": [],
        "mdMRuleReason": None,
        "group": 1,
        "value": [],
        "remarks": None,
        "dependentedParameters": [],
        "mdmParametersBlockItems": [
            {
    
                "blockName": "Vitals",
                "blockContent": "Pain scale was 0 out of 10.\n \nCalculated Height (inches):\n 0 inches. \n \nTemperature:\n 98.70 F. \n \nPulse:\n 77 per min.\n Pulse rhythm regular: Yes \n \nRespiration:\n 10 breaths per min. \n BMI: aN. \n \nBP Systolic:\n 142 mm Hg. \n \nBP Diastolic:\n 80 mmHg. ",
                "highlightWords": [
                    "pain",
                    "scale"
                ]
            }
        ]
    },
    {
        "keyParameter": 9,
        "keyParameterName": "SURGICAL HISTORY",
        "aiReasoning": "",
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
        "keyParameter": 11,
        "keyParameterName": "SOCIAL HISTORY",
        "aiReasoning": "Work History: \nMaintenance .\nUse of Drugs/Alcohol/Tobacco: \nNever drinks any alcohol.  Smoking Status (MU) never smoker.  Does not drink caffeinated beverages.  He has never used any illicit drugs.  He denies using street drugs with a needle.",
        "severity": 1,
        "displayOrder": 9,
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
        "aiReasoning": "\nno known past medical history\n",
        "severity": 1,
        "displayOrder": 10,
        "mdMRule": [],
        "mdMRuleReason": None,
        "group": 3,
        "value": [],
        "remarks": None,
        "dependentedParameters": [],
        "mdmParametersBlockItems": []
    }]        
}
