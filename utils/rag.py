
from .constants import Constants
from .crud_files import documentStore
from .exceptions import NotEnoughContextError
import faiss
import numpy as np
import click
import os
import json


class Chat:
  def upsert_chat(self, query: str, response: str):
    history = self.load_chat()
    history.append({"query": query, "response": response})
    history = history[-Constants.max_history_length:]
    with open(Constants.chat_history_file, 'w') as f:
      json.dump(history, f)

  def load_chat(self) -> list[dict]:
    if not Constants.chat_history_file.exists():
      return []
    with open(Constants.chat_history_file, 'r') as f:
      return json.load(f)

  def load_context(self, query: str) -> str:
    '''Load the context from the chat history.'''
    question_embedding = Constants.embedding_model.encode(query).tolist()
    results = Constants.collection.query(
                query_embeddings=[question_embedding],
                n_results=Constants.relevant_items
            )
    if not results["documents"][0]:
      raise NotEnoughContextError(
        "I don't have enough context to answer your question.")

    return "\n".join(results["documents"][0])

  def handle_query(self, query: str) -> str:
    chat_history = self.load_chat()
    context = self.load_context(query)
    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": Constants.prompt_template},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ]
            )
    self.upsert_chat(query, response)
    return response.choices[0].message.content


chat_instance = Chat()


def embed_query(query: str):
  '''
          Embed a query using the model.
  '''
  return Constants.embedding_model.encode([query], show_progress_bar=False)


def merge_indices() :
  pass


def get_context_util(query: str, file_path: str, k: int = 1):
  try:
    index = faiss.read_index(file_path)
    query_embedding = embed_query(query)
    distances, indices = index.search(
      np.array(query_embedding, dtype=np.float32), k)
    click.echo(f"Distances: {distances}")
    click.echo(f"Indices: {indices}")
  except Exception as e:
    raise e


def get_context_for_query(query: str):
  '''
          Get the context for a query.
  '''
  click.echo(f"Getting context for query: {query}")
  try:
    click.secho(f"Searching for all relevant files in context", fg="yellow")
    for file_path in os.listdir(Constants.parent_path):
      if file_path.endswith('.index'):
        get_context_util(query, os.path.join(Constants.parent_path, file_path))
  except Exception as e:
    raise e


@click.command()
@click.argument("query", type=str)
def query(query: str):
  '''
          Query the model for a context.
  '''
  click.secho(f"Querying the model for context: {query}", fg="green")
  click.secho(chat_instance.handle_query(query), fg="green")
