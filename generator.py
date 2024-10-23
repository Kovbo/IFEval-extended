import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
import json
import random
from datetime import datetime

def generate_prompt():
    load_dotenv()
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI assistant that generates a single, diverse, human-like instruction for language models. Each time you're prompted, create one unique instruction that mimics how people typically interact with AI."},
        ],
        temperature=1,
    )

    return completion.choices[0].message.content

def load_instructions_from_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def generate_instruction(data, prompt):
    all_instructions = []
    for item in data:
        if isinstance(item, list):
            all_instructions.extend(item)
        else:
            all_instructions.append(item)
    
    element = random.choice(all_instructions)
    
    rule = element['rule']
    instruction = element['instruction']
    kwargs = element.get('kwargs', {})
    singe = element.get('singe', False)
    exclude = element.get('exclude', [])
    
    for key, value in kwargs.items():
        if isinstance(value, list):
            if key == "keywords" and isinstance(value[0], list):
                chosen_value = random.choice(value)
                kwargs[key] = chosen_value
                placeholder = f"{{{key}}}"
                instruction = instruction.replace(placeholder, ", ".join(chosen_value))
            else:
                chosen_value = random.choice(value)
                kwargs[key] = chosen_value
                placeholder = f"{{{key}}}"
                if isinstance(chosen_value, list):
                    chosen_value_str = ", ".join(map(str, chosen_value))
                else:
                    chosen_value_str = str(chosen_value)
                instruction = instruction.replace(placeholder, chosen_value_str)
    
    # Add prompt_to_repeat to kwargs if the rule is "combination:repeat_prompt"
    if rule == "combination:repeat_prompt":
        kwargs["prompt_to_repeat"] = prompt
    
    return {
        "rule": rule,
        "instruction": instruction,
        "kwargs": kwargs,
        "singe": singe,
        "exclude": exclude
    }

def combine_prompt_and_instructions(prompt, instructions):
    combined = prompt

    for instruction in instructions:
        # Replace placeholders in the instruction with actual values
        for key, value in instruction['kwargs'].items():
            if key != "prompt_to_repeat":  # Skip prompt_to_repeat
                placeholder = f"{{{key}}}"
                if isinstance(value, list):
                    replacement = ", ".join(map(str, value))
                else:
                    replacement = str(value)
                instruction['instruction'] = instruction['instruction'].replace(placeholder, replacement)
        
        # Add the instruction to the combined prompt
        combined += f"\n\n{instruction['instruction']}"
    
    return combined

def write_to_jsonl(data, file_path):
    with open(file_path, 'a') as file:
        json.dump(data, file)
        file.write('\n')

def generate_unique_instructions(data, num_instructions, prompt):
    instructions = []
    used_rules = set()

    while len(instructions) < num_instructions and len(used_rules) < len(data):
        instruction = generate_instruction(data, prompt)
        if instruction['rule'] not in used_rules:
            if instruction['singe']:
                return [instruction]
            
            # Check if this instruction excludes any previously selected instructions
            instructions = [instr for instr in instructions if instr['rule'] not in instruction['exclude']]
            
            instructions.append(instruction)
            used_rules.add(instruction['rule'])
            
            # Check if any previously selected instruction excludes this one
            for prev_instruction in instructions[:-1]:
                if instruction['rule'] in prev_instruction['exclude']:
                    instructions.pop()
                    used_rules.remove(instruction['rule'])
                    break

    return instructions

def get_model_response(prompt):
    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    return completion.choices[0].message.content

def main(num_runs, max_instructions):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    instructions_file_path = os.path.join(script_dir, 'instructions.json')
    data = load_instructions_from_json(instructions_file_path)

    # Generate the output file names with the current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    input_file_path = os.path.join(script_dir, f'input_{current_date}.jsonl')
    input_response_file_path = os.path.join(script_dir, f'input_response_{current_date}.jsonl')

    for _ in range(num_runs):
        prompt = generate_prompt()
        
        num_instructions = min(random.randint(1, max_instructions), len(data))
        instructions = generate_unique_instructions(data, num_instructions, prompt)
        
        combined_prompt = combine_prompt_and_instructions(prompt, instructions)

        output = {
            "key": random.randint(1000, 9999),
            "prompt": combined_prompt,
            "instruction_id_list": [instruction["rule"] for instruction in instructions],
            "kwargs": [instruction["kwargs"] for instruction in instructions]
        }

        # Write the output to the JSONL file
        write_to_jsonl(output, input_file_path)

        # Generate model response
        response = get_model_response(combined_prompt)

        # Create response output
        response_output = {
            "prompt": combined_prompt,
            "response": response
        }

        # Write the response output to the new JSONL file
        write_to_jsonl(response_output, input_response_file_path)

    print(f"{num_runs} outputs written to {input_file_path}")
    print(f"{num_runs} response outputs written to {input_response_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate prompts with instructions and model responses")
    parser.add_argument("-n", "--num_runs", type=int, default=1, help="Number of outputs to generate")
    parser.add_argument("-m", "--max_instructions", type=int, default=3, help="Maximum number of random instructions per output")
    args = parser.parse_args()

    main(args.num_runs, args.max_instructions)