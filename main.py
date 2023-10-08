import logging
import time
import arg
from get_dataset import get_dataset
from models.api_base import APIBase
from call_api import call_api
import utils
from check_and_parse import answer_validation,parse_answer
from tqdm import tqdm
from evaluation import evaluate
if __name__ == '__main__':
    current_time = int(time.time())
    logging.basicConfig(filename='./logs/{}.log'.format(current_time),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
    args = arg.get_command_line_args()
    filename=f'./result/{args.dataset}_{args.mode}_{args.scenario}_{args.k}_{current_time}.json'
    result=[]
    if args.mode=='gen':
        prompt_list_list=[]
        for try_id in range(6):
            prompt_list_list.append(get_dataset(args.dataset,mode='gen',scenario=args.scenario,k=args.k,tries=try_id))
        end=utils.get_end(prompt_list_list[0],args.end)
        result=[]
        abnormal=0
        for idx in tqdm(range(args.begin,end)):
            retries=0
            while retries<24:
                print(f"idx: {idx},\t retries: {retries}")
                out=call_api(prompt_list_list[retries%6][idx],temperature=utils.get_temp(retries),max_tokens=3000)
                if answer_validation(out['result'],args.dataset,args.scenario,args.k):
                    result.append(out)
                    break
                retries+=1
            if retries==24:
                assert args.dataset=='MATH' and args.scenario=='cot', "Model couldn't generate demonstrations in 24 retries, please try again from this index."
                result.append({'idx':idx,'result':None})
                abnormal+=1
                

            utils.save_results(result,filename)
        assert abnormal<=30,  "too much faliure, please post an issue on the github repository."
        print(f"total number of faliure: {abnormal}")
        parse_answer(utils.automatic_concatenate_and_read(args.dataset,'gen',args.scenario,args.k),args.dataset,args.scenario,args.k)
        print("Parse output successfully.")
                






    elif args.mode=='test':
        
        prompt_list=get_dataset(args.dataset,mode='test',scenario=args.scenario,k=args.k)  
        end=utils.get_end(prompt_list,args.end)
        result=[]
        for idx in tqdm(range(args.begin,end)):
            out=call_api(prompt_list[idx],max_tokens=800)
            result.append(out)
            utils.save_results(result,filename)

        evaluate(args.dataset,mode='test',scenario=args.scenario,k=args.k)

        #todo: add evaluation

    elif args.mode=='all':
        prompt_list_list=[]
        for try_id in range(6):
            prompt_list_list.append(get_dataset(args.dataset,mode='gen',scenario=args.scenario,k=args.k,tries=try_id))
        end=utils.get_end(prompt_list_list[0],args.end)
        result=[]
        filename=f'./result/{args.dataset}_{args.mode}_{args.scenario}_gen_{args.k}.json'
        abnormal=0
        for idx in tqdm(range(args.begin,end)):
            retries=0
            while retries<24:
                print(f"idx: {idx},\t retries: {retries}")
                out=call_api(prompt_list_list[retries%6][idx],temperature=utils.get_temp(retries),max_tokens=3000)
                if answer_validation(out['result'],args.dataset,args.scenario,args.k):
                    result.append(out)
                    break
                retries+=1
            if retries==24:
                assert args.dataset=='MATH' and args.scenario=='cot', "Model couldn't generate demonstrations in 24 retries, please try again from this index."
                result.append({'idx':idx,'result':None})
                abnormal+=1
                

            utils.save_results(result,filename)

        assert abnormal<=30,  "too much faliure, please post an issue on the github repository."
        print(f"total number of faliure: {abnormal}")
        parse_answer(utils.automatic_concatenate_and_read(args.dataset,'gen',args.scenario,args.k),args.dataset,args.scenario,args.k)
        

# parse and cleaning



        filename=f'./result/{args.dataset}_{args.mode}_{args.scenario}_test_{args.k}.json'
        prompt_list=get_dataset(args.dataset,mode='test',scenario=args.scenario,k=args.k) 
        end=utils.get_end(prompt_list,args.end)
        for idx in tqdm(range(args.begin,end)):
            out=call_api(prompt_list[idx],max_tokens=800)
            result.append(out)
            utils.save_results(result,filename)

        evaluate(args.dataset,mode='test',scenario=args.scenario,k=args.k)
    else:
        raise NotImplementedError 