import json
def get_end(prompt_list,end):
    if end==-1:
        return len(prompt_list)

def save_results(result,filename):
    with open(filename,"w") as file:
        json.dump(result, file, ensure_ascii=False, indent=2) 