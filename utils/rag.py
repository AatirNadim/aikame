
from .constants import Constants
from .exceptions import NotEnoughContextError
from .llm_integrations.gemini import GeminiPlugin
import faiss
import numpy as np
import click
import os
import json
from pathlib import Path
from openai import OpenAI
import tkinter as tk
from tkinter import filedialog


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
      history.append(Constants.MessageInstance(
        role=Constants.EntityRole.user, content=query))
      history.append(Constants.MessageInstance(
        role=Constants.EntityRole.assistant, content=response))
      history = history[-Constants.max_history_length:]
      history = [itr.toDict() for itr in history]

      with open(Constants.chat_history_file, 'w') as f:
        json.dump(history, f)
    except Exception as e:
      raise e

  @staticmethod
  def load_chat() -> list[Constants.MessageInstance]:
    try:
      if not Constants.chat_history_file.exists():
        return []
      with open(Constants.chat_history_file, 'r') as f:
        history = json.load(f)
        return [Constants.MessageInstance.fromDict(itr) for itr in history]
    except Exception as e:
      raise e
    
  @staticmethod
  def clear_chat():
    try:
      with open(Constants.chat_history_file, 'w') as f:
        json.dump([], f)
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

  def handle_dedicated_chat(self):
    '''
		Handle a dedicated chat.
		'''
    click.secho("Starting a dedicated chat\nPlease type `exit` to end the dedicated chat", fg="yellow")
    click.echo("Agent:\nHello! How can I help you today?")
    while True:
      click.secho("User: ", fg="yellow")
      query = input()
      if query == "exit":
        break
      click.secho("Agent: ", fg="green")
      self.handle_query(query)

  def handle_query(self, query: str) -> None:
    try:
      chat_history = self.load_chat()
      # click.secho(f"\n\nChat history: {chat_history}\n\n", fg="yellow")
      context = self.load_context(query)
      # click.secho("Relevant context has been loaded succesfully")
      # response = ai_client.chat.completions.create(
      #   model=Constants.llm_model,
      #   messages=[{"role": "system", "content": Constants.prompt_template},{"role": "user", "content": f"Chat history:\n{chat_history}\nContext:\n{context}\n\nQuestion: {query}\n"}])
      response = self.geminiPlugin.invoke(
        query=query, chat_history=chat_history, context=context)

      self.upsert_chat(query, response)
      # return response
    except Exception as e:
      raise e


chat_instance = Chat()
# ai_client = OpenAI(
#   api_key=Constants.api_key
# )


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
  

  
# returns the dir path including the file name

def select_save_location() -> str:
  root = tk.Tk()
  root.withdraw()
  
  file_path = filedialog.asksaveasfilename(
      title="Select Location to Save Chat History",
      defaultextension=".json",
      initialfile="chat_history.json",
      filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
  )
  print("the path from the window is ", file_path)
  return file_path

@click.command(name="ask")
# @click.argument("query", type=str, cls=)
@click.option("--query", "-q", type=str, help="Query for the model", default=Constants.no_inline_query)
def query(query: str):
  '''
    Query the model for a context.
  '''
  if query == Constants.no_inline_query:
    chat_instance.handle_dedicated_chat()
    return
  click.secho(f"Querying the model for context: {query}", fg="green")
  chat_instance.handle_query(query)


@click.command(name="export_chat")
@click.option("--file_path", "-f", type=str, help="File path to export the chat history", default = Constants.random_id)
def export_chat(file_path: str):
  '''
    Export the chat history to a location of your choosing.

    Args:
    file_path: str: The file path to export the chat history eg(./example.json). 
                    Note: The file path should have a .json extension.
    (Optional) In case the file path is not provided, the user will be prompted to select a location to save the chat history.

  '''
  try:
    if file_path == Constants.random_id:
      file_path = select_save_location()
    chat_history = chat_instance.load_chat()
    if not os.path.exists(os.path.dirname(file_path)):
      os.makedirs(os.path.dirname(file_path))
    with open(Path.absolute(Path(file_path)), 'w') as f:
      json.dump([itr.toDict() for itr in chat_history], f)
  except Exception as e:
    raise e
