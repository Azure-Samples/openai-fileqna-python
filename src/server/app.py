from __future__ import print_function
from config import *

import os
import tiktoken
import uuid
import sys
import logging
import openai
import azure.identity
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask import request

from handle_file import handle_file
from answer_question import get_answer_from_files

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def load_redis_index():
    import redis
    from redis.commands.search.indexDefinition import (
        IndexDefinition,
        IndexType
    )
    from redis.commands.search.field import (
        TextField,
        VectorField,
    )

    # Connect to Redis
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD
    )

    id = TextField(name="id")
    filename = TextField(name="filename")
    embedding = VectorField("embedding",
        "FLAT", {
            "TYPE": "FLOAT32",
            "DIM": EMBEDDING_DIMENSION,
            "DISTANCE_METRIC": DISTANCE_METRIC,
        }
    )
    fields = [id, filename, embedding]

    # Check if index exists
    try:
        redis_client.ft(INDEX_NAME).info()
        print("Index already exists")
    except:
        # Create RediSearch Index
        redis_client.ft(INDEX_NAME).create_index(
            fields = fields,
            definition = IndexDefinition(prefix=INDEX_PREFIX, index_type=IndexType.HASH)
    )
    return redis_client

def create_app():
    # init openai
    openai.api_type = "azure_ad"  # using azure endpoints with AAD auth
    openai.api_base = os.environ["OPENAI_API_BASE"]  # the endpoint value
    openai.api_version = "2023-03-15-preview"  # API version, subject to change
    credential = azure.identity.DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    openai.api_key = token.token  # set the key to the value of the AccessToken

    redis_index = load_redis_index()
    tokenizer = tiktoken.get_encoding("gpt2")
    session_id = str(uuid.uuid4().hex)
    app = Flask(__name__)
    app.redis_index = redis_index
    app.tokenizer = tokenizer
    app.session_id = session_id
    # log session id
    logging.info(f"session_id: {session_id}")
    app.config["file_text_dict"] = {}
    CORS(app, supports_credentials=True)

    return app

app = create_app()

@app.route(f"/process_file", methods=["POST"])
@cross_origin(supports_credentials=True)
def process_file():
    try:
        file = request.files['file']
        logging.info(str(file))
        handle_file(
            file, app.session_id, app.redis_index, app.tokenizer)
        return jsonify({"success": True})
    except Exception as e:
        logging.error(str(e))
        return jsonify({"success": False})

@app.route(f"/answer_question", methods=["POST"])
@cross_origin(supports_credentials=True)
def answer_question():
    try:
        params = request.get_json()
        question = params["question"]

        answer_question_response = get_answer_from_files(
            question, app.session_id, app.redis_index)
        return answer_question_response
    except Exception as e:
        return str(e)

@app.route("/healthcheck", methods=["GET"])
@cross_origin(supports_credentials=True)
def healthcheck():
    return "OK"

if __name__ == "__main__":
    app.run(debug=True, port=SERVER_PORT, threaded=True)
