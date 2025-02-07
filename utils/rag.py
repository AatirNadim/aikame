
from .constants import Constants
from .crud_files import documentStore
from .exceptions import NotEnoughContextError
from .llm_integrations.gemini import GeminiPlugin
import faiss
import numpy as np
import click
import os
import json
from openai import OpenAI


# Format of the chat history:
# [
#   {
#     role: <"user" | "system" | "assistant">,
#     content: <str>
# 	}
# ]

class Chat:

  def __init__(self):
    self.geminiPlugin = GeminiPlugin()

  def upsert_chat(self, query: str, response: str):
    try:
      history = self.load_chat()
      history.append({"role": "user", "content": query})
      history.append({"role": "assistant", "content": response})
      history = history[-Constants.max_history_length:]
      with open(Constants.chat_history_file, 'w') as f:
        json.dump(history, f)
    except Exception as e:
      raise e

  def load_chat(self) -> list[str]:
    try:
      if not Constants.chat_history_file.exists():
        return []
      with open(Constants.chat_history_file, 'r') as f:
        return json.load(f)
    except Exception as e:
      raise e

  def load_context(self, query: str) -> str:
    try:
      '''Load the context from the chat history.'''
      click.secho(f"Loading context for query", fg="yellow")
      question_embedding = Constants.embedding_model.encode(query).tolist()
      results = Constants.collection.query(
                                                      query_embeddings=[
                                                        question_embedding],
                                                      n_results=Constants.relevant_items
                                      )
      if not results["documents"][0]:
        raise NotEnoughContextError(
                "I don't have enough context to answer your question.")

      return "\n".join(results["documents"][0])
    except Exception as e:
      raise e

  def handle_query(self, query: str) -> str:
    try:
      chat_history = self.load_chat()
      click.secho(f"\n\nChat history: {chat_history}\n\n", fg="yellow")
      context = self.load_context(query)
      click.secho("Relevant context has been loaded succesfully")
      # response = ai_client.chat.completions.create(
      #   model=Constants.llm_model,
      #   messages=[{"role": "system", "content": Constants.prompt_template},{"role": "user", "content": f"Chat history:\n{chat_history}\nContext:\n{context}\n\nQuestion: {query}\n"}])
      response = self.geminiPlugin.invoke(
        query=query, chat_history=chat_history, context=context)
      click.secho("recied response from llm", fg="green")
      self.upsert_chat(query, response)
      return response
    except Exception as e:
      raise e


chat_instance = Chat()
ai_client = OpenAI(
  api_key=Constants.api_key
)


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
