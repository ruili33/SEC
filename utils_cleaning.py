import os
import re
from datasets import load_dataset
from tqdm import tqdm
import json
import utils

def _fix_fracs(string):
    substrs = string.split("\\frac")
    new_str = substrs[0]
    if len(substrs) > 1:
        substrs = substrs[1:]
        for substr in substrs:
            new_str += "\\frac"
            if substr[0] == "{":
                new_str += substr
            else:
                try:
                    assert len(substr) >= 2
                except:
                    return string
                a = substr[0]
                b = substr[1]
                if b != "{":
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}{" + b + "}" + post_substr
                    else:
                        new_str += "{" + a + "}{" + b + "}"
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}" + b + post_substr
                    else:
                        new_str += "{" + a + "}" + b
    string = new_str
    return string

def _fix_a_slash_b(string):
    if len(string.split("/")) != 2:
        return string
    a = string.split("/")[0]
    b = string.split("/")[1]
    try:
        a = int(a)
        b = int(b)
        assert string == "{}/{}".format(a, b)
        new_string = "\\frac{" + str(a) + "}{" + str(b) + "}"
        return new_string
    except:
        return string

def _remove_right_units(string):
    # "\\text{ " only ever occurs (at least in the val set) when describing units
    if "\\text{ " in string:
        splits = string.split("\\text{ ")
        assert len(splits) == 2
        return splits[0]
    else:
        return string

def _fix_sqrt(string):
    if "\\sqrt" not in string:
        return string
    splits = string.split("\\sqrt")
    new_string = splits[0] 
    for split in splits[1:]:
        if split[0] != "{":
            a = split[0]
            new_substr = "\\sqrt{" + a + "}" + split[1:]
        else:
            new_substr = "\\sqrt" + split
        new_string += new_substr
    return new_string
def _strip_string(string):
    # linebreaks  
    string = string.replace("\n", "")
    #print(string)

    # remove inverse spaces
    string = string.replace("\\!", "")
    #print(string)

    # replace \\ with \
    string = string.replace("\\\\", "\\")
    #print(string)

    # replace tfrac and dfrac with frac
    string = string.replace("tfrac", "frac")
    string = string.replace("dfrac", "frac")
    #print(string)

    # remove \left and \right
    string = string.replace("\\left", "")
    string = string.replace("\\right", "")
    #print(string)
    
    # Remove circ (degrees)
    string = string.replace("^{\\circ}", "")
    string = string.replace("^\\circ", "")

    # remove dollar signs
    string = string.replace("\\$", "")
    
    # remove units (on the right)
    string = _remove_right_units(string)

    # remove percentage
    string = string.replace("\\%", "")
    string = string.replace("\%", "")

    # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively, add "0" if "." is the start of the string
    string = string.replace(" .", " 0.")
    string = string.replace("{.", "{0.")
    # if empty, return empty string
    if len(string) == 0:
        return string
    if string[0] == ".":
        string = "0" + string

    # to consider: get rid of e.g. "k = " or "q = " at beginning
    if len(string.split("=")) == 2:
        if len(string.split("=")[0]) <= 2:
            string = string.split("=")[1]

    # fix sqrt3 --> sqrt{3}
    string = _fix_sqrt(string)

    # remove spaces
    string = string.replace(" ", "")

    # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc. Even works with \frac1{72} (but not \frac{72}1). Also does a/b --> \\frac{a}{b}
    string = _fix_fracs(string)

    # manually change 0.5 --> \frac{1}{2}
    if string == "0.5":
        string = "\\frac{1}{2}"

    # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple cases fix in case the model output is X/Y
    string = _fix_a_slash_b(string)

    return string
def process_raw(string):
    pattern = r"(?<!\n)\n(?!\n)"
    result = re.sub(pattern, "", string)
    pattern2=r"we have:\n\n"
    result = re.sub(pattern2, "we have:", result)
    return result
def process_raw_humaneval(string):
    pattern = r"(?<!\n)\n(?!\n)"
    result = re.sub(pattern, "@@", string)
    pattern2=r"we have:\n\n"
    result = re.sub(pattern2, "we have:", result)
    return result
def process_special(string):
    pattern = r"(?<!\n)\n(?!\n)"
    result = re.sub(pattern, "", string)
    pattern2=r"\n\n"
    result = re.sub(pattern2, "", result)
    return result
def process_text(passage): 
    mod_string=re.sub("{{", '', passage )
    mod_string=re.sub("}}", '', mod_string )
    mod_string=re.sub("\n", '', mod_string)
    mod_string=re.sub("\'", '', mod_string)
    mod_string=re.sub("\]", '', mod_string)
    mod_string=re.sub("\[", '', mod_string)
    mod_string=re.sub("\"", '', mod_string)
    if mod_string[0]==' ':
        mod_string=mod_string[1:]
    return mod_string
def get_ans(string):
    ans=re.findall(r"[-+]?\d(?:,?\d)*",string) 
    ans=[i.replace(",", "") for i in ans]
    return int(ans[-1]) if ans!=[] else 0
def change(string:str):
    string=string[1:-1]
    string=re.sub("\"", '\'', string )
    out=string.split("', '")
    return out
def get_special_match(result,pattern):
    mod_string=re.sub("\n\n\[", '}}}}', result)
    mod_string=re.sub("\n\n", ' ', mod_string)
    mod_string=re.sub("}}}}", '\n\n', mod_string)
    matches=re.findall(pattern, mod_string+"\n\n")
    return matches
def get_special_match_b(result,pattern):
    mod_string=re.sub("\n\nQues", '}}}}', result)
    mod_string=re.sub("\n\n", ' ', mod_string)
    mod_string=re.sub("}}}}", '\n\nQues', mod_string)
    matches=re.findall(pattern, mod_string+"\n\n")
    return matches
def process_label(passage):
    mod_string=re.sub(",", '', passage )
    mod_string=re.sub(" ", '', mod_string )
    return mod_string
def process(k):
    k=list(k)
    k[2]=[process_text(i) for i in k[2]]
    return k
SUBSTITUTIONS = [
    ('an ', ''), ('a ', ''), ('.$', '$'), ('\\$', ''), (r'\ ', ''),
    (' ', ''), ('mbox', 'text'), (',\\text{and}', ','),
    ('\\text{and}', ','), ('\\text{m}', '\\text{}')]
REMOVED_EXPRESSIONS = [
             'square', 'ways', 'integers', 'dollars', 'mph', 'inches', 'ft',
       'hours', 'km', 'units', '\\ldots', 'sue', 'points', 'feet',
       'minutes', 'digits', 'cents', 'degrees', 'cm', 'gm', 'pounds',
       'meters', 'meals', 'edges', 'students', 'childrentickets', 'multiples',
       '\\text{s}', '\\text{.}', '\\text{\ns}', '\\text{}^2',
       '\\text{}^3', '\\text{\n}', '\\text{}', r'\mathrm{th}',
       r'^\circ', r'^{\circ}', r'\;', r',\!', '{,}', '"', '\\dots' ]


def normalize_final_answer (final_answer: str) -> str:
    """Normalize a final answer to a quantitative reasoning question."""
    final_answer = final_answer.split('=')[-1]

    for before, after in SUBSTITUTIONS:

        final_answer= final_answer.replace (before, after)
    for expr in REMOVED_EXPRESSIONS:

        final_answer = final_answer.replace (expr, '')

    # Extract answer that is in LaTeX math, is bold,

    # is surrounded by a box, etc.

    final_answer =re.sub(r'(.*?)(\$)(.*?)(\$)(.*)', '$\\3$', final_answer)
    final_answer =re.sub(r'(\\text\{)(.*?)(\})', '\\2', final_answer)
    final_answer = re.sub(r'(\\textbf\{)(.*?)(\})', '\\2', final_answer)
    final_answer =re.sub(r'(\\overline\{)(.*?)(\})', '\\2', final_answer)
    final_answer = re.sub(r'(\\boxed\{)(.*)(\})', '\\2', final_answer)
                                                
    # Normalize shorthand TeX:
    # \fracab —-> \frac{a}{b}
    # \frac{abc} {bef} —-> \frac{abc} {bef}
    # \fracabc -> \frac{a}{bl}c
    # \sgrta -> \sgrt{a}
    # \sgrtab -> sqgrt{a}b
    final_answer = re.sub (
    r'(frac)([^{])(.)', 'frac{\\2}{\\3}', final_answer)
    final_answer = re.sub(
    r'(sqrt)([^{])', 'sqrt{\\2}', final_answer)
    final_answer = final_answer.replace('$', '')

    # Normalize 100,000 -> 100000
    if final_answer.replace(',', '').isdigit():

        final_answer = final_answer.replace(',', '')

    return final_answer

def find_ans(result):
    pattern = r'\$(.*?)\$'
    matches = re.findall(pattern, result)
    if len(matches)==1:
        return matches[0]
    pattern = r"Answer:(.*)"
    match = re.search(pattern, result, re.IGNORECASE)

    if match:
        extracted_part = match.group(1)
        matches_e = re.findall(r'\$(.*?)\$', result)
        if len(matches_e)>0:
            return matches_e[-1]

        ans=re.findall(r"[-+]?[0-9]*\.?[0-9]+",extracted_part) 
        ans=[i.replace(",", "") for i in ans]
        return ans[0] if ans!=[] else extracted_part 
    else:
        if len(matches)>0:
            return matches[0]
        ans=re.findall(r'[-+]?[0-9]*\.?[0-9]+',result) 
        ans=[i.replace(",", "") for i in ans]
        return ans[-1] if ans!=[] else None
    


def gen_arc(data):
    prompt=data[0]
    choice_text=data[2]
    choice_lab=data[1]
    for j in range(len(choice_lab)):
        prompt+="\n{}. {}".format(choice_lab[j], choice_text[j])
    return prompt


def gen_math(data):
    prompt=""+data[0]+""
    return prompt

def gen_mmlu(data):
    prompt="Question:{{"+data[0]+"}}"
    choice_text=data[2]
    choice_lab=data[1]
    for j in range(len(choice_lab)):
        prompt+="\n{}. {}".format(choice_lab[j], choice_text[j])
    return prompt

def gen_ceval(data):
    prompt="题目:"+data[0]+""
    choice_text=data[2]
    choice_lab=data[1]
    for j in range(len(choice_lab)):
        prompt+="\n{}. {}".format(choice_lab[j], choice_text[j])
    return prompt
def process_humaneval(string):
    if string[-3:]=="]\n\n":
        return string[:-3]
    else:
        return string
    



def find_ans_gsm(result):
    ans=re.findall(r"[-+]?\d(?:,?\d)*",result) 
    ans=[i.replace(",", "") for i in ans]
    if len(ans)==1:
        return int(ans[0])
    pattern = r"The answer is\s*(.*)"
    match = re.search(pattern, result, re.IGNORECASE)

    # 提取到的部分
    if match:
        extracted_part = match.group(1)
        ans=re.findall(r"[-+]?\d(?:,?\d)*",extracted_part) 
        ans=[i.replace(",", "") for i in ans]
        return int(ans[0]) if ans!=[] else None
    else:
        return int(ans[-1]) if ans!=[] else None
def check_in(result,label):
    out=[]
    for i in label:
        if i in result:
            out.append(i)
    return out  
def adv_check(result,label):
    out=[]
    for i in label:
        if i+"." in result:
            out.append(i)
    return out
def find_ans_arc(result,label):
    filt=check_in(result,label)
    if len(filt)==1:
        return filt[0]
    if len(filt)==0:
        return label[0]
    pattern = r"Answer:\s*(.*)"
    match = re.search(pattern, result, re.IGNORECASE)

    # 提取到的部分
    if match:
        extracted_part = match.group(1)
        ans_filter=check_in(extracted_part,filt)
        if len(ans_filter)==1:
            return ans_filter[0]
        ans_filter_a=adv_check(extracted_part,ans_filter)
        if len(ans_filter_a)==1:
            return ans_filter_a[0]
        if len(ans_filter)>1:
            return ans_filter[-1]
    
    filt=adv_check(result,filt)
    if(len(filt)==1):
        return filt[0]
    elif(len(filt)>1):
        return filt[-1]
    if "Answer" in result:
        result2=result.replace("Answer:","")
        filt=check_in(result2,filt)
    if len(filt)==1:
        return filt[0]
    return  label[0]

def is_equiv(str1, str2, verbose=False):
    if str1 is None and str2 is None:
        print("WARNING: Both None")
        return True
    if str1 is None or str2 is None:
        return False

    try:
        ss1 = _strip_string(str1)
        ss2 = _strip_string(str2)
        if verbose:
            print(ss1, ss2)
        return ss1 == ss2
    except:
        return str1 == str2
    


def find_ans_math(result):
    pattern = r'\$(.*?)\$'
    matches = re.findall(pattern, result)
    if len(matches)==1:
        return matches[0]
    pattern = r"Answer:(.*)"
    match = re.search(pattern, result, re.IGNORECASE)

    if match:
        extracted_part = match.group(1)
        matches_e = re.findall(r'\$(.*?)\$', result)
        if len(matches_e)>0:
            return matches_e[-1]

        ans=re.findall(r"[-+]?[0-9]*\.?[0-9]+",extracted_part) 
        ans=[i.replace(",", "") for i in ans]
        return ans[0] if ans!=[] else extracted_part 
    else:
        if len(matches)>0:
            return matches[0]
        ans=re.findall(r'[-+]?[0-9]*\.?[0-9]+',result) 
        ans=[i.replace(",", "") for i in ans]
        return ans[-1] if ans!=[] else None

def find_ans_mmlu(result,label=['A','B','C','D']):
    filt=check_in(result,label)
    if len(filt)==1:
        return filt[0]
    if len(filt)==0:
        return label[0]
    pattern = r"Answer:\s*(.*)"
    match = re.search(pattern, result, re.IGNORECASE)

    # 提取到的部分
    if match:
        extracted_part  = match.group(1)
        # extracted_part=process_label(process_text(extracted_part))
        ans_filter=check_in(extracted_part,filt)
        if len(ans_filter)==1:
            return ans_filter[0]
        ans_filter_a=adv_check(extracted_part,ans_filter)
        if len(ans_filter_a)==1:
            return ans_filter_a[0]
        if len(ans_filter)>1:
            return ans_filter[-1]
    
    filt=adv_check(result,filt)
    if(len(filt)==1):
        return filt[0]
    elif(len(filt)>1):
        return filt[-1]
    if "Answer" in result:
        result2=result.replace("Answer:","")
        filt=check_in(result2,filt)
    if len(filt)==1:
        return filt[0]
    return  label[0]

def find_ans_ceval(result,label=['A','B','C','D']):
    filt=check_in(result,label)
    if len(filt)==1:
        return filt[0]
    if len(filt)==0:
        return label[0]
    pattern = r"答案[:：]\s*(.*)"
    match = re.search(pattern, result, re.IGNORECASE)

    # 提取到的部分
    if match:
        extracted_part  = match.group(1)
        # extracted_part=process_label(process_text(extracted_part))
        ans_filter=check_in(extracted_part,filt)
        if len(ans_filter)==1:
            return ans_filter[0]
        ans_filter_a=adv_check(extracted_part,ans_filter)
        if len(ans_filter_a)==1:
            return ans_filter_a[0]
        if len(ans_filter)>1:
            return ans_filter[-1]
    
    filt=adv_check(result,filt)
    if(len(filt)==1):
        return filt[0]
    elif(len(filt)>1):
        return filt[-1]
    if "答案" in result:
        result2=result.replace("答案:","")
        result2=result.replace("答案：","")
        filt=check_in(result2,filt)
    if len(filt)==1:
        return filt[0]
    return  label[0]