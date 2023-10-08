import argparse
def get_command_line_args():
    parser = argparse.ArgumentParser(description='SEC')
    parser.add_argument('--dataset', default='GSM8k', type=str,choices=["GSM8k", "MATH", "ARC","MMLU","Ceval",'HumanEval'])
    parser.add_argument('--mode', default='test', type=str,choices=['test','gen','all'])
    parser.add_argument('--scenario', type=str, default='van',choices=['van','cot'])
    parser.add_argument('--k', type=int, default=4)
    parser.add_argument('--begin', type=int, default=0)
    parser.add_argument('--end', type=int, default=-1)
    args = parser.parse_args()
    return args