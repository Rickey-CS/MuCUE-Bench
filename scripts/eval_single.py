import json
import argparse
from tqdm import tqdm
import subprocess
import os
from pathlib import Path
from datasets import load_dataset
import datasets

ds_revision = "2fd45ed1f7d462da22f1dce1018d6599d3696d68"
ins = 'Choose the correct option for the question based on the audio. '

def gen_answers(model_name, request_alm, data_names=None, save_every=-1):
    ds = load_dataset("Yi3852/MuCUE", revision=ds_revision, trust_remote_code=True).cast_column("audio", datasets.Audio(decode=False))
    if data_names is None:
        data_names=list(ds.keys())
        # data_names=['mmau_music','gs_key_30s',]
    
    os.makedirs('./outputs', exist_ok=True)
    for data_name in data_names[:]:
        print(f"Generating answers for {data_name}")
        save_path='./outputs/{}_{}.json'.format(model_name, data_name)
        if os.path.exists(save_path):
            with open(save_path,'r') as f:
                test_data = json.load(f)
        else:
            test_data = list(ds[data_name])
        try:
            for i in tqdm(range(len(test_data))):
                item = test_data[i]
                if 'raw_response' in item:
                    continue
                prompt = ins + item['question'] + ' ' + item['choices_text']
                result = request_alm(prompt, item['audio']['path'], item['time_seg'] if item['time_seg'] else None)
                item['raw_response'] = result
                if (save_every > 0) and ((i+1) % save_every == 0):
                    with open(save_path, 'w') as f:
                        json.dump(test_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(e)
            print(item)
            with open(save_path, 'w') as f:
                json.dump(test_data, f, indent=4, ensure_ascii=False)
            continue
        with open(save_path, 'w') as f:
            json.dump(test_data, f, indent=4, ensure_ascii=False)

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate a single JSON file.")
    parser.add_argument("--data", type=str, required=True, help="Path to the JSON file to evaluate")
    return parser.parse_args()

def main():
    args = parse_args()
    
    with open(args.data, 'r') as file:
            data = json.load(file)
    
    qusetion_num = 0
    correct_num = 0
    for item in data:
        if "pred_choice" in item: 
            qusetion_num += 1
            if item["pred_choice"] == item["correct_choice"]:
                correct_num += 1
    
    print(f"Correct/Total: {correct_num}/{qusetion_num}")
    print(f"Accuracy: {correct_num / qusetion_num:.2%}")
        
if __name__ == "__main__":
    main()