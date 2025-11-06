import re

def parse_diagnosis(diagnosis_str):
    """Extract diagnosis conditions and percentages from a formatted string."""
    pattern = r'([A-Za-z\s\(\)]+)\s\((\d+)%\)'
    diagnosis_matches = re.findall(pattern, diagnosis_str)
    return [{"condition": condition.strip(), "percentage": percentage} for condition, percentage in diagnosis_matches]


def compare_diagnosis(current_diagnosis_str, previous_diagnosis_str):
    current_diagnosis = parse_diagnosis(current_diagnosis_str)
    previous_diagnosis = parse_diagnosis(previous_diagnosis_str)

    # Convert conditions to lowercase for case-insensitive comparison
    current_diag_dict = {item['condition'].lower(): item['percentage'] for item in current_diagnosis}
    previous_diag_dict = {item['condition'].lower(): item['percentage'] for item in previous_diagnosis}

    # Check for new or changed diagnosis
    updated_diagnosis = []
    for condition, percentage in current_diag_dict.items():
        if condition not in previous_diag_dict:
            # Use the original case-sensitive condition for the output
            updated_diagnosis.append(f"{next(item['condition'] for item in current_diagnosis if item['condition'].lower() == condition)} ({percentage}%)")
        elif previous_diag_dict[condition] != percentage:
            updated_diagnosis.append(f"{next(item['condition'] for item in current_diagnosis if item['condition'].lower() == condition)} ({percentage}%)")

    # Check for removed diagnosis
    # for condition in previous_diag_dict:
    #     if condition not in current_diag_dict:
    #         updated_diagnosis.append(f"{next(item['condition'] for item in previous_diagnosis if item['condition'].lower() == condition)} (0%)")

    return ",".join(updated_diagnosis) if updated_diagnosis else ""



def compare_questions(current_question_str, previous_question_str):
    # Split and strip the questions into lists
    current_questions_list = current_question_str.split(",")
    previous_questions_list = previous_question_str.split(",")

    # Create a set of lowercase previous questions for faster lookup
    previous_questions_set = {question.strip().lower() for question in previous_questions_list}
    
    # Find new questions by checking against the set
    new_questions = [question.strip() for question in current_questions_list 
                     if question.strip().lower() not in previous_questions_set]
    
    # Return the new questions in their original format
    return ",".join(new_questions) if new_questions else ""


def compare_symptoms(current_symptoms_str, previous_symptoms_str):
    # Split and normalize the current symptoms into a list
    current_symptoms_list = [symptom.strip() for symptom in current_symptoms_str.split(",")]

    # Normalize the previous symptoms: split by both commas and newlines, then strip
    previous_symptoms_list = [
        symptom.strip() 
        for symptom in str(previous_symptoms_str).replace("\n", ",").split(",") 
        if symptom.strip()
    ]

    # Create a set of lowercase previous symptoms for faster lookup
    previous_symptoms_set = {symptom.lower() for symptom in previous_symptoms_list}
    # print("previous_symptoms_set:", previous_symptoms_set)

    # Find new symptoms by checking against the set
    new_symptoms = [
        symptom for symptom in current_symptoms_list 
        if symptom.lower() not in previous_symptoms_set
    ]

    # Combine new symptoms into a single string, if any
    return ",".join(new_symptoms) if new_symptoms else ""
   