# IFEvalExtended: Instruction Following Eval Extended

Extended version of IFEval with outogenerated instructions and prompts.

## Dependencies

Please make sure that all required python packages are installed via:

```
pip3 install -r requirements.txt
```

## How to generate instructions and prompts

```bash
python3 generator.py --num_runs 500 --max_instructions 3
```

## How to run

You need to create a jsonl file with two entries: prompt and response.
Then, call `evaluation_main` from the parent folder of
instruction_following_eval. For example:

```bash
# Content of `--input_response_data` should be like:
# {"prompt": "Write a 300+ word summary ...", "response": "PUT YOUR MODEL RESPONSE HERE"}
# {"prompt": "I am planning a trip to ...", "response": "PUT YOUR MODEL RESPONSE HERE"}
# ...
python3 -m evaluation_main \
  --input_data=./data/input_llama_3_8b.jsonl \
  --input_response_data=./data/input_response_llama_3_8b.jsonl \
  --output_dir=./data/
```
