import json
import os
import re
from datasets import load_dataset
from tqdm import tqdm
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

        result.append({
            'idx':i,
            "prompt":prompt,
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
    subcategories = {
        "abstract_algebra": ["math"],
        "anatomy": ["health"],
        "astronomy": ["physics"],
        "business_ethics": ["business"],
        "clinical_knowledge": ["health"],
        "college_biology": ["biology"],
        "college_chemistry": ["chemistry"],
        "college_computer_science": ["computer science"],
        "college_mathematics": ["math"],
        "college_medicine": ["health"],
        "college_physics": ["physics"],
        "computer_security": ["computer science"],
        "conceptual_physics": ["physics"],
        "econometrics": ["economics"],
        "electrical_engineering": ["engineering"],
        "elementary_mathematics": ["math"],
        "formal_logic": ["philosophy"],
        "global_facts": ["other"],
        "high_school_biology": ["biology"],
        "high_school_chemistry": ["chemistry"],
        "high_school_computer_science": ["computer science"],
        "high_school_european_history": ["history"],
        "high_school_geography": ["geography"],
        "high_school_government_and_politics": ["politics"],
        "high_school_macroeconomics": ["economics"],
        "high_school_mathematics": ["math"],
        "high_school_microeconomics": ["economics"],
        "high_school_physics": ["physics"],
        "high_school_psychology": ["psychology"],
        "high_school_statistics": ["math"],
        "high_school_us_history": ["history"],
        "high_school_world_history": ["history"],
        "human_aging": ["health"],
        "human_sexuality": ["culture"],
        "international_law": ["law"],
        "jurisprudence": ["law"],
        "logical_fallacies": ["philosophy"],
        "machine_learning": ["computer science"],
        "management": ["business"],
        "marketing": ["business"],
        "medical_genetics": ["health"],
        "miscellaneous": ["other"],
        "moral_disputes": ["philosophy"],
        "moral_scenarios": ["philosophy"],
        "nutrition": ["health"],
        "philosophy": ["philosophy"],
        "prehistory": ["history"],
        "professional_accounting": ["other"],
        "professional_law": ["law"],
        "professional_medicine": ["health"],
        "professional_psychology": ["psychology"],
        "public_relations": ["politics"],
        "security_studies": ["politics"],
        "sociology": ["culture"],
        "us_foreign_policy": ["politics"],
        "virology": ["health"],
        "world_religions": ["philosophy"],
    }

    categories = {
        "STEM": ["physics", "chemistry", "biology", "computer science", "math", "engineering"],
        "humanities": ["history", "philosophy", "law"],
        "social sciences": ["politics", "culture", "economics", "geography", "psychology"],
        "other (business, health, misc.)": ["other", "business", "health"],
    }
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
            out.append({
                'idx':idx,
                'tuple':(test_data[j]['input'],label,choice,test_data[j]['target']),
                'prompt':prompt,
                'class':i,
                'subcat':subcategories[i],
            })
            idx+=1
    output_path=os.path.join('.','data','mmlu.json') 
    with open(output_path,"w") as file:
        json.dump(out, file, ensure_ascii=False, indent=2) 

def ceval():
    #https://github.com/SJTU-LIT/ceval/blob/main/subject_mapping.json
    input_dict={
	"computer_network": [
		"Computer Network",
		"\u8ba1\u7b97\u673a\u7f51\u7edc",
		"STEM"
	],
	"operating_system": [
		"Operating System",
		"\u64cd\u4f5c\u7cfb\u7edf",
		"STEM"
	],
	"computer_architecture": [
		"Computer Architecture",
		"\u8ba1\u7b97\u673a\u7ec4\u6210",
		"STEM"
	],
	"college_programming": [
		"College Programming",
		"\u5927\u5b66\u7f16\u7a0b",
		"STEM"
	],
	"college_physics": [
		"College Physics",
		"\u5927\u5b66\u7269\u7406",
		"STEM"
	],
	"college_chemistry": [
		"College Chemistry",
		"\u5927\u5b66\u5316\u5b66",
		"STEM"
	],
	"advanced_mathematics": [
		"Advanced Mathematics",
		"\u9ad8\u7b49\u6570\u5b66",
		"STEM"
	],
	"probability_and_statistics": [
		"Probability and Statistics",
		"\u6982\u7387\u7edf\u8ba1",
		"STEM"
	],
	"discrete_mathematics": [
		"Discrete Mathematics",
		"\u79bb\u6563\u6570\u5b66",
		"STEM"
	],
	"electrical_engineer": [
		"Electrical Engineer",
		"\u6ce8\u518c\u7535\u6c14\u5de5\u7a0b\u5e08",
		"STEM"
	],
	"metrology_engineer": [
		"Metrology Engineer",
		"\u6ce8\u518c\u8ba1\u91cf\u5e08",
		"STEM"
	],
	"high_school_mathematics": [
		"High School Mathematics",
		"\u9ad8\u4e2d\u6570\u5b66",
		"STEM"
	],
	"high_school_physics": [
		"High School Physics",
		"\u9ad8\u4e2d\u7269\u7406",
		"STEM"
	],
	"high_school_chemistry": [
		"High School Chemistry",
		"\u9ad8\u4e2d\u5316\u5b66",
		"STEM"
	],
	"high_school_biology": [
		"High School Biology",
		"\u9ad8\u4e2d\u751f\u7269",
		"STEM"
	],
	"middle_school_mathematics": [
		"Middle School Mathematics",
		"\u521d\u4e2d\u6570\u5b66",
		"STEM"
	],
	"middle_school_biology": [
		"Middle School Biology",
		"\u521d\u4e2d\u751f\u7269",
		"STEM"
	],
	"middle_school_physics": [
		"Middle School Physics",
		"\u521d\u4e2d\u7269\u7406",
		"STEM"
	],
	"middle_school_chemistry": [
		"Middle School Chemistry",
		"\u521d\u4e2d\u5316\u5b66",
		"STEM"
	],
	"veterinary_medicine": [
		"Veterinary Medicine",
		"\u517d\u533b\u5b66",
		"STEM"
	],
	"college_economics": [
		"College Economics",
		"\u5927\u5b66\u7ecf\u6d4e\u5b66",
		"Social Science"
	],
	"business_administration": [
		"Business Administration",
		"\u5de5\u5546\u7ba1\u7406",
		"Social Science"
	],
	"marxism": [
		"Marxism",
		"\u9a6c\u514b\u601d\u4e3b\u4e49\u57fa\u672c\u539f\u7406",
		"Social Science"
	],
	"mao_zedong_thought": [
		"Mao Zedong Thought",
		"\u6bdb\u6cfd\u4e1c\u601d\u60f3\u548c\u4e2d\u56fd\u7279\u8272\u793e\u4f1a\u4e3b\u4e49\u7406\u8bba\u4f53\u7cfb\u6982\u8bba",
		"Social Science"
	],
	"education_science": [
		"Education Science",
		"\u6559\u80b2\u5b66",
		"Social Science"
	],
	"teacher_qualification": [
		"Teacher Qualification",
		"\u6559\u5e08\u8d44\u683c",
		"Social Science"
	],
	"high_school_politics": [
		"High School Politics",
		"\u9ad8\u4e2d\u653f\u6cbb",
		"Social Science"
	],
	"high_school_geography": [
		"High School Geography",
		"\u9ad8\u4e2d\u5730\u7406",
		"Social Science"
	],
	"middle_school_politics": [
		"Middle School Politics",
		"\u521d\u4e2d\u653f\u6cbb",
		"Social Science"
	],
	"middle_school_geography": [
		"Middle School Geography",
		"\u521d\u4e2d\u5730\u7406",
		"Social Science"
	],
	"modern_chinese_history": [
		"Modern Chinese History",
		"\u8fd1\u4ee3\u53f2\u7eb2\u8981",
		"Humanities"
	],
	"ideological_and_moral_cultivation": [
		"Ideological and Moral Cultivation",
		"\u601d\u60f3\u9053\u5fb7\u4fee\u517b\u4e0e\u6cd5\u5f8b\u57fa\u7840",
		"Humanities"
	],
	"logic": [
		"Logic",
		"\u903b\u8f91\u5b66",
		"Humanities"
	],
	"law": [
		"Law",
		"\u6cd5\u5b66",
		"Humanities"
	],
	"chinese_language_and_literature": [
		"Chinese Language and Literature",
		"\u4e2d\u56fd\u8bed\u8a00\u6587\u5b66",
		"Humanities"
	],
	"art_studies": [
		"Art Studies",
		"\u827a\u672f\u5b66",
		"Humanities"
	],
	"professional_tour_guide": [
		"Professional Tour Guide",
		"\u5bfc\u6e38\u8d44\u683c",
		"Humanities"
	],
	"legal_professional": [
		"Legal Professional",
		"\u6cd5\u5f8b\u804c\u4e1a\u8d44\u683c",
		"Humanities"
	],
	"high_school_chinese": [
		"High School Chinese",
		"\u9ad8\u4e2d\u8bed\u6587",
		"Humanities"
	],
	"high_school_history": [
		"High School History",
		"\u9ad8\u4e2d\u5386\u53f2",
		"Humanities"
	],
	"middle_school_history": [
		"Middle School History",
		"\u521d\u4e2d\u5386\u53f2",
		"Humanities"
	],
	"civil_servant": [
		"Civil Servant",
		"\u516c\u52a1\u5458",
		"Other"
	],
	"sports_science": [
		"Sports Science",
		"\u4f53\u80b2\u5b66",
		"Other"
	],
	"plant_protection": [
		"Plant Protection",
		"\u690d\u7269\u4fdd\u62a4",
		"Other"
	],
	"basic_medicine": [
		"Basic Medicine",
		"\u57fa\u7840\u533b\u5b66",
		"Other"
	],
	"clinical_medicine": [
		"Clinical Medicine",
		"\u4e34\u5e8a\u533b\u5b66",
		"Other"
	],
	"urban_and_rural_planner": [
		"Urban and Rural Planner",
		"\u6ce8\u518c\u57ce\u4e61\u89c4\u5212\u5e08",
		"Other"
	],
	"accountant": [
		"Accountant",
		"\u6ce8\u518c\u4f1a\u8ba1\u5e08",
		"Other"
	],
	"fire_engineer": [
		"Fire Engineer",
		"\u6ce8\u518c\u6d88\u9632\u5de5\u7a0b\u5e08",
		"Other"
	],
	"environmental_impact_assessment_engineer": [
		"Environmental Impact Assessment Engineer",
		"\u73af\u5883\u5f71\u54cd\u8bc4\u4ef7\u5de5\u7a0b\u5e08",
		"Other"
	],
	"tax_accountant": [
		"Tax Accountant",
		"\u7a0e\u52a1\u5e08",
		"Other"
	],
	"physician": [
		"Physician",
		"\u533b\u5e08\u8d44\u683c",
		"Other"
	]
}
    out=[]
    label=['A','B','C','D']
    idx=0
    for i in tqdm(input_dict.keys()):
        dataset = load_dataset("ceval/ceval-exam",i)
        test_data=dataset["test"]
        for j in tqdm(range(int(test_data.num_rows))):
            choice=[test_data[j]['A'],test_data[j]['B'],test_data[j]['C'],test_data[j]['D']]
            prompt="题目:"+test_data[j]['question']+""
            for l in range(len(label)):
                prompt+="\n{}. {}".format(label[l], choice[l])
            out.append({
                'idx':idx,
                'tuple':(test_data[j]['question'],label,choice,test_data[j]['answer']),
                'prompt':prompt,
                'class':i,
                'subcat':input_dict[i][2],
                'chinese_class':input_dict[i][1],
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