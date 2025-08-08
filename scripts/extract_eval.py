import json
import argparse
from tqdm import tqdm
import subprocess
import os
from pathlib import Path
from datasets import load_dataset
import datasets

        
def parse_args():
    parser = argparse.ArgumentParser(description="Extract answer choices and Evaluate on all datasets for a single model")
    parser.add_argument("--model", type=str, required=True, help="model name")
    return parser.parse_args()

def main():
    args = parse_args()
    model_name=args.model
    ds = load_dataset("Yi3852/MuCUE", revision="main", trust_remote_code=True).cast_column("audio", datasets.Audio(decode=False))
    data_names=list(ds.keys())
    
    for data_name in data_names:
        
        save_path='./outputs/{}_{}.json'.format(model_name, data_name)
        if os.path.exists(save_path):
            print('extracting {}...'.format(save_path))
        
            command = "python scripts/extract_single.py --data {}".format(save_path)

            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            for line in process.stdout:
                print(line, end='')  
    for data_name in data_names:
        
        save_path='./outputs/{}_{}.json'.format(model_name, data_name)
        if os.path.exists(save_path):
            print('evaluating {}...'.format(data_name))
            command = "python scripts/eval_single.py --data {}".format(save_path)

            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            for line in process.stdout:
                print(line, end='')  
        else:
            print('output file does not exist for {}.'.format(data_name))
        
if __name__ == "__main__":
    main()