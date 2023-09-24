import logging
import time
import arg
from get_dataset import get_dataset
from models.api_base import APIBase
from call_api import call_api
import utils
if __name__ == '__main__':
    current_time = int(time.time())
    logging.basicConfig(filename='./logs/{}.log'.format(current_time),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
    args = arg.get_command_line_args()
    filename=f'./result/{args.dataset}_{args.mode}_{args.scenario}_{args.k}.json'
    result=[]
    if args.mode=='gen':
        prompt_list=get_dataset(args.dataset,mode='gen',scenario=args.scenario,k=args.k)
        end=utils.get_end(prompt_list,args.end)
        result=[]
        
        for idx in range(args.begin,end):
            retries=0
            while retries<10:
                out=call_api(prompt_list[idx])
            






    elif args.mode=='test':
        prompt_list=get_dataset(args.dataset,mode='test',scenario=args.scenario,k=args.k)  
        end=utils.get_end(prompt_list,args.end)
        result=[]
        for idx in range(args.begin,end):
            out=call_api(prompt_list[idx])
            result.append({'idx':idx,'result':out})
            utils.save_results(result,filename)

        #todo: add evaluation

    elif args.mode=='all':
        prompt_list=get_dataset(args.dataset,mode='gen',scenario=args.scenario,k=args.k)
        end=utils.get_end(prompt_list,args.end) 
        for idx in range(args.begin,end): 
            pass
        prompt_list=get_dataset(args.dataset,mode='test',scenario=args.scenario,k=args.k) 
        end=utils.get_end(prompt_list,args.end)
        for idx in range(args.begin,end):
            pass
    else:
        raise NotImplementedError 