import logging

from learning_companion.graph.graph import app
from pprint import pprint

import vertexai
from learning_companion.config import Config

config = Config()
config.set_env_vars()
vertexai.init(project="adkaspar-sandbox")

question1 = "What is a cluster in BigQuery?"
inputs = {"question": question1}

for output in app.stream(inputs, config={"configurable": {"thread_id": "2"}}):
    for key, value in output.items():
        pprint(f"Finished running: {key}:")
        pprint(value["generation"])