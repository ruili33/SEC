import os
import re
from datasets import load_dataset
from tqdm import tqdm
import json
import utils
from utils_cleaning import process_raw,get_special_match,get_special_match_b,process_text,change,find_ans,normalize_final_answer,process_label,get_ans,process,_strip_string,gen_arc,gen_math,gen_mmlu,gen_ceval,process_humaneval

def answer_validation(results,dataset,scenario,k):
    if dataset=='GSM8k':
        if scenario=='van':
            pattern = r"Q\s?\d?:(.*?)\s?\s?S\s?\d?:(.*?)\s?\n?\s?A\s?\d?:(.*?)\s?\n"
        elif scenario=='cot':
            pattern = r"Q\s?\d?:(.*?)\s?\s?S\s?\d?:(.*?)\s?\n?\s?A\s?\d?:(.*?)\s?\n"
        else:
            raise NotImplementedError
        result=process_raw(results)
        matches = re.findall(pattern, result+"\n\n")
        if len(matches)<k:
            matches_a=get_special_match(result,pattern)
            if len(matches_a)>=k:
                matches=matches_a
            elif len(matches_a)<k:
                matches_b=get_special_match_b(result,pattern)
                if len(matches_b)>=k:
                    matches=matches_b
        try:   
            shot_list=[(process_text(i[0]),process_text(i[1]),process_text(i[2])) for i in matches]
        except:
            return False
        if len(shot_list)<k:
            return False
        return True
    


    elif dataset=='ARC':
        if scenario=='van':
            pattern = r"Question(\d*):(.*?)\s?Label(\d*):(.*?)\n?\s?Text(\d*):(.*?)\n?\s?Ans(\d*):(.*?)\n"
            result=process_raw(results)
            matches = re.findall(pattern, result+"\n\n")
            if len(matches)>k:
                matches=matches[:k]
            try:
                shot_list=[(process_text(i[1]),eval(i[3]),change(i[5]),process_text(i[7])) for i in matches]
            except:
                return False

            if len(shot_list)<k:
                return False
            return True
        elif scenario=='cot':
            pattern = r"Question(\d*):(.*?)\s?Label(\d*):(.*?)\n?\s?Text(\d*):(.*?)\n?\s?Sol(\d*):(.*?)\n?\s?Ans(\d*):(.*?)\n"
            result=process_raw(results)
            matches = re.findall(pattern, result+"\n\n")
            if len(matches)>k:
                matches=matches[:k]
            try:
                shot_list=[(process_text(i[1]),eval(i[3]),change(i[5]),process_text(i[7]),process_text(i[9])) for i in matches]
            except:
                return False

            if len(shot_list)<k:
                return False
            return True
        else:
            raise NotImplementedError
        
    


    elif dataset=='MATH':
        if scenario=='van':
            pattern = r"Question\s?\d?:(.*?)\s?Ans(wer)?\s?\d?:(.*?)\n"
            result=process_raw(results)
            matches = re.findall(pattern, result+"\n\n")
            if len(matches)<k:
                matches_a=get_special_match(result,pattern)
                if len(matches_a)>=k:
                    matches=matches_a
                elif len(matches_a)<k:
                    matches_b=get_special_match_b(result,pattern)
                    if len(matches_b)>=k:
                        matches=matches_b
            if len(matches)>k:
                    matches=matches[:k]
            try:
                for item in matches:
                    assert find_ans(item[2]) is not None
                    assert normalize_final_answer(find_ans(item[2])) is not None
            except:
                return False
            if len(matches)<k:
                return False
            return True
        elif scenario=='cot':
            pattern = r"Question\s?\d?:(.*?)\s?Sol\s?\d?:(.*?)\s?Ans(wer)?\s?\d?:(.*?)\n"
            result=process_raw(results)
            matches = re.findall(pattern, result+"\n\n")
            if len(matches)<k:
                matches_a=get_special_match(result+"\n\n",pattern)
                if len(matches_a)>len(matches):
                    matches=matches_a
                if len(matches)<k:
                    matches_c=get_special_match_b(result,pattern)
                    if len(matches_c)>len(matches):
                        matches=matches_c
            if len(matches)>k: 
                matches=matches[:k]
            try:
                for item in matches:
                    assert find_ans(item[3]) is not None
                    assert normalize_final_answer(find_ans(item[3])) is not None
            except:
                return False
            if len(matches)<k:
                return False
            return True
        else:
            raise NotImplementedError
        
       

        
    

    elif dataset=='MMLU':
        if scenario=='van':
            pattern = r"Question\s?\d?:(.*?)\s?Label\d?:(.*?)\n?\s?Text\d?:(.*?)\n?\s?Ans(wer)?\d?:(.*?)\n"
            result=process_raw(results)
            matches = re.findall(pattern, result+"\n\n")
            if len(matches)<k:
                matches=get_special_match(result,pattern)
                if len(matches)<k:
                    matches=get_special_match_b(result,pattern)
            if len(matches)>k:
                matches=matches[:k]
            try:
                shot_list=[(process_text(i[0]),['A','B','C','D'],change(i[2]),process_label(process_text(i[4]))) for i in matches]
                for i in shot_list:
                    assert i[3] in ['A','B','C','D']
                    assert len(i[2])==4
            except:
                return False
            if len(shot_list)<k:
                return False
            return True
        elif scenario=='cot':
            pattern = r"Question\s?\d?:(.*?)\s?Label\d?:(.*?)\n?\s?Text\d?:(.*?)\n?\s?Sol\d?:(.*?)\n?\s?Ans(wer)?\d?:(.*?)\n"
            result=process_raw(results)
            matches = re.findall(pattern, result+"\n\n")
            if len(matches)<k:
                matches=get_special_match(result,pattern)
                if len(matches)<k:
                    matches=get_special_match_b(result,pattern)
            if len(matches)>k:
                matches=matches[:k]
            try:
                shot_list=[(process_text(i[0]),['A','B','C','D'],change(i[2]),process_text(i[3]),process_label(process_text(i[5]))) for i in matches]
                for i in shot_list:
                    assert i[4] in ['A','B','C','D']
                    assert len(i[2])==4
            except:
                return False
            if len(shot_list)<k:
                return False
            return True
        else:
            raise NotImplementedError
        



    elif dataset=='Ceval':
        if scenario=='van':
            pattern = r"题目\s?\d?[:：](.*?)\n?\s?选项标签\s?\d?[:：](.*?)\n?\s?选项内容\d?[:：](.*?)\n?\s?答案?\d?[:：](.*?)\n"
            result=process_raw(results)
            matches = re.findall(pattern, result+"\n\n")
            if len(matches)<k:
                matches_a=get_special_match(results,pattern)
                if len(matches_a)>len(matches):
                        matches=matches_a
                if len(matches)<k:
                    matches_c=get_special_match_b(result,pattern)
                    if len(matches_c)>len(matches):
                        matches=matches_c 
            if len(matches)>k:
                    matches=matches[:k]
            try:
                shot_list=[(process_text(i[0]),eval(i[1]),change(i[2]),process_label(process_text(i[3]))) for i in matches]
                for i in shot_list:
                    assert i[3] in ['A','B','C','D']
                    assert len(i[2])==4
            except:
                return False
            if len(shot_list)<k:
                return False
            return True
        elif scenario=='cot':
            pattern = r"题目\s?\d?[:：](.*?)\n?\s?选项标签\s?\d?[:：](.*?)\n?\s?选项内容\d?[:：](.*?)\n?\s?解析\d?[:：](.*?)\n?\s?答案?\d?[:：](.*?)\n"
            result=process_raw(results)
            matches = re.findall(pattern, result+"\n\n")
            if len(matches)<k:
                matches_a=get_special_match(results,pattern)
                if len(matches_a)>len(matches):
                        matches=matches_a
                if len(matches)<k:
                    matches_c=get_special_match_b(result,pattern)
                    if len(matches_c)>len(matches):
                        matches=matches_c 
            if len(matches)>k:
                    matches=matches[:k]
            try:
                shot_list=[(process_text(i[0]),['A','B','C','D'],change(i[2]),process_text(i[3]),process_label(process_text(i[4]))) for i in matches]
                for i in shot_list:
                    assert i[4] in ['A','B','C','D']
                    assert len(i[2])==4
            except:
                return False
            if len(shot_list)<k:
                return False
            return True
        else:
            raise NotImplementedError
        

    elif dataset=='HumanEval':
        if scenario=='van':
            pattern = pattern = r'\[\[Function Header\d\]\]:(.*?)\[\[Function Body\d\]\]:((.*?)(?=\[\[|$))'
        elif scenario=='cot':
            raise NotImplementedError
        else:
            raise NotImplementedError
        matches = re.findall(pattern, results, re.DOTALL)
        if len(matches)>k:
            matches=matches[:k]
        try:
            shot_list=[(i[0],i[1]) for i in matches]
            for i in shot_list:
                assert i[0] !=None
                assert i[0]!=""
                assert i[1] !=None
                assert i[1]!=""
                assert " return " in i[1] or i[1][:6]=='return' or "\nreturn " in i[1]
        except:
            return False
        if len(shot_list)<k:
            return False
        return True
    else:
        return NotImplementedError




def parse_answer(input_data,dataset,scenario,k):
    few=[]
    if dataset=='GSM8k':
        if scenario=='van':
            pattern = r"Q\s?\d?:(.*?)\s?\s?S\s?\d?:(.*?)\s?\n?\s?A\s?\d?:(.*?)\s?\n"
            filename='gsm_van_demonstrations.json'
        elif scenario=='cot':
            pattern = r"Q\s?\d?:(.*?)\s?\s?S\s?\d?:(.*?)\s?\n?\s?A\s?\d?:(.*?)\s?\n"
            filename='gsm_cot_demonstrations.json'
        else:
            raise NotImplementedError
        for i in range(0,1319):
            result=process_raw(input_data[i]["result"])
            matches = re.findall(pattern, result+"\n\n")
            if len(matches)<k:
                matches_a=get_special_match(result,pattern)
                if len(matches_a)>=k:
                    matches=matches_a
                elif len(matches_a)<k:
                    matches_b=get_special_match_b(result,pattern)
                    if len(matches_b)>=k:
                        matches=matches_b
            if len(matches)>k:
                matches=matches[:k]
            shot_list=[(process_text(i[0]),process_text(i[1]),get_ans(i[2])) for i in matches]
            few.append({
                "idx":i,
                "few_shot":shot_list
            })
        
        with open(os.path.join('.','data',filename),"w") as file:
            json.dump(few, file, ensure_ascii=False, indent=2) 
    elif dataset=='ARC':
        if scenario=='van':
            filename='arc_van_demonstrations.json'
            pattern = r"Question(\d*):(.*?)\s?Label(\d*):(.*?)\n?\s?Text(\d*):(.*?)\n?\s?Ans(\d*):(.*?)\n"
            for i in range(0,1172):
                result=process_raw(input_data[i]["result"]) 
                matches = re.findall(pattern, result+"\n\n")
                if len(matches)>k:
                    matches=matches[:k]
                shot_list=[(process_text(i[1]),eval(i[3]),change(i[5]),process_text(i[7])) for i in matches]
                prom=[gen_arc(i) for i in shot_list]
                few.append({
                    "idx":i,
                    "few_shot":{"list":shot_list,"prompt":prom}
                })
            with open(os.path.join('.','data',filename),"w") as file:
                json.dump(few, file, ensure_ascii=False, indent=2) 
        elif scenario=='cot':
            filename='arc_cot_demonstrations.json'
            pattern = r"Question(\d*):(.*?)\s?Label(\d*):(.*?)\n?\s?Text(\d*):(.*?)\n?\s?Sol(\d*):(.*?)\n?\s?Ans(\d*):(.*?)\n"
            for i in range(0,1172):
                result=process_raw(input_data[i]["result"]) 
                matches = re.findall(pattern, result+"\n\n")
                if len(matches)>k:
                    matches=matches[:k]
                shot_list=[(process_text(i[1]),eval(i[3]),change(i[5]),process_text(i[7]),process_text(i[9])) for i in matches]
                prom=[gen_arc(i) for i in shot_list]
                few.append({
                    "idx":i,
                    "few_shot":{"list":shot_list,"prompt":prom}
                })
            with open(os.path.join('.','data',filename),"w") as file:
                json.dump(few, file, ensure_ascii=False, indent=2) 
        else:
            raise NotImplementedError
        


    elif dataset=='MATH':
        if scenario=='van':
            pattern = r"Question\s?\d?:(.*?)\s?Ans(wer)?\s?\d?:(.*?)\n"
            filename='math_van_demonstrations.json'
            for i in range(0,5000):
                result=process_raw(input_data[i]["result"]) 
                matches = re.findall(pattern, result+"\n\n")
                if len(matches)<k:
                    matches_a=get_special_match(result,pattern)
                    if len(matches_a)>=k:
                        matches=matches_a
                    elif len(matches_a)<k:
                        matches_b=get_special_match_b(result,pattern)
                        if len(matches_b)>=k:
                            matches=matches_b
                if len(matches)>k:
                    matches=matches[:k]
                shot_list=[(process_text(i[0]),_strip_string(normalize_final_answer(find_ans(process_text(i[2]))))) for i in matches]
                prom=[gen_math(i) for i in shot_list]
                few.append({
                    "idx":i,
                    "few_shot":{"list":shot_list,"prompt":prom,'Ans':["$"+i[1]+"$" for i in shot_list]},
                })
            with open(os.path.join('.','data',filename),"w") as file:
                json.dump(few, file, ensure_ascii=False, indent=2) 

        elif scenario=='cot':
            pattern = r"Question\s?\d?:(.*?)\s?Sol\s?\d?:(.*?)\s?Ans(wer)?\s?\d?:(.*?)\n"
            error_index=utils.get_abnormal_index(input_data)
            if error_index is not None:
                filename='math_van_demonstrations.json'
                assert os.path.exists(os.path.join('.','data',filename)), f"file {filename} not exists"
                with open(os.path.join('.','data',filename)) as input_file:
                    demonstration_input_all=json.load(input_file) 
            filename='math_cot_demonstrations.json'
            for i in range(0,5000):
                if i in error_index:
                    few.append({
                    "idx":i,
                    "few_shot":demonstration_input_all[i]['few_shot'],
                    })
                    continue
                result=process_raw(input_data[i]["result"])
                matches = re.findall(pattern, result+"\n\n")
                if len(matches)<k:
                    matches_a=get_special_match(result+"\n\n",pattern)
                    if len(matches_a)>len(matches):
                        matches=matches_a
                    if len(matches)<k:
                        matches_c=get_special_match_b(result,pattern)
                        if len(matches_c)>len(matches):
                            matches=matches_c
                if len(matches)>k: 
                    matches=matches[:k]
                shot_list=[(process_text(i[0]),process_text(i[1]),_strip_string(normalize_final_answer(find_ans(process_text(i[3]))))) for i in matches]
                prom=[gen_math(i) for i in shot_list]
                few.append({
                    "idx":i,
                    "few_shot":{"list":shot_list,"prompt":prom,'Ans':["$"+i[2]+"$" for i in shot_list]},
                })
                with open(os.path.join('.','data',filename),"w") as file:
                    json.dump(few, file, ensure_ascii=False, indent=2) 

        else:
            raise NotImplementedError 
        
    elif dataset=='MMLU':
        if scenario=='van':
            pattern = r"Question\s?\d?:(.*?)\s?Label\d?:(.*?)\n?\s?Text\d?:(.*?)\n?\s?Ans(wer)?\d?:(.*?)\n"
            filename='mmlu_van_demonstrations.json'
            for i in range(0,13985):
                result=process_raw(input_data[i]["result"])
                matches = re.findall(pattern, result+"\n\n")
                if len(matches)<k:
                    matches=get_special_match(result,pattern)
                    if len(matches)<k:
                            matches=get_special_match_b(result,pattern)
                if len(matches)>k:
                    matches=matches[:k]
                shot_list=[(process_text(i[0]),['A','B','C','D'],change(i[2]),process_label(process_text(i[4]))) for i in matches]
                shot_list=[process(i) for i in shot_list]
                prom=[gen_mmlu(i) for i in shot_list]
                few.append({
                    "idx":i,
                    "few_shot":{"list":shot_list,"prompt":prom,'Ans':[i[3] for i in shot_list]}
                })
            with open(os.path.join('.','data',filename),"w") as file:
                json.dump(few, file, ensure_ascii=False, indent=2) 
        elif scenario=='cot':
            pattern = r"Question\s?\d?:(.*?)\s?Label\d?:(.*?)\n?\s?Text\d?:(.*?)\n?\s?Sol\d?:(.*?)\n?\s?Ans(wer)?\d?:(.*?)\n"
            filename='mmlu_cot_demonstrations.json'
            for i in range(0,13985):
                result=process_raw(input_data[i]["result"])
                matches = re.findall(pattern, result+"\n\n")
                if len(matches)<k:
                    matches=get_special_match(result,pattern)
                    if len(matches)<k:
                            matches=get_special_match_b(result,pattern)
                if len(matches)>k:
                    matches=matches[:k]
                shot_list=[(process_text(i[0]),['A','B','C','D'],change(i[2]),process_text(i[3]),process_label(process_text(i[5]))) for i in matches]
                shot_list=[process(i) for i in shot_list]
                prom=[gen_mmlu(i) for i in shot_list]
                few.append({
                    "idx":i,
                    "few_shot":{"list":shot_list,"prompt":prom,'Ans':[i[4] for i in shot_list]}
                })
            with open(os.path.join('.','data',filename),"w") as file:
                json.dump(few, file, ensure_ascii=False, indent=2) 
        else:
            raise NotImplementedError
    


    elif dataset=='Ceval':
        if scenario=='van':
            pattern = r"题目\s?\d?[:：](.*?)\n?\s?选项标签\s?\d?[:：](.*?)\n?\s?选项内容\d?[:：](.*?)\n?\s?答案?\d?[:：](.*?)\n"
            filename='ceval_van_demonstrations.json'
            for i in range(0,12342):
                result=process_raw(input_data[i]["result"])
                matches = re.findall(pattern, result+"\n\n")
                if len(matches)<k:
                    matches_a=get_special_match(input_data[i]["result"],pattern)
                    if len(matches_a)>len(matches):
                        matches=matches_a
                    if len(matches)<k:
                        matches_c=get_special_match_b(result,pattern)
                        if len(matches_c)>len(matches):
                            matches=matches_c
                if len(matches)>k:
                    matches=matches[:k]
                shot_list=[(process_text(i[0]),['A','B','C','D'],change(i[2]),process_label(process_text(i[3]))) for i in matches]
                shot_list=[process(i) for i in shot_list]
                prom=[gen_ceval(i) for i in shot_list]
                few.append({
                    "idx":i,
                    "few_shot":{"list":shot_list,"prompt":prom,'Ans':[i[3] for i in shot_list]}
                })
            with open(os.path.join('.','data',filename),"w") as file:
                json.dump(few, file, ensure_ascii=False, indent=2) 
        elif scenario=='cot':
            pattern = r"题目\s?\d?[:：](.*?)\n?\s?选项标签\s?\d?[:：](.*?)\n?\s?选项内容\d?[:：](.*?)\n?\s?解析\d?[:：](.*?)\n?\s?答案?\d?[:：](.*?)\n"
            filename='ceval_cot_demonstrations.json'
            for i in range(0,12342):
                result=process_raw(input_data[i]["result"])
                matches = re.findall(pattern, result+"\n\n")
                if len(matches)<k:
                    matches_a=get_special_match(input[i]["result"][0],pattern)
                    if len(matches_a)>len(matches):
                        matches=matches_a
                    if len(matches)<k:
                        matches_c=get_special_match_b(result,pattern)
                        if len(matches_c)>len(matches):
                            matches=matches_c
                if len(matches)>k:
                    matches=matches[:k]
                shot_list=[(process_text(i[0]),['A','B','C','D'],change(i[2]),process_text(i[3]),process_label(process_text(i[4]))) for i in matches]
                shot_list=[process(i) for i in shot_list]
                prom=[gen_ceval(i) for i in shot_list]
                few.append({
                    "idx":i,
                    "few_shot":{"list":shot_list,"prompt":prom,'Ans':[i[4] for i in shot_list]}
                })
            with open(os.path.join('.','data',filename),"w") as file:
                json.dump(few, file, ensure_ascii=False, indent=2) 
        else:
            raise NotImplementedError

    elif dataset=='HumanEval':
        if scenario=='van':
            pattern = pattern = r'\[\[Function Header\d\]\]:(.*?)\[\[Function Body\d\]\]:((.*?)(?=\[\[|$))'
            filename='humaneval_van_demonstrations.json'
            for i in range(0,164):
                result=input_data[i]["result"]
                matches =re.findall(pattern, result, re.DOTALL)
                if len(matches)>k:
                    matches=matches[:k]
                shot_list=[(i[0],process_humaneval(i[1])) for i in matches]
                few.append({
                    "idx":i,
                    "few_shot":{"list":shot_list,'prom':[i[0] for i in shot_list],'Ans':[i[1] for i in shot_list]},
                })
            with open(os.path.join('.','data',filename),"w") as file:
                json.dump(few, file, ensure_ascii=False, indent=2) 

        elif scenario=='cot':
            raise NotImplementedError
        else:
            raise NotImplementedError
