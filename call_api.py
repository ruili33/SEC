import os.path
import sys
sys.path.append(".")
from models.api_base import APIBase
from logger import get_logger
logger = get_logger(__name__)
os.environ["OPENAI_API_KEY"] = "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"
def call_api(prompt,temperature=0,engine="gpt-3.5-turbo",max_tokens=1000):
    client=APIBase(
            engine=engine,
            temperature=temperature,
            top_p=1.0,
            max_tokens=max_tokens,
            frequency_penalty=0,
            presence_penalty=0,
            best_of=1,
        )
    result=[]
    result.append(client.get_multiple_sample(prompt))
    return result[0]
