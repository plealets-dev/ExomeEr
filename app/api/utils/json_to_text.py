# Function to convert JSON to text
def json_to_text(data, keyname = False):
    if data:

        result = []
        for each in data:
            if isinstance(each, dict):

                if keyname:
                    value = each.get(keyname, "")
                    result.append(f"{keyname}:\n{value}\n")
                    continue

                else:
                    
                    for key, value in each.items():
                        result.append(f"{key}:\n{value}\n")
            
        if result:
            return "\n".join(result)
    else:
        return ""
    return ""

# Convert JSON to text
# text_output = json_to_text(json_data)