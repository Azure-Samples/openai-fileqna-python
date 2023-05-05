import openai
import logging
import sys
import time

from config import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_redis_id_for_file_chunk(session_id, filename, chunk_index):
    return str(INDEX_PREFIX+session_id+"-"+filename+"-"+str(chunk_index))

def get_embedding(text, deployment_id):
    return openai.Embedding.create(input=text, deployment_id=deployment_id)['data'][0]['embedding']

def get_embeddings(text_array, deployment_id):
    # Parameters for exponential backoff
    max_retries = 5 # Maximum number of retries
    base_delay = 1 # Base delay in seconds
    factor = 2 # Factor to multiply the delay by after each retry
    results = []
    for text in text_array:
        while True:
            try:
                result = openai.Embedding.create(input=text, deployment_id=deployment_id)['data'][0]
                results.append(result)
                break
            except Exception as e:
                if max_retries > 0:
                    logging.info(f"Request failed. Retrying in {base_delay} seconds.")
                    time.sleep(base_delay)
                    max_retries -= 1
                    base_delay *= factor
                else:
                    raise e
    return results
