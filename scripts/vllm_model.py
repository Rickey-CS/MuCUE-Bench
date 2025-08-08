import base64
import io
from pydub import AudioSegment
import requests
from openai import APIConnectionError, OpenAI
from openai.pagination import SyncPage
from openai.types.model import Model
import json
import os
from tqdm import tqdm
from pathlib import Path
from eval_single import gen_answers
import argparse

def get_first_model(client: OpenAI) -> str:
    """
    Get the first model from the vLLM server.
    """
    try:
        models: SyncPage[Model] = client.models.list()
    except APIConnectionError as e:
        raise RuntimeError(
            "Failed to get the list of models from the vLLM server at "
            f"{client.base_url} with API key {client.api_key}. Check\n"
            "1. the server is running\n"
            "2. the server URL is correct\n"
            "3. the API key is correct"
        ) from e

    if len(models.data) == 0:
        raise RuntimeError(f"No models found on the vLLM server at {client.base_url}")

    return models.data[0].id
from vllm.utils import FlexibleArgumentParser

openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

def encode_audio(audio_path, time_seg=None, output_format='wav'):
    audio = AudioSegment.from_file(audio_path)
    
    if time_seg is not None:
        start_time, end_time = time_seg
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)
        audio = audio[start_ms:end_ms]
    
    if output_format is None:
        format = audio_path.split('.')[-1].lower()
    else:
        format = output_format.lower()
    
    buffer = io.BytesIO()
    audio.export(buffer, format=format)
    
    buffer.seek(0)
    base64_audio = base64.b64encode(buffer.read()).decode('utf-8')
    
    return {'data': base64_audio, 'format': format}

def request_alm(prompt, audio_path, time_seg=None):
    chat_completion_from_base64 = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "input_audio",
                        "input_audio": encode_audio(audio_path, time_seg),
                    },
                ],
            }
        ],
        model=model,
        max_completion_tokens=64,
        temperature=0.0
    )

    result = chat_completion_from_base64.choices[0].message.content
    return result

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate a single model on all datasets.")
    parser.add_argument("--model", type=str, required=True, help="model name you prefer")
    return parser.parse_args()

def main():
    args = parse_args()
    model_name=args.model
    
    model=get_first_model(client)
    print("Using model: ", model)
    
    gen_answers(model_name, request_alm)
        
if __name__ == "__main__":
    main()
