# Self-Contemplation Prompting (SEC for short)

Source code for paper [Are Human-generated Demonstrations Necessary for In-context Learning](https://arxiv.org/abs/2309.14681)

---------
### Main Results
#### Table: Comparison between SEC and ICL in both CoT and answer only scenarios. SEC reaches comparable results to ICL. Some of our results differ from the published results, which might be due to that the experiments was conducted on different model checkpoints.
#### Any result encompassed within brackets signifies data derived from zero-shot prompting. The subscript denotes the number of employed shots for published results. For example, <sub>5</sub> means 5-shot scenario. For our own experiments, the number of shots are shown in Table (link to the specific table).
#### The superscripts are used to indicate results that have been cited from previous studies: <sup>a</sup>[1], <sup>b</sup>[2], <sup>c</sup>[3].

| Prompting Strategies | MATH | GSM8K | MMLU Math | C-Eval STEM | ARC | MMLU | C-Eval | Human Eval |
|----------------------|------|-------|-----------|-------------|-----|------|--------|------------|
|                      |      |       |           |             |     |      |        |            |
| **Published Results**||
| *Vanilla ICL*        | -    | 57.1<sup>a</sup><sub>5</sub> | -       | [49.0<sup>c</sup><sub>0</sub>]  | 85.2<sup>a</sup><sub>25</sub> | 70.0<sup>a</sup><sub>5</sub> | [51.0<sup>c</sup><sub>0</sub>] | [48.1<sup>a</sup><sub>0</sub>] |
| *CoT-ICL*            | -    | 74.9<sup>b</sup><sub>8</sub> | 51.1<sup>b</sup><sub>5</sub> | 52.9<sup>c</sup><sub>5</sub>   | -         | 67.3<sup>b</sup><sub>5</sub> | 54.6<sup>c</sup><sub>5</sub>   | -          |
|                      |      |       |           |             |     |      |        |            |
| **Our Results**      ||
| *Zero-shot*          | 16.6 | 31.4  | 46.4      | 48.1        | 80.1| 64.7 | 51.0    | 48.8       |
| *Vanilla ICL*        | 20.3 | 57.1^a | 45.1     | **53.2**    | 86.5| 70.4 | **55.0**| 73.8       |
| *Vanilla SEC*        | 18.1 | 65.4  | 45.9      | 52.3        | 85.9| 68.3 | 54.0    | **75.6**   |
|                      | (-2.2)| (+8.3) | (+0.8)  | (-0.9)      | (-0.6)| (-2.1) | (-1.0)  | (+2.8)    |
| *CoT-ICL*            | 31.2 | **77.4** | **58.3**| 50.5       | **87.9**| 69.6 | 53.1   | -          |
| *CoT-SEC*            | **33.5** | 77.0 | 56.6    | 51.8       | 86.9| **71.4** | 54.6    | -          |
|                      | (+2.3)| (-0.4) | (-1.7)  | (+1.3)      | (-1.0)| (+1.8) | (+1.5)  | -          |

#### References
1. openai2023gpt4
2. fu2023chain
3. huang2023c




### Environment Setup

```
pip install numpy
pip install openai
pip install datasets
pip install human_eval
pip install python-json-logger
```

### Usage

```sh
python main.py  [--dataset DATASET] [--mode MODE] [--scenario SCENARIO] [--k K] [--begin BEGIN] [--end END--end]
```

### Arguments

- `--dataset`: Specifies the name of dataset. Default is "GSM8k". Choices are ["GSM8k" , "MATH" , "ARC" , "MMLU" , "C-Eval" , "HumanEval"].
- `--mode`: Specifies the mode of this execution. Default is "test". Choices are ["test" , "gen" , "all"]. "gen" means that the program is executing the SEC Demonstration Generation part. "test" means that the program is executing the evaluation part (ICL part). "all" means both parts should be executed.
- `--scenario`: Specifies the scenario of this execution. Default is "van". Choices are ["van" , "cot"]. "van" means vanilla SEC, and "cot" means CoT-SEC.
- `--k`: Specifies the number of demonstrations used for evaluation. Default is 4.
- `--scenario`: Specifies the scenario of this execution. Default is "van". Choices are ["van" , "cot"]. "van" means vanilla SEC, and "cot" means CoT-SEC.
- `--begin`: Specifies the beginning index for the execution. Default is 0.
- `--end`: Specifies the ending index for the execution. Default is -1.

### Examples

Run the whole process of vanilla SEC for the GSM8k dataset:

```sh
python main.py --dataset GSM8k --mode all --scenario van --k 5 
```

Run only the SEC Demonstration Generation part of CoT-SEC for the GSM8k dataset:

```sh
python main.py --dataset GSM8k --mode gen --scenario cot --k 5 
```

Run only the evaluation part of CoT-SEC for the MATH dataset from index 1000 to index 3000:

```sh  
python main.py --dataset MATH --mode test --scenario cot --k 4 --begin 1000 --end 3000
```

### Preprocessed datasets and model-generated demonstrations

Preprocessed datasets and model-generated demonstrations can be downloaded by this [link](https://drive.google.com/file/d/1ZCD0a_nmkPxWv2FlG6QN0uJ1kZ9nNRej/view?usp=share_link). Please unzip the file to `/data`.

### For Ceval and HumanEval

The evaluation of these two datasets relies on external packages or submission. The target file of the outcome of thw two dataset will be stored under directory evaluation_result. For Ceval, you need to submit to its [official website](https://cevalbenchmark.com). For HumanEval, you need to follow the instructions under it's [github repository](https://github.com/openai/human-eval).

### Some tips

- Cosidering that calling API is a long process and some of our dataset (MMLU and Ceval) contains more than 10k examples, our code allows execution on data within a specified index range. You just need to add the start and end index in the cmd instruction.
- If there is an error calling the API due to network issues or other problems, you just need to continue executing from where it was interrupted.
- Our code supports reading information from multiple files. All you need is for the filenames to be arranged in ascending order based on their index and make sure that the arguments for each file is the same. Therefore, continuing execution from the interrupted position will not affect subsequent results.
- If the pipeline reports  an error of "Model couldn't generate demonstrations in 24 retries, please try again from this index.", the best way to solve this is try again. In almost all cases, since the randomness in LLMs, this successfully solve the problem. If this error still exists after several tries, please post an issue on github or email me.
- Considering the long process of both two phase, we highly recommend you do it separately instead of execute two phases at once.

### Citation

```
@article{li2023human,
  title={Are Human-generated Demonstrations Necessary for In-context Learning?},
  author={Li, Rui and Wang, Guoyin and Li, Jiwei},
  journal={arXiv preprint arXiv:2309.14681},
  year={2023}
}
```