import os
import re
from datasets import load_dataset
from tqdm import tqdm
import json,numpy as np
import utils
from utils_cleaning import _strip_string,normalize_final_answer,find_ans_gsm,find_ans_arc,find_ans_math,is_equiv,find_ans_mmlu,find_ans_ceval
from utils import subcategories,categories,ceval_input_dict
from human_eval.data import write_jsonl





def evaluate(dataset,mode,scenario,k):
    result=utils.automatic_concatenate_and_read(dataset,mode,scenario,k)
    if dataset=='GSM8k':
        if scenario=='van' or scenario=='cot':
            correct=0
            dataset = load_dataset("gsm8k","main")
            test_data=dataset["test"]   
            for i in tqdm(range(test_data.num_rows)):
                ans_str=dataset["test"][i]["answer"]
                cur_ans=re.findall("### -?\d+",ans_str)
                ans=int(cur_ans[0][4:])
                assert ans is not None
                assert result[i]["idx"]==i
                assert result[i]["result"]!=""
                model_ans=find_ans_gsm(result[i]["result"])
                if model_ans==ans:
                    correct+=1
            print(f'Evaluation result for dataset {dataset} mode {dataset} scenario {scenario} k {k}, Accuracy: ',correct/test_data.num_rows)
        else:
            raise NotImplementedError
    elif dataset=='ARC':
        if scenario=='van' or scenario=='cot':
            correct=0
            dataset = load_dataset("ai2_arc","ARC-Challenge")
            test_data=dataset["test"]
            for i in tqdm(range(test_data.num_rows)):
                cur_ans=dataset["test"][i]["answerKey"]
                ans=cur_ans
                assert ans is not None
                assert result[i]["idx"]==i
                assert result[i]["result"]!=""
                model_ans=find_ans_arc(result[i]["result"],dataset["test"][i]["choices"]["label"])
                if model_ans==ans:
                    correct+=1
            print(f'Evaluation result for dataset {dataset} mode {dataset} scenario {scenario} k {k}, Accuracy: ',correct/test_data.num_rows)
        else:
            raise NotImplementedError 
    
    elif dataset=='MATH':
        if scenario=='van' or scenario=='cot':
            correct=0
            filename='math.json'
            assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
            with open(os.path.join('.','data',filename)) as input_file:
                test_data=json.load(input_file)
            total=len(test_data)
            for i in tqdm(range(total)):
                ans=test_data[i]["answer"]
                assert ans is not None
                assert result[i]["idx"]==i
                assert result[i]["result"]!=""
                model_ans=find_ans_math(result[i]["result"])
                model_ans=normalize_final_answer(model_ans) if model_ans else None
                if is_equiv(model_ans,ans):
                    correct+=1
                
            print(f'Evaluation result for dataset {dataset} mode {dataset} scenario {scenario} k {k}, Accuracy: ',correct/total)

        else:
            raise NotImplementedError 


    elif dataset=='MMLU':
        if scenario=='van' or scenario=='cot':
            filename='mmlu.json'
            assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
            with open(os.path.join('.','data',filename)) as input_file:
                test_data=json.load(input_file)
            correct={}
            count={}
            for i in tqdm(range(len(test_data))):
                if test_data[i]['class'] not in correct.keys():
                    correct[test_data[i]['class']]=0
                if test_data[i]['class'] not in count.keys():
                    count[test_data[i]['class']]=0
                ans=test_data[i]['tuple'][3]
                assert ans is not None
                assert result[i]["idx"]==i
                assert result[i]["result"]!=""
                model_ans=find_ans_mmlu(result[i]["result"])
                if model_ans==ans:
                    correct[test_data[i]['class']]+=1
                count[test_data[i]['class']]+=1
            assert 13985==sum(count.values())
            out={}
            for i in correct.keys():
                out[i]=correct[i]/count[i]
            out['ave']=float(np.average(list(out.values())))

            sub_correct={}
            for i in tqdm(subcategories.keys()):
                if subcategories[i][0] not in sub_correct.keys():
                    sub_correct[subcategories[i][0]]=[]
                sub_correct[subcategories[i][0]].append(input[i])
            for i in sub_correct.keys():
                sub_correct[i]=float(np.average(list(sub_correct[i])))
            for i in categories.keys():
                sub_correct[i]=float(np.average([sub_correct[j] for j in categories[i]]))
            out.update(sub_correct)
            with open(os.path.join('.','evaluation_result',f"mmlu_{scenario}_{k}"),"w") as file:
                json.dump(out, file, ensure_ascii=False, indent=2) 
            print(out['ave'])

        else:
            raise NotImplementedError  

    elif dataset=='Ceval':
        if scenario=='van' or scenario=='cot':
            filename='ceval.json'
            assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
            with open(os.path.join('.','data',filename)) as input_file:
                test_data=json.load(input_file)
            num={}
            out={}
            for i in tqdm(ceval_input_dict.keys()):
                num[i]=0
                out[i]={}
            assert len(result)==len(test_data)
            for i in tqdm(range(len(test_data))):
                assert result[i]['idx']==i
                assert test_data[i]['idx']==i
                cur_class=input[i]['class']
                out[cur_class][f"{num[cur_class]}"]=find_ans_ceval(result[i]["result"])
                num[cur_class]+=1
            with open(os.path.join('.','evaluation_result',f"ceval_{scenario}_{k}"),"w") as file:
                json.dump(out, file, ensure_ascii=False, indent=2) 
        else:
            raise NotImplementedError  

    elif dataset=='HumanEval':
        if scenario=='van':
            filename='humaneval.json'
            assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
            with open(os.path.join('.','data',filename)) as input_file:
                test_data=json.load(input_file)
            sample_list=[]
            for i in tqdm(range(164)):
                sample_list.append({
                    "task_id":test_data[i]['id'],
                    "completion":test_data[i]['result'][0]
                })
            write_jsonl("pred/test.jsonl", sample_list)
        else:
            raise NotImplementedError  
        
