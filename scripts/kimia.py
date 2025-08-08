import soundfile as sf
from kimia_infer.api.kimia import KimiAudio
import base64
import io
from pydub import AudioSegment
import json
import os
from tqdm import tqdm
from vllm_model import encode_audio
from eval_single import gen_answers
import argparse

# --- 1. Load Model ---
model_path = "moonshotai/Kimi-Audio-7B-Instruct" 
model = KimiAudio(model_path=model_path, load_detokenizer=False)

sampling_params = {
    "audio_temperature": 0.8,
    "audio_top_k": 10,
    "text_temperature": 0.0,
    "text_top_k": 5,
    "audio_repetition_penalty": 1.0,
    "audio_repetition_window_size": 64,
    "text_repetition_penalty": 1.0,
    "text_repetition_window_size": 16,
    "max_new_tokens": 64
}

model_name='Kimi-Audio-7B-Instruct'

def decode_audio(encoded_result, output_path=None):
    audio_data = base64.b64decode(encoded_result['data'])
    format = encoded_result['format']
    
    if output_path is None:
        output_path = f"decoded_audio.{format}"
    else:
        if not output_path.endswith(f".{format}"):
            output_path = f"{output_path}.{format}"
    
    with open(output_path, 'wb') as f:
        f.write(audio_data)
    
    return output_path

def request_alm(prompt, audio_path, time_seg=None):
    messages_asr = [
    # You can provide context or instructions as text
    {"role": "user", "message_type": "text", "content": prompt},
    # Provide the audio file path
    {"role": "user", "message_type": "audio", "content": decode_audio(encode_audio(audio_path, time_seg))}
    ]
    # Generate only text output
    _, text_output = model.generate(messages_asr, **sampling_params, output_type="text")
    
    return text_output


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