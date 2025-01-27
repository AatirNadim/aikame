import os

'''
	Constants for the project.
	They can be set as environment variables.
'''

parent_path = os.environ.get("parent_path", "./data")

chunk_size = os.environ.get("chunk_size", 256)

model_label = os.environ.get("model_label", 'all-MiniLM-L6-v2')

llm_model = os.environ.get("llm_model", "gpt-4")

# please set the api key as an environment variable
api_key = os.environ.get("llm_api_key")


prompt_template = """Use the added context to answer all the questions given to you.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Keep the answer as relevant as possible and explain all the important points coherently.
Always say "thanks for asking!" at the end of the answer."""


# query_template = """Use the added context to answer all the questions given to you.