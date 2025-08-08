import json
import argparse
from openai import OpenAI
from tqdm import tqdm

openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8008/v1"

extract_prompt = """
extract the choice of A, B, C, D from the following answer.
If the answer is not clear, return "None", otherwise just return the single choice letter.
options: {}\n answer: \n{}\n
"""
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

def request_llm(userContent, model="Qwen/Qwen3-8B"):
    chat_response = client.chat.completions.create(
    model="Qwen/Qwen3-8B",
    messages=[
        {"role": "user", "content": userContent},
    ],
    max_tokens=32,
    temperature=0.1,
    
    extra_body={
        "chat_template_kwargs": {"enable_thinking": False},
    },
)
    return chat_response.choices[0].message.content

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate a single JSON file.")
    parser.add_argument("--data", type=str, required=True, help="Path to the JSON file to evaluate")
    return parser.parse_args()

def main():
    args = parse_args()
    
    with open(args.data, 'r') as file:
            test_data = json.load(file)
    for item in tqdm(test_data[:]):
        if "pred_choice" in item and (item["pred_choice"].strip() ):
            continue
        if 'raw_response' in item and item['raw_response'].strip():
            res=request_llm(extract_prompt.format(item['choices_text'], item['raw_response']))
            item["pred_choice"] = res
    
    with open(args.data,'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=4)
          
if __name__ == "__main__":
    main()