import os
import re
from datasets import load_dataset
from tqdm import tqdm
def process_raw(string):
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

def answer_validation(results,dataset,scenario,k):
    if dataset=='GSM8k':
        if scenario=='van':
            pattern = r"Q\s?\d?:(.*?)\s?\s?S\s?\d?:(.*?)\s?\n?\s?A\s?\d?:(.*?)\s?\n"
        elif scenario=='cot':
            pattern = r"Q\s?\d?:(.*?)\s?\s?S\s?\d?:(.*?)\s?\n?\s?A\s?\d?:(.*?)\s?\n"
        else:
            raise NotImplementedError
        result=process_raw(results)
        matches = re.findall(pattern, result+"\n\n", re.DOTALL)
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
        elif scenario=='cot':
            pattern = r"Question(\d*):(.*?)\s?Label(\d*):(.*?)\n?\s?Text(\d*):(.*?)\n?\s?Sol(\d*):(.*?)\n?\s?Ans(\d*):(.*?)\n"
        else:
            raise NotImplementedError
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
    


    elif dataset=='MATH':
        if scenario=='van':
            pattern = r"Question\s?\d?:(.*?)\s?Ans(wer)?\s?\d?:(.*?)\n"
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
    

    elif dataset=='MMLU':
        if scenario=='van':
            pattern = r"Question\s?\d?:(.*?)\s?Label\d?:(.*?)\n?\s?Text\d?:(.*?)\n?\s?Ans(wer)?\d?:(.*?)\n"
        elif scenario=='cot':
            pattern = r"Question\s?\d?:(.*?)\s?Label\d?:(.*?)\n?\s?Text\d?:(.*?)\n?\s?Sol\d?:(.*?)\n?\s?Ans(wer)?\d?:(.*?)\n"
        else:
            raise NotImplementedError
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
                assert i[3] in ['A','B','C','D']
                assert len(i[2])==4
        except:
            return False
        if len(shot_list)<k:
            return False
        return True



    elif dataset=='Ceval':
        if scenario=='van':
            pattern = r"题目\s?\d?[:：](.*?)\n?\s?选项标签\s?\d?[:：](.*?)\n?\s?选项内容\d?[:：](.*?)\n?\s?答案?\d?[:：](.*?)\n"
        elif scenario=='cot':
            pattern = r"题目\s?\d?[:：](.*?)\n?\s?选项标签\s?\d?[:：](.*?)\n?\s?选项内容\d?[:：](.*?)\n?\s?解析\d?[:：](.*?)\n?\s?答案?\d?[:：](.*?)\n"
        else:
            raise NotImplementedError
        result=process_raw(results)
        matches = re.findall(pattern, result+"\n\n")
        if len(matches)<k:
            matches_a=get_special_match(results,pattern)
        if len(matches_a)>=k:
            matches=matches_a
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

    elif dataset=='HumanEval':
        if scenario=='van':
            pattern = pattern = r'\[\[Function Header\d\]\]:(.*?)\[\[Function Body\d\]\]:((.*?)(?=\[\[|$))'
        elif scenario=='cot':
            raise NotImplementedError
        else:
            raise NotImplementedError
        result=process_raw(results)
        matches = re.findall(pattern, result, re.DOTALL)
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
