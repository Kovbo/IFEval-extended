import json
import sys
import os

def transform_jsonl(input_file):
    # Generate output file name
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_dataset.jsonl"

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Parse the input JSON
            input_data = json.loads(line.strip())
            
            # Create the new format
            output_data = {
                "messages": [
                    {
                        "role": "system",
                        "content": input_data["prompt"]
                    },
                    {
                        "role": "assistant",
                        "content": input_data["response"]
                    }
                ],
                "tools": []
            }
            
            # Write the transformed JSON to the output file
            json.dump(output_data, outfile)
            outfile.write('\n')  # Add newline after each JSON object

    return output_file

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file_path>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = transform_jsonl(input_file)
    print(f"Transformation complete. Output written to {output_file}")