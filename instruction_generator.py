import json
import random
import os

def load_instructions_from_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def generate_instruction(data):
    # Flatten the list, handling both single objects and arrays
    all_instructions = []
    for item in data:
        all_instructions.extend(item) if isinstance(item, list) else all_instructions.append(item)
    
    # Choose a random element from the flattened list
    element = random.choice(all_instructions)
    
    rule = element['rule']
    instruction = element['instruction']
    kwargs = element['kwargs']
    
    # Process the kwargs and replace placeholders in the instruction
    for key, value in kwargs.items():
        if isinstance(value, list):
            chosen_value = random.choice(value)
            kwargs[key] = chosen_value
            placeholder = f"{{{key}}}"

            if key == "keywords" and isinstance(value[0], list):
                # Handle the special case for keywords:existence
                instruction = instruction.replace(placeholder, ", ".join(chosen_value))
            else:
                # Convert list to string without brackets
                if isinstance(chosen_value, list):
                    chosen_value_str = ", ".join(map(str, chosen_value))
                else:
                    chosen_value_str = str(chosen_value)
                instruction = instruction.replace(placeholder, chosen_value_str)
    
    return {
        "rule": rule,
        "instruction": instruction,
        "kwargs": kwargs
    }


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the instructions.json file
instructions_file_path = os.path.join(script_dir, 'data', 'instructions.json')

# Load the data from the JSON file
data = load_instructions_from_json(instructions_file_path)

# Generate and print the instruction
result = generate_instruction(data)
print(json.dumps(result, indent=2))
