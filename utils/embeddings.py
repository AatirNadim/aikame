import faiss
import os
import click
import numpy as np
from sentence_transformers import SentenceTransformer
from .constants import Constants
from langchain.vectorstores import chroma


model = SentenceTransformer(model_name_or_path=Constants.model_label)


def create_parent_directory():
  '''
          Create parent directory if it does not exist.
  '''
  try:
    if not os.path.exists(Constants.parent_path):
      click.secho(f'Creating parent directory at {Constants.parent_path}', fg='green')
      os.makedirs(Constants.parent_path)
  except Exception as e:
    raise Exception(f"Error creating parent directory: {e}")


def update_central_ledger(key, path_of_embedding):
  click.secho(f'Updating central ledger with key: {key} and path: {path_of_embedding}', fg='green')
  try:
    central_ledger = os.path.join(Constants.parent_path, 'central_ledger.txt')
    if not os.path.exists(central_ledger):
      click.secho(f'Creating file at {central_ledger}', fg='green')
      with open(central_ledger, 'w') as f:
        f.write(f'{key} : {path_of_embedding}\n')
      return
    with open(central_ledger, 'a') as f:
      f.write(f'{key} : {path_of_embedding}\n')
  except Exception as e:
    raise Exception(f"Error updating central ledger: {e}")


def store_embeddings(embeddings, path_of_embedding: str) -> tuple:
  click.secho(f'Storing embeddings at {path_of_embedding}', fg='green')
  try:
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings, dtype=np.float32))

    path_of_embedding = os.path.join(Constants.parent_path, path_of_embedding)

    if not os.path.exists(path_of_embedding):
      click.secho(f'Creating file at {path_of_embedding}', fg='green')
      with open(path_of_embedding, 'w') as f:
        pass
    faiss.write_index(index, path_of_embedding)
  except Exception as e:
    raise Exception(f"Error storing embeddings: {e}")


def create_embedding(texts: list[str]):
  try:
    click.secho(f'Creating embeddings for {len(texts)} texts', fg='green')
    embeddings = model.encode(
      texts, show_progress_bar=True, batch_size=Constants.chunk_size)
    click.secho(f'Embeddings created for {len(texts)} texts', fg='green')
    click.secho(f'Embedding shape: {embeddings.shape}', fg='green')
    click.secho(f'Embedding size: {embeddings}', fg='green')
    return embeddings
  except Exception as e:
    raise Exception(f"Error creating embeddings: {e}")


def create_and_store_embeddings(chunks: list[str], key):
  try:
    # Store embeddings in ChromaDB (persistent storage)
    vector_db = chroma.Chroma.from_documents(
documents=chunks,
embedding=model,
persist_directory="./chroma_db"
    )
    vector_db.persist()
  except Exception as e:
    click.secho(f"Error in embedding the given chunks: \n{e}", fg='red')
    raise e


def embeddings_wrapper(texts: list[str], key, path_of_embedding: str):
  try:
    # embeddings = create_embedding(texts)

    create_parent_directory()
    # store_embeddings(embeddings, path_of_embedding)
    update_central_ledger(key, path_of_embedding)
  except Exception as e:
    click.secho(f"Error in embedding the given chunks: \n{e}", fg='red')
    raise e
