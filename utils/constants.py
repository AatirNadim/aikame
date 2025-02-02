import os
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

'''
	Constants for the project.
	They can be set as environment variables.
'''


class Constants:
  """
  Constants for the project.
  They can be set as environment variables.
  """
  parent_path: Path = os.environ.get(
    "parent_path", Path.home() / ".aikame-dump")
  docs_dir: Path = parent_path / "documents"
  metadata_file = parent_path / "metadata.json"
  chat_history_file = parent_path / "chat_history.json"
  max_history_length = os.environ.get("max_history_length", 5)
  relevant_items = os.environ.get("relevant_items", 3)
  chunk_size = os.environ.get("chunk_size", 256)
  overlap = os.environ.get("overlap", 50)
  model_label = os.environ.get("model_label", 'all-MiniLM-L6-v2')
  llm_model = os.environ.get("llm_model", "gpt-4")
  api_key = os.environ.get("llm_api_key")
  if(api_key is None):
    raise ValueError("API key for LLM not found.")

  embedding_model = SentenceTransformer(model_label)

  local_db = chromadb.PersistentClient(path=str(parent_path / "chromadb"))
  collection = local_db.get_or_create_collection("documents")

  prompt_template = """Use the added context to answer all the questions given to you. If you don't know the answer, just say that you don't know, don't try to make up an answer. Keep the answer as relevant as possible and explain all the important points coherently. Always say "thanks for asking!" at the end of the answer."""
