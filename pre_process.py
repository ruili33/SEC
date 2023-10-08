import json
import os
import re
from datasets import load_dataset
from tqdm import tqdm
from utils import subcategories,categories,ceval_input_dict
def arc():
    dataset = load_dataset("ai2_arc","ARC-Challenge")
    test_data=dataset["test"]
    result=[]
    for i in range(test_data.num_rows):
        prompt=dataset["test"][i]["question"]
        choice=dataset["test"][i]["choices"]
        choice_text=choice['text']
        choice_lab=choice['label']
        assert choice_lab==['A','B','C','D'] or  choice_lab==['1','2','3','4'] or  choice_lab==['A','B','C'] or  choice_lab==['1','2','3'] or  choice_lab==['A','B','C','D','E']
        for j in range(len(choice_text)):
            prompt+="\n{}. {}".format(choice_lab[j], choice_text[j])
        prompt_question="Question: "+dataset["test"][i]["question"]
        prompt_question+="\n Label:"+str(choice_lab)+"\n Text:"+str(choice_text) 

        result.append({
            'idx':i,
            "prompt":prompt,
			'prompt_question':prompt_question,
            "question":dataset["test"][i]["question"]
        })
    filename=f"arc.json"
    with open(os.path.join('.','data',filename),"w") as file:
        json.dump(result, file, ensure_ascii=False, indent=2) 
def math_data():
    def remove_boxed(s):
        left = "\\boxed{"
        try:
            assert s[:len(left)] == left
            assert s[-1] == "}"
            return s[len(left):-1]
        except:
            return None
    def last_boxed_only_string(string):
        idx = string.rfind("\\boxed")
        if idx < 0:
            idx = string.rfind("\\fbox")
            if idx < 0:
                return None

        i = idx
        right_brace_idx = None
        num_left_braces_open = 0
        while i < len(string):
            if string[i] == "{":
                num_left_braces_open += 1
            if string[i] == "}":
                num_left_braces_open -= 1
                if num_left_braces_open == 0:
                    right_brace_idx = i
                    break
            i += 1
        
        if right_brace_idx == None:
            retval = None
        else:
            retval = string[idx:right_brace_idx + 1]
        
        return retval
    fnames_list=[]
    out=[]
    idx=0
    dataset='math'
    rootdir = os.path.join('.','dataset','MATH','test') 
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            fnames_list.append(os.path.join(subdir, file))
            with open(os.path.join(subdir, file), 'r') as fp:
                try:
                    problem_data = json.load(fp)
                except Exception as e:
                    print(f"Error loading JSON from {file}", e)
                    continue
            prob_level = problem_data["level"]
            prob_type = problem_data["type"]
            try:
                prob_level = int(prob_level.split("Level ")[1])
            except:
                prob_level = None
            problem_data['prob_level']=prob_level
            problem_data['idx']=idx
            answer = remove_boxed(last_boxed_only_string(problem_data["solution"]))
            problem_data['answer']=answer
            problem_data['prompt']=problem_data['problem']
            out.append(problem_data)
            idx+=1
    assert len(out)==5000
    output_path=os.path.join('.','data','math.json') 
    with open(output_path,"w") as file:
        json.dump(out, file, ensure_ascii=False, indent=2) 

def mmlu_dataset():
    #https://github.com/hendrycks/test/blob/master/categories.py

    out=[]
    label=['A','B','C','D']
    idx=0
    for i in tqdm(subcategories.keys()):
        dataset = load_dataset("lukaemon/mmlu",i)
        test_data=dataset["test"]
        for j in tqdm(range(test_data.num_rows)):
            choice=[test_data[j]['A'],test_data[j]['B'],test_data[j]['C'],test_data[j]['D']]
            prompt=test_data[j]['input']
            for l in range(len(label)):
                prompt+="\n{}. {}".format(label[l], choice[l])
                
            prompt_question="Question: "+test_data[j]['input']
            prompt_question+="\n Label:"+str(label)+"\n Text:"+str(choice) 
            out.append({
                'idx':idx,
                'tuple':(test_data[j]['input'],label,choice,test_data[j]['target']),
                'prompt':prompt,
                'class':i,
                'subcat':subcategories[i],
				'prompt_question':prompt_question
            })
            idx+=1
    output_path=os.path.join('.','data','mmlu.json') 
    with open(output_path,"w") as file:
        json.dump(out, file, ensure_ascii=False, indent=2) 

def ceval():
    
    out=[]
    label=['A','B','C','D']
    idx=0
    for i in tqdm(ceval_input_dict.keys()):
        dataset = load_dataset("ceval/ceval-exam",i)
        test_data=dataset["test"]
        for j in tqdm(range(int(test_data.num_rows))):
            choice=[test_data[j]['A'],test_data[j]['B'],test_data[j]['C'],test_data[j]['D']]
            prompt="题目:"+test_data[j]['question']+""
            for l in range(len(label)):
                prompt+="\n{}. {}".format(label[l], choice[l])
            prompt_question="题目:"+test_data[j]['question']
            prompt_question+="\n选项标签:"+str(label)+"\n选项内容:"+str(choice) 
            out.append({
                'idx':idx,
                'tuple':(test_data[j]['question'],label,choice,test_data[j]['answer']),
                'prompt':prompt,
                'class':i,
                'subcat':ceval_input_dict[i][2],
                'chinese_class':ceval_input_dict[i][1],
				'prompt_question':prompt_question
            })
            idx+=1
    output_path=os.path.join('.','data','ceval.json') 
    with open(output_path,"w") as file:
        json.dump(out, file, ensure_ascii=False, indent=2) 


def humaneval():
    data_path= os.path.join('.','dataset','human-eval','data','HumanEval.jsonl') 
    json_list=[]
    with open(data_path, "rb") as file:
        for line in file:
            json_obj = json.loads(line)
            json_list.append(json_obj)
    out=[]
    for i in range(len(json_list)):
        out.append({
            'idx':i,
            'id':json_list[i]['task_id'],
            'prompt':json_list[i]['prompt']
        })
    output_path=os.path.join('.','data','humaneval.json') 
    with open(output_path,"w") as file:
        json.dump(out, file, ensure_ascii=False, indent=2) 