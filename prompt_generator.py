import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import random

def generate_prompt():
    # Load the .env file
    load_dotenv()

    # Use the API key from the environment
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant that generates a single, diverse, human-like instruction for language models. Each time you're prompted, create one unique instruction that mimics how people typically interact with AI."},
        ],
        temperature=1,
    )

    return completion.choices[0].message.content

# Example usage
if __name__ == "__main__":
    generated_prompt = generate_prompt()
    print(generated_prompt)


    def load_instructions_from_json(file_path):
        with open(file_path, 'r') as file:
        return json.load(file)

def generate_instruction(data):
    # Flatten the list, handling both single objects and arrays
    all_instructions = []
    for item in data:
        if isinstance(item, list):
            all_instructions.extend(item)
        else:
            all_instructions.append(item)
    
    # Choose a random element from the flattened list
    element = random.choice(all_instructions)
    
    rule = element['rule']
    instruction = element['instruction']
    kwargs = element['kwargs']
    
    # Process the kwargs and replace placeholders in the instruction
    for key, value in kwargs.items():
        if isinstance(value, list):
            if key == "keywords" and isinstance(value[0], list):
                # Handle the special case for keywords:existence
                chosen_value = random.choice(value)
                kwargs[key] = chosen_value
                placeholder = f"{{{key}}}"
                instruction = instruction.replace(placeholder, ", ".join(chosen_value))
            else:
                chosen_value = random.choice(value)
                kwargs[key] = chosen_value
                placeholder = f"{{{key}}}"
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