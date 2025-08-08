import json
import argparse
from tqdm import tqdm
import subprocess
import os
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from eval_single import gen_answers

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate a single model on all datasets.")
    parser.add_argument("--model", type=str, required=True, help="model name you prefer")
    return parser.parse_args()

def main():
    args = parse_args()
    model_name=args.model
    
    hf_path = 'Yi3852/MuFun-Base'
    tokenizer = AutoTokenizer.from_pretrained(hf_path, use_fast=False)
    device='cuda'
    model = AutoModelForCausalLM.from_pretrained(hf_path, trust_remote_code=True, torch_dtype="bfloat16")
    model.to(device)

    def request_alm(prompt, audio_path, time_seg=None):
        return model.chat(prompt=prompt, audio_files=audio_path, segs=time_seg, tokenizer=tokenizer, temperature=0.0, max_new_tokens = 64)
    
    gen_answers(model_name, request_alm)
        
if __name__ == "__main__":
    main()