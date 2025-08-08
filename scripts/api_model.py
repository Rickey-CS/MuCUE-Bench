import json
import time
from tqdm import tqdm
import os
import base64
import argparse
from openai import OpenAI
from vllm_model import encode_audio
from eval_single import gen_answers

API_KEY=os.environ['GEMINI_API_KEY']
base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
client = OpenAI(
    api_key=API_KEY,
    base_url= base_url 
)


def request_alm(prompt, audio_path, time_seg=None):
    response = client.chat.completions.create(
        model= "gemini-2.0-flash",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "input_audio",
                        "input_audio": encode_audio(audio_path, time_seg),
                    }
                ],
            }
        ],
    )
    return response.choices[0].message.content

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate a single model on all datasets.")
    parser.add_argument("--model", type=str, required=True, help="model name you prefer")
    return parser.parse_args()

def main():
    args = parse_args()
    model_name=args.model
    
    gen_answers(model_name, request_alm)
        
if __name__ == "__main__":
    main()
