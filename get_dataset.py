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
                prompt="Please generate five similar questions with step by step reasoning process and an integer answer in the following form Q1:{question}\n S1:{solution}\n A1:{answer}\n\n Q2:{question}\n S2:{solution}\n A2:{answer}\n\n Q3:{question}\n S3:{solution}\n A3:{answer}\n\n Q4:{question}\n S4:{solution}\n A4:{answer}\n\n Q5:{question}\n S5:{solution}\n A5:{answer}\n\n."
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
                for idx in range(0,1319):
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
                prompt="Follwing the above question, generate five similar multiple choice science questions with its choice labels, choice text and an answer label in the following form [[Question1:{question}\n Label1:[choice labels]\n Text1:[choice text]\n Ans1:{answer label}]]\n\n [[Question2:{question}\n Label2:[choice labels]\n Text2:[choice text]\n Ans2:{answer label}]]\n\n [[Question3:{question}\n Label3:[choice labels]\n Text3:[choice text]\n Ans3:{answer label}]]\n\n [[Question4:{question}\n Label4:[choice labels]\n Text4:[choice text]\n Ans4:{answer label}]]\n\n [[Question5:{question}\n Label5:[choice labels]\n Text5:[choice text]\n Ans5:{answer label}]]\n\n."
                sys_prompt="You are a helpful assistant that answer multiple choice science questions."
            elif scenario=="cot":
                prompt="Follwing the above question, generate five similar multiple choice science questions with its choice labels, choice text, the explanation of the right answer and an answer label in the following form [[Question1:{question}\n Label1:[choice labels]\n Text1:[choice text]\n Sol1:{the explanation of the right answer}\n Ans1:{answer label}]]\n\n [[Question2:{question}\n Label2:[choice labels]\n Text2:[choice text]\n Sol2:{the explanation of the right answer}\n Ans2:{answer label}]]\n\n [[Question3:{question}\n Label3:[choice labels]\n Text3:[choice text]\n Sol3:{the explanation of the right answer}\n Ans3:{answer label}]]\n\n [[Question4:{question}\n Label4:[choice labels]\n Text4:[choice text]\n Sol4:{the explanation of the right answer}\n Ans4:{answer label}]]\n\n [[Question5:{question}\n Label5:[choice labels]\n Text5:[choice text]\n Sol5:{the explanation of the right answer}\n Ans5:{answer label}]]\n\n  [[Question6:{question}\n Label6:[choice labels]\n Text6:[choice text]\n Sol6:{the explanation of the right answer}\n Ans6:{answer label}]]\n\n [[Question7:{question}\n Label7:[choice labels]\n Text7:[choice text]\n Sol7:{the explanation of the right answer}\n Ans7:{answer label}]]\n\n [[Question8:{question}\n Label8:[choice labels]\n Text8:[choice text]\n Sol8:{the explanation of the right answer}\n Ans8:{answer label}]]\n\n [[Question9:{question}\n Label9:[choice labels]\n Text9:[choice text]\n Sol9:{the explanation of the right answer}\n Ans9:{answer label}]]\n\n [[Question10:{question}\n Label10:[choice labels]\n Text10:[choice text]\n Sol10:{the explanation of the right answer}\n Ans10:{answer label}]]\n\n."
                sys_prompt="You are a helpful assistant that generate few-shot multiple choice science question examples."
            else:
                raise NotImplementedError


            # generate the demonstration
            for idx in range(0,1172):
                sentence=dataset[idx]["prompt"]
                demonstration=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": "Q: {{"+sentence+"}} "+prompt+"\n"}]
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
                prompt="\nPlease follwing the above question, generate five similar questions with its answer in Latex. Please output in the following form [[Question1:{question}\n Answer1:$answer in Latex$]]\n\n [[Question2:{question}\n Answer2:$answer in Latex$]]\n\n [[Question3:{question}\n Answer3:$answer in Latex$]]\n\n [[Question4:{question}\n Answer4:$answer in Latex$]]\n\n [[Question5:{question}\n Answer5:$answer in Latex$]]\n\n."
                sys_prompt="Given a mathematics problem, generate several similar questions along with answer in Latex. Simplify the answer as much as possible."
            elif scenario=="cot":
                prompt="\nPlease follwing the above question, generate 5 similar questions with its step by step solution and answer in Latex. Please output in the following form [[Question1:{question}\n Sol1:[step by step solution]\n Answer1:$answer in Latex$]]\n\n [[Question2:{question}\n Sol2:[step by step solution]\n Answer2:$answer in Latex$]]\n\n [[Question3:{question}\n Sol3:[step by step solution]\n Answer3:$answer in Latex$]]\n\n [[Question4:{question}\n Sol4:[step by step solution]\n Answer4:$answer in Latex$]]\n\n [[Question5:{question}\n Sol5:[step by step solution]\n Answer5:$answer in Latex$]]\n\n."
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
                for idx in range(5000):
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
                prompt="Please follwing the above question, create five similar multiple choice {} questions with its choice labels, choice text and an answer label (A or B or C or D). Note that each question should be complete and can be answered independently. Please output in the following form [[Question1:[question]\n Label1:[choice labels]\n Text1:[choice text]\n Ans1:[A or B or C or D]]]\n\n [[Question2:[question]\n Label2:[choice labels]\n Text2:[choice text]\n Ans2:[A or B or C or D]]]\n\n [[Question3:[question]\n Label3:[choice labels]\n Text3:[choice text]\n Ans3:[A or B or C or D]]]\n\n [[Question4:[question]\n Label4:[choice labels]\n Text4:[choice text]\n Ans4:[A or B or C or D]]]\n\n [[Question5:[question]\n Label5:[choice labels]\n Text5:[choice text]\n Ans5:[A or B or C or D]]]\n\n."
                sys_prompt="You are a helpful assistant that generate few-shot multiple choice {} question examples."
            elif scenario=="cot":
                prompt="Follwing the above question, generate five similar multiple choice {} questions with its choice labels, choice text, the step by step reason to choose your answer and an answer label (A or B or C or D). Note that each question should be complete and can be answered independently. Please output in the following form [[Question1:[question]\n Label1:[choice labels]\n Text1:[choice text]\n Sol1:[reason to choose your answer]\n Ans1:[A or B or C or D]]]\n\n [[Question2:[question]\n Label2:[choice labels]\n Text2:[choice text]\n Sol2:[reason to choose your answer]\n Ans2:[A or B or C or D]]]\n\n [[Question3:[question]\n Label3:[choice labels]\n Text3:[choice text]\n Sol3:[reason to choose your answer]\n Ans3:[A or B or C or D]]]\n\n [[Question4:[question]\n Label4:[choice labels]\n Text4:[choice text]\n Sol4:[reason to choose your answer]\n Ans4:[A or B or C or D]]]\n\n [[Question5:[question]\n Label5:[choice labels]\n Text5:[choice text]\n Sol5:[reason to choose your answer]\n Ans5:[A or B or C or D]]]\n\n."
                sys_prompt="You are a helpful assistant that generate few-shot multiple choice {} question examples."
            else:
                raise NotImplementedError
            # generate the demonstration
            for idx in range(13985):
                sentence=dataset[idx]["prompt"]
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
                for idx in range(13985):
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
                prompt='请模仿上面的问题，生成5个相似的关于{}考试的单项选择题，和这个这个题目的选项标签，选项内容和答案。每个问题必须是完整且能被独立回答的。请以以下格式输出答案：[[题目1:[题目]\n 选项标签1:[选项标签]\n 选项内容1:[选项内容]\n 答案1:[A或B或C或D]]]\n\n [[题目2:[题目]\n 选项标签2:[选项标签]\n 选项内容2:[选项内容]\n 答案2:[A或B或C或D]]]\n\n [[题目3:[题目]\n 选项标签3:[选项标签]\n 选项内容3:[选项内容]\n 答案3:[A或B或C或D]]]\n\n [[题目4:[题目]\n 选项标签4:[选项标签]\n 选项内容4:[选项内容]\n 答案4:[A或B或C或D]]]\n\n [[题目5:[题目]\n 选项标签5:[选项标签]\n 选项内容5:[选项内容]\n 答案5:[A或B或C或D]]]。'
                sys_prompt="以下是中国关于{}考试的单项选择题，请仿照这个题目生成一些类似的题目和标准答案。"
            elif scenario=="cot":
                prompt='请模仿上面的问题，生成5个相似的关于{}考试的单项选择题，和这个这个题目的选项标签，选项内容，逐步的推导出答案的过程和正确答案。每个问题必须是完整且能被独立回答的。请以以下格式输出答案：[[题目1:[题目]\n 选项标签1:[选项标签]\n 选项内容1:[选项内容]\n 解析1：[逐步的推导出答案的过程]\n 答案1:[A或B或C或D]]]\n\n [[题目2:[题目]\n 选项标签2:[选项标签]\n 选项内容2:[选项内容]\n 解析2：[逐步的推导出答案的过程]\n 答案2:[A或B或C或D]]]\n\n [[题目3:[题目]\n 选项标签3:[选项标签]\n 选项内容3:[选项内容]\n 解析3：[逐步的推导出答案的过程]\n 答案3:[A或B或C或D]]]\n\n [[题目4:[题目]\n 选项标签4:[选项标签]\n 选项内容4:[选项内容]\n 解析4：[逐步的推导出答案的过程]\n 答案4:[A或B或C或D]]]\n\n [[题目5:[题目]\n 选项标签5:[选项标签]\n 选项内容5:[选项内容]\n 解析5：[逐步的推导出答案的过程]\n 答案5:[A或B或C或D]]]。'
                sys_prompt="以下是中国关于{}考试的单项选择题，请模仿这个题目生成一些类似的题目和它的解析与答案。"
            else:
                raise NotImplementedError
            # generate the demonstration
            for idx in range(12342):
                sentence=dataset[idx]["prompt"]
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
                prompt="[[Function Body]]: {implementation of the function}]\n\nFollowing the example, generate 5 similar function headers with its function body in python. Please output in the following form: [[[Function Heaser1]]:\n [[Function Body1]]: ]\n\n [[[Function Heaser2]]:\n [[Function Body2]]: ]\n\n [[[Function Heaser3]]:\n [[Function Body3]]: ]\n\n [[[Function Heaser4]]:\n [[Function Body4]]: ]\n\n [[[Function Heaser5]]:\n [[Function Body5]]: ]\n\n."
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
                for idx in range(164):
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