from datasets import load_dataset
import os
import json
import pre_process
from get_demonetration_generation_prompt import get_demonstration_generation_prompt
def get_dataset(dataset_name,mode='test',scenario='van',k=0,tries=0):
    total_demonstration=[]
    if dataset_name=='GSM8k':
        dataset = load_dataset("gsm8k","main")
        if mode=='gen':

            # prompt
            if scenario=='van':
                prompt=get_demonstration_generation_prompt(dataset_name,mode,scenario,k,tries)
                sys_prompt="You are a helpful assistant that generate few-shot examples."        
            elif scenario=="cot":
                prompt=get_demonstration_generation_prompt(dataset_name,mode,scenario,k,tries)
                sys_prompt="You are a helpful assistant that generate few-shot examples." 
            else:
                raise NotImplementedError
            
            # generate the demonstration
            for idx in range(0,1319):
                sentence=dataset["test"][idx]["question"]
                demonstration=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": "Q: {{"+sentence+"}} "+prompt+"\n"}]
                total_demonstration.append({"idx":idx,"prompt":demonstration})
            return total_demonstration
        elif mode=='test':
            if scenario=='van':
                filename='gsm_van_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 
                prompt=""
                sys_prompt="You are a helpful assistant that solve the problem."
                for idx in range(0,1319):
                    sentence=dataset["test"][idx]["question"]
                    demonstration=[
                    {"role": "system", "content": sys_prompt}]
                    assert demonstration_input_all is not None
                    demonstration_input=demonstration_input_all[idx] 
                    for i in range(k):
                        demonstration+=[{"role":"user","content":"Question: "+demonstration_input["few_shot"][i][0]+""+prompt+"\n"},
                                    {"role":"assistant","content":"\nThe answer is "+str(demonstration_input["few_shot"][i][1])+".\n"}]
                    demonstration+=[{"role": "user", "content": "Question: "+sentence+""+prompt+"\n"}]
                    total_demonstration.append({"idx":idx,"prompt":demonstration})
                return total_demonstration
            elif scenario=="cot":
                filename='gsm_cot_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 
                prompt=""
                sys_prompt="You are a helpful assistant that solve the problem."
                for idx in range(0,10):
                    sentence=dataset["test"][idx]["question"]
                    demonstration=[
                    {"role": "system", "content": sys_prompt}]
                    assert demonstration_input_all is not None
                    demonstration_input=demonstration_input_all[idx] 
                    for i in range(k):
                        demonstration+=[{"role":"user","content":"Question: "+demonstration_input["few_shot"][i][0]+""+prompt+"\n"},
                                    {"role":"assistant","content":"Solution: "+demonstration_input["few_shot"][i][1]+"\nThe answer is "+str(demonstration_input["few_shot"][i][2])+".\n"}]
                    demonstration+=[{"role": "user", "content": "Question: "+sentence+""+prompt+"\n"}]
                    total_demonstration.append({"idx":idx,"prompt":demonstration})
                return total_demonstration
            else:
                raise NotImplementedError
            



    if dataset_name=='ARC':
        filename='arc.json'
        if not os.path.exists(os.path.join('.','data',filename)):
            pre_process.arc()
        assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
        with open(os.path.join('.','data',filename)) as input_file:
            dataset=json.load(input_file)
        if mode=='gen':

            #prompt
            if scenario=='van':
                prompt=get_demonstration_generation_prompt(dataset_name,mode,scenario,k,tries)
                sys_prompt="You are a helpful assistant that answer multiple choice science questions."
            elif scenario=="cot":
                prompt=get_demonstration_generation_prompt(dataset_name,mode,scenario,k,tries)
                sys_prompt="You are a helpful assistant that generate few-shot multiple choice science question examples."
            else:
                raise NotImplementedError


            # generate the demonstration
            for idx in range(0,1172):
                sentence=dataset[idx]["prompt_question"]
                demonstration=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": sentence+prompt+"\n"}]
                total_demonstration.append({"idx":idx,"prompt":demonstration})
            return total_demonstration
        if mode=='test':
            if scenario=='van':
                filename='arc_van_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 

                prompt="You are a helpful assistant that answer multiple choice science questions."
                sys_prompt="Please choose the correct answer among multiple choices."
                for idx in range(1172):
                    sentence=dataset[idx]["prompt"]
                    demonstration=[
                    {"role": "system", "content":sys_prompt}]
                    assert demonstration_input_all is not None
                    demonstration_input=demonstration_input_all[idx] 
                    for i in range(k):
                        demonstration+=[{"role":"user","content":"Q: {{"+demonstration_input["few_shot"]["prompt"][i]+"}}"+prompt+"\n"},
                                    {"role":"assistant","content":"Answer:"+demonstration_input["few_shot"]["list"][i][3]}]
                    demonstration+=[{"role": "user", "content": "Q: {{"+sentence+"}} "+prompt+"\n"}]
                    total_demonstration.append({"idx":idx,"prompt":demonstration})
                return total_demonstration
            elif scenario=="cot":
                filename='arc_cot_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 
                prompt="You are a helpful assistant that answer multiple choice science questions."
                sys_prompt="Please choose the correct answer among multiple choices."
                for idx in range(1172):
                    sentence=dataset[idx]["prompt"]
                    demonstration=[
                    {"role": "system", "content":sys_prompt}]
                    assert demonstration_input_all is not None
                    demonstration_input=demonstration_input_all[idx] 
                    for i in range(k):
                        demonstration+=[{"role":"user","content":"Q: {{"+demonstration_input["few_shot"]["prompt"][i]+"}}"+prompt+"\n"},
                            {"role":"assistant","content":"Solution: "+demonstration_input["few_shot"]["list"][i][3]+" Answer: "+demonstration_input["few_shot"]["list"][i][4]}]
                    demonstration+=[{"role": "user", "content": "Q: {{"+sentence+"}} "+prompt+"\n"}]
                    total_demonstration.append({"idx":idx,"prompt":demonstration})
                return total_demonstration
            else:
                raise NotImplementedError






    if dataset_name=='MATH':
        filename='math.json'
        if not os.path.exists(os.path.join('.','data',filename)):
            pre_process.math_data()
        assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
        with open(os.path.join('.','data',filename)) as input_file:
            dataset=json.load(input_file)
        if mode=='gen':
            #prompt
            if scenario=='van':
                prompt=get_demonstration_generation_prompt(dataset_name,mode,scenario,k,tries)
                sys_prompt="Given a mathematics problem, generate several similar questions along with answer in Latex. Simplify the answer as much as possible."
            elif scenario=="cot":
                prompt=get_demonstration_generation_prompt(dataset_name,mode,scenario,k,tries)
                sys_prompt="Given a mathematics problem, generate several similar questions along with its step by step solution and answer in Latex. Simplify the answer as much as possible."
            else:
                raise NotImplementedError
            
            # generate the demonstration
            for idx in range(5000):
                sentence=dataset[idx]["prompt"]
                demonstration=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content":"Question: "+sentence+""+prompt+"\n"}]
                total_demonstration.append({"idx":idx,"prompt":demonstration})

            return total_demonstration
        if mode=='test':
            if scenario=='van':
                filename='math_van_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 
                prompt=""
                sys_prompt="Given a mathematics problem, determine the answer. Simplify your answer as much as possible. Please answer in the form Answer: $your answer$."
                for idx in range(5000):
                    sentence=dataset[idx]["prompt"]
                    demonstration=[{"role": "system", "content":sys_prompt}]
                    assert demonstration_input_all is not None
                    demonstration_input=demonstration_input_all[idx] 
                    for i in range(k):
                        demonstration+=[{"role":"user","content":"Question: "+demonstration_input["few_shot"]["prompt"][i]+""+prompt+"\n"},
                                    {"role":"assistant","content":"Answer: "+demonstration_input["few_shot"]["Ans"][i]}]
                    demonstration+=[{"role": "user", "content":"Question: "+sentence+""+prompt+"\n"}]
                    total_demonstration.append({"idx":idx,"prompt":demonstration})

                return total_demonstration
            elif scenario=="cot":
                filename='math_cot_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 
                prompt=""
                sys_prompt="Given a mathematics problem, determine the answer. Simplify your answer as much as possible. Please answer in the form Answer: $your answer$."
                for idx in range(10):
                    sentence=dataset[idx]["prompt"]
                    demonstration=[{"role": "system", "content":sys_prompt}]
                    assert demonstration_input_all is not None
                    demonstration_input=demonstration_input_all[idx] 
                    for i in range(k):
                        demonstration+=[{"role":"user","content":"Question: "+demonstration_input["few_shot"]["prompt"][i]+""+prompt+"\n"},
                            {"role":"assistant","content":"Solution: Let's think step by step. "+demonstration_input["few_shot"]["list"][i][1]+" Answer: "+demonstration_input["few_shot"]["Ans"][i]}]
                    demonstration+=[{"role": "user", "content": "Question: "+sentence+""+prompt+"\n"}]
                    total_demonstration.append({"idx":idx,"prompt":demonstration})
                return total_demonstration
            else:
                raise NotImplementedError
            




    if dataset_name=='MMLU':
        filename='mmlu.json'
        if not os.path.exists(os.path.join('.','data',filename)):
            pre_process.mmlu_dataset()
        assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
        with open(os.path.join('.','data',filename)) as input_file:
            dataset=json.load(input_file)
        if mode=='gen':
            #prompt
            if scenario=='van':
                prompt=get_demonstration_generation_prompt(dataset_name,mode,scenario,k,tries)
                sys_prompt="You are a helpful assistant that generate few-shot multiple choice {} question examples."
            elif scenario=="cot":
                prompt=get_demonstration_generation_prompt(dataset_name,mode,scenario,k,tries)
                sys_prompt="You are a helpful assistant that generate few-shot multiple choice {} question examples."
            else:
                raise NotImplementedError
            # generate the demonstration
            for idx in range(13985):
                sentence=dataset[idx]["prompt_question"]
                demonstration=[
                    {"role": "system", "content": sys_prompt.format(dataset[idx]['class'])},
                    {"role": "user", "content":sentence+'\n'+prompt.format(dataset[idx]['class'])+"\n"}]
                total_demonstration.append({"idx":idx,"prompt":demonstration})
            return total_demonstration
        if mode=='test':
            if scenario=='van':
                filename='mmlu_van_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 
                prompt=""
                sys_prompt="You are a helpful assistant that answer multiple choice {} questions."
                for idx in range(13985):
                    sentence=dataset[idx]["prompt"]
                    demonstration=[
                    {"role": "system", "content":sys_prompt.format(dataset[idx]['class'])}]
                    assert demonstration_input_all is not None
                    demonstration_input=demonstration_input_all[idx] 
                    for i in range(k):
                        demonstration+=[{"role":"user","content":demonstration_input["few_shot"]["prompt"][i]+'\n'+prompt.format(dataset[idx]['class'])+"\n"},
                                    {"role":"assistant","content":"Answer:"+demonstration_input["few_shot"]["Ans"][i]}]
                    demonstration+=[{"role": "user", "content": sentence+'\n'+prompt.format(dataset[idx]['class'])+"\n"}]
                    total_demonstration.append({"idx":idx,"prompt":demonstration})
                return total_demonstration
            elif scenario=="cot":
                filename='mmlu_cot_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 
                prompt=""
                sys_prompt="You are a helpful assistant that answer multiple choice {} questions."
                for idx in range(10):
                    sentence=dataset[idx]["prompt"]
                    demonstration=[
                    {"role": "system", "content":sys_prompt.format(dataset[idx]['class'])}]
                    assert demonstration_input_all is not None
                    demonstration_input=demonstration_input_all[idx] 
                    for i in range(k):
                            demonstration+=[{"role":"user","content":"Q: {{"+demonstration_input["few_shot"]["prompt"][i]+"}}"+prompt+"\n"},
                                    {"role":"assistant","content":"Solution: "+demonstration_input["few_shot"]["list"][i][3]+" Answer: "+demonstration_input["few_shot"]["list"][i][4]}]
                    demonstration+=[{"role": "user", "content": "Q: {{"+sentence+"}} "+prompt+"\n"}]
                    total_demonstration.append({"idx":idx,"prompt":demonstration})
                return total_demonstration
            else:
                raise NotImplementedError

    
    
    if dataset_name=='Ceval':
        filename='ceval.json'
        if not os.path.exists(os.path.join('.','data',filename)):
            pre_process.ceval()
        assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
        with open(os.path.join('.','data',filename)) as input_file:
            dataset=json.load(input_file)
        if mode=='gen':
            #prompt
            if scenario=='van':
                prompt=get_demonstration_generation_prompt(dataset_name,mode,scenario,k,tries)
                sys_prompt="以下是中国关于{}考试的单项选择题，请仿照这个题目生成一些类似的题目和标准答案。"
            elif scenario=="cot":
                prompt=get_demonstration_generation_prompt(dataset_name,mode,scenario,k,tries)
                sys_prompt="以下是中国关于{}考试的单项选择题，请模仿这个题目生成一些类似的题目和它的解析与答案。"
            else:
                raise NotImplementedError
            # generate the demonstration
            for idx in range(12342):
                sentence=dataset[idx]["prompt_question"]
                demonstration=[
                {"role": "system", "content": sys_prompt.format(dataset[idx]['chinese_class'])},
                {"role": "user", "content":sentence+'\n'+prompt.format(dataset[idx]['chinese_class'])+"\n"}]
                total_demonstration.append({"idx":idx,"prompt":demonstration})
            return total_demonstration
        if mode=='test':
            if scenario=='van':
                filename='ceval_van_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 
                prompt=""
                sys_prompt="以下是中国关于{}考试的单项选择题，请选出其中的正确答案。"
                for idx in range(12342):
                    sentence=dataset[idx]["prompt"]
                    demonstration=[
                    {"role": "system", "content":sys_prompt.format(dataset[idx]['chinese_class'])}]
                    assert demonstration_input_all is not None
                    demonstration_input=demonstration_input_all[idx] 
                    for i in range(k):
                        demonstration+=[{"role":"user","content":demonstration_input["few_shot"]["prompt"][i]+'\n'+prompt.format(dataset[idx]['class'])+"\n"},
                                    {"role":"assistant","content":"答案："+demonstration_input["few_shot"]["Ans"][i]}]
                    demonstration+=[{"role": "user", "content": sentence+'\n'+prompt.format(dataset[idx]['chinese_class'])+"\n"}]
                    total_demonstration.append({"idx":idx,"prompt":demonstration})
                return total_demonstration
            elif scenario=="cot":
                filename='ceval_cot_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 
                prompt=""
                sys_prompt="以下是中国关于{}考试的单项选择题，请选出其中的正确答案。"
                for idx in range(12342):
                    sentence=dataset[idx]["prompt"]
                    demonstration=[
                    {"role": "system", "content":sys_prompt.format(dataset[idx]['chinese_class'])}]
                    assert demonstration_input_all is not None
                    demonstration_input=demonstration_input_all[idx] 
                    for i in range(k):
                        demonstration+=[{"role":"user","content":demonstration_input["few_shot"]["prompt"][i]+'\n'+prompt.format(dataset[idx]['class'])+"\n"},
                            {"role":"assistant","content":"解析: "+demonstration_input["few_shot"]["list"][i][3]+" 答案："+demonstration_input["few_shot"]["Ans"][i]}]
                    demonstration+=[{"role": "user", "content": sentence+'\n'+prompt.format(dataset[idx]['chinese_class'])+"\n"}]
        
                    total_demonstration.append({"idx":idx,"prompt":demonstration})
                return total_demonstration
            else:
                raise NotImplementedError










    if dataset_name=='HumanEval':
        filename='humaneval.json'
        if not os.path.exists(os.path.join('.','data',filename)):
            pre_process.humaneval()
        assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
        with open(os.path.join('.','data',filename)) as input_file:
            dataset=json.load(input_file)
        if mode=='gen':
            #prompt
            if scenario=='van':
                prompt=get_demonstration_generation_prompt(dataset_name,mode,scenario,k,tries)
                sys_prompt='You are an expert coder in Python. Following the example, generate some python function headers and function bodies. The function header defines the basic information about the function. The function body contains the actual Python implementation of the function.'
                front_promt="[[[Function Header]]: "
            elif scenario=="cot":
                raise NotImplementedError
            else:
                raise NotImplementedError
            # generate the demonstration
            for idx in range(164):
                sentence=dataset[idx]["prompt"]
                demonstration=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content":front_promt+sentence+prompt}]
                total_demonstration.append({"idx":idx,"prompt":demonstration})
            return total_demonstration
        if mode=='test':
            if scenario=='van':
                filename='humaneval_van_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 
                prompt=""
                sys_prompt=""
                for idx in range(10):
                    sentence=dataset[idx]["prompt"]
                    demonstration=[
                    {"role": "system", "content":sys_prompt}]
                    assert demonstration_input_all is not None
                    demonstration_input=demonstration_input_all[idx] 
                    for i in range(k):
                        demonstration+=[{"role":"user","content":demonstration_input["few_shot"]["prom"][i]+'\n'+prompt+"\n"},
                                    {"role":"assistant","content":demonstration_input["few_shot"]["Ans"][i]}]
                    demonstration+=[{"role": "user", "content": sentence+'\n'+prompt+"\n"}]
                    total_demonstration.append({"idx":idx,"prompt":demonstration})
                return total_demonstration
            elif scenario=="cot":
                raise NotImplementedError
            else:
                raise NotImplementedError