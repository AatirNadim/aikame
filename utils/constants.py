import os

'''
	Constants for the project.
	They can be set as environment variables.
'''

parent_path = os.environ.get("parent_path", "./data")

chunk_size = os.environ.get("chunk_size", 256)

model_label = os.environ.get("model_label", 'all-MiniLM-L6-v2')

# please set the api key as an environment variable
api_key = os.environ.get("llm_api_key")


prompt_template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.
Always say "thanks for asking!" at the end of the answer.

{context}

Question: {question}

Helpful Answer:"""