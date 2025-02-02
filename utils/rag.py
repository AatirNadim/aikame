
from .constants import Constants
import faiss
import numpy as np
import click
import os


# get all the embeddings to get the context of the question

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
  get_context_for_query(query)
