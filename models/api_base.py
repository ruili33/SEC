# encoding: utf-8
"""
@author: Xiaofei Sun
@contact: xiaofei_sun@shannonai.com
@time: 2022/08/18
@desc: 这只飞很懒
"""
import os
import random
import time
from math import ceil
from typing import List

import openai
from tqdm import tqdm
import openai.error as openai_error

from logger import get_logger

logger = get_logger(__name__)

INIT_DELAY = 1
EXPONENTIAL_BASE = 1.3
MAX_RETRIES = 8 

import signal

class TimeoutError(Exception):
    pass

def timeout(seconds=8, error_message="Timeout Error: the function took too long to complete"):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wrapper
    return decorator


class APIBase(object):
    
    delay = INIT_DELAY

    def __init__(self, engine, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, best_of):
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.best_of = best_of
    
    def _get_multiple_sample(self, prompt_list: List[str],key=None):
        openai.api_key = os.environ["OPENAI_API_KEY"] if key is None else key  # 随机选择一个key
        response =  openai.ChatCompletion.create(
        model=self.engine,
        messages=prompt_list,
        max_tokens=self.max_tokens,
        temperature=self.temperature,
        )
       
        results = [choice.message["content"] for choice in response.choices]
       
        logger.info(msg=f"prompt_and_result", extra={"prompt_list": prompt_list, "results": results})
        return results

    def get_multiple_sample(
            self,
            prompt_list: List[str],
            jitter: bool = True,
    ):
        """
        Retry a function with exponential backoff.
        代码借鉴自 https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb 的 Example 3: Manual backoff implementation
        """
        errors: tuple = (openai.error.RateLimitError,openai_error.APIConnectionError,openai_error.APIError,openai_error.ServiceUnavailableError,TimeoutError,openai_error.Timeout)
        # Initialize variables
        num_retries = 0
        idx=prompt_list["idx"]
        prompt_list=prompt_list["prompt"]
        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            used_delay = APIBase.delay
            try:
                logger.info(f"Delay={used_delay - 1}")
                for _ in tqdm(range(ceil(used_delay - 1)), desc=f"sleep{used_delay - 1}"):
                    time.sleep(1)
                # time.sleep(used_delay - 1)  
                results = self._get_multiple_sample(prompt_list)[0]
                APIBase.delay = INIT_DELAY 
                return {"result":results,"idx":idx}
            except errors as e:
                logger.info(f"Retry")
                # Increment retries
                num_retries += 1
                # Check if max retries has been reached
                if num_retries > MAX_RETRIES:
                    logger.error(f"Retry Failed")
                    logger.error(f"Other Error")
                    raise Exception(f"Maximum number of retries ({MAX_RETRIES}) exceeded.")
                # Increment the delay
                APIBase.delay = max(APIBase.delay, used_delay * EXPONENTIAL_BASE * (1 + jitter * random.random()))
                # Sleep for the delay

            # Raise exceptions for any errors not specified
            except Exception as e:
                logger.error(f"Other Error")
                logger.error(e)
                raise e
