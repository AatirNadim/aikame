import os
import json
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

'''
        Constants for the project.
        They can be set as environment variables.
'''


class Constants:
  """
  Constants for the project.
  They can be set as environment variables.
  """
  class EntityRole:
    user = "user"
    assistant = "assistant"
    system = "system"

  class MessageInstance:
    def __init__(self, role: "Constants.EntityRole", content: str):
      self.role = role
      self.content = content
    
    def toDict(self) -> str:
      return {
        'role': self.role,
        'content': self.content
      }

    @staticmethod
    def object_hook(dct):
      pass

    @staticmethod
    def fromDict(dct: dict):
      return Constants.MessageInstance(
        role=dct['role'], content=dct['content']
      )

  # give path to the env file if required
  load_dotenv()
  parent_path: Path = os.environ.get(
    "parent_path", Path.home() / ".aikame-dump")
  docs_dir: Path = parent_path / "documents"
  metadata_file = parent_path / "metadata.json"
  chat_history_file = parent_path / "chat_history.json"
  max_history_length = os.environ.get("max_history_length", 7)
  relevant_items = os.environ.get("relevant_items", 3)
  chunk_size = os.environ.get("chunk_size", 256)
  overlap = os.environ.get("overlap", 50)
  model_label = os.environ.get("model_label", 'all-MiniLM-L6-v2')

  # models
  gpt_model = os.environ.get("llm_model", "gpt-3.5-turbo")
  gemini_model = os.environ.get("gemini_model", "gemini-2.0-flash")
  anthropic_model = os.environ.get("anthropic_model", "claude-v1")

  # api keys
  gpt_api_key = os.environ.get("llm_api_key")
  gemini_api_key = os.environ.get("gemini_api_key")
  anthropic_api_key = os.environ.get("anthropic_api_key")

  embedding_model = SentenceTransformer(model_label)

  local_db = chromadb.PersistentClient(path=str(parent_path / "chromadb"))
  collection = local_db.get_or_create_collection("documents-testing")

  prompt_template = """Dont give the response in markdown format.
  Use the added context to answer all the questions given to you. If you don't know the answer, just say that you don't know, don't try to make up an answer. 
  You can consult your training data if explicitly mentioned in the user prompt. 
  Keep the answer as relevant as possible and explain all the important points coherently. Please note that the response you give will be output as cli command response, so use the text format appropriate for user-friendly console print and not the markdown format. 
  Always say "thanks for asking!" at the end of the answer and ask the user for a possible follow-up."""

  no_inline_query = "no_inline_query"

  random_id = "dbf8f69d-60ba-4e37-8a2d-17ca14371d36"
