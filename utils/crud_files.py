import click
import os
import PyPDF2
import json
from datetime import datetime
from .embeddings import embeddings_wrapper
from .index import timing_decorator, get_embeddings_path_from_key
from .constants import Constants
from .exceptions import *
import shutil
import fileinput
from uuid import uuid4 as uuid
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.pdf import PyPDFLoader


acceptable_file_types = [".txt", ".pdf"]


class DocumentStore:

  def __init__(self):
    self._init_directories()
    self.embedding_model = Constants.embedding_model

  def _init_directories(self):
    """Initialize necessary directories and files."""
    Constants.parent_path.mkdir(exist_ok=True)
    Constants.docs_dir.mkdir(exist_ok=True)

    if not Constants.metadata_file.exists():
      self._save_metadata({})

  def _save_metadata(self, metadata: dict):
    """Save metadata to file."""
    with open(Constants.metadata_file, 'w') as f:
      json.dump(metadata, f)

  def _load_metadata(self) -> dict:
    """Load metadata from file."""
    if Constants.metadata_file.exists():
      with open(Constants.metadata_file, 'r') as f:
        return json.load(f)
    return {}

  def _process_document(self, file_path: Path):
    """Process a document and return chunks."""
    if file_path.suffix.lower() not in acceptable_file_types:
      raise ValueError(f"Unsupported file type: {file_path.suffix.lower()}")
    if file_path.suffix.lower() == '.pdf':
      loader = PyPDFLoader(str(file_path))
    else:
      loader = TextLoader(str(file_path))

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=Constants.chunk_size,
                    chunk_overlap=Constants.overlap
    )
    return text_splitter.split_documents(documents)

  def add_document(self, file_path: Path):
    """Add a document to the system."""
    try:
      # Process document into chunks
      chunks = self._process_document(file_path)
      click.secho(f"Document processed into {len(chunks)} chunks.", fg="green")

      # Generate embeddings and add to ChromaDB
      texts = [chunk.page_content for chunk in chunks]
      embeddings = self.embedding_model.encode(texts).tolist()
      click.secho(f"Embeddings generated for {len(chunks)} chunks.", fg="green")

      # Generate IDs for chunks
      doc_id = str(file_path.stem)
      ids = [f"{doc_id}_{i}" for i in range(len(chunks))]

      click.secho(f"IDs generated for chunks: \n{ids}\n", fg="green")

      # Add to ChromaDB
      Constants.collection.add(
              embeddings=embeddings,
              documents=texts,
              ids=ids,
              metadatas=[{"source": str(file_path)} for _ in chunks]
      )
      click.secho(f"Chunks added in local, for persistence.", fg="green")

      # Update metadata
      metadata = self._load_metadata()
      metadata[str(file_path)] = {
                      "chunks": len(chunks),
                      "ids": ids
      }
      self._save_metadata(metadata)
      click.secho(f"Metadata updated for document: {file_path}", fg="green")

    except ValueError as e:
      raise DocumentProcessingError(
              f"Error processing document {file_path}: {str(e)}")

    except Exception as e:
      raise DocumentProcessingError(
        f"Error processing document {file_path}: {str(e)}")

  def delete_document(self, file_path: Path):
    """Delete a specific document."""
    metadata = self._load_metadata()
    if str(file_path) not in metadata:
      raise FileNotFoundError(f"Document with path: {file_path}, not found.")
    for chunk_id in metadata[str(file_path)]["ids"]:
      Constants.collection.delete(ids=[chunk_id])
    click.secho(f"Document with path: {file_path}, has been removed.", fg="green")

    del metadata[str(file_path)]
    self._save_metadata(metadata)
    click.secho(f"Metadata for document with path: {file_path}, has been removed.", fg="green")

  def delete_all(self):
    """Delete all documents."""
    Constants.collection.delete(ids=Constants.collection.get()["ids"])
    self._save_metadata({})

  def query(self, question: str, k: int = 3) -> str:
    """Query the system."""
    try:
      # Generate embedding for the question
      question_embedding = self.embedding_model.encode(question).tolist()

      # Query ChromaDB
      results = Constants.collection.query(
                      query_embeddings=[question_embedding],
                      n_results=k
      )

      if not results["documents"][0]:
        return "I don't have enough context to answer your question."

      # Prepare context for OpenAI
      context = "\n".join(results["documents"][0])

      # Query OpenAI
      # response = openai.ChatCompletion.create(
      #                 model="gpt-3.5-turbo",
      #                 messages=[
      #                                 {"role": "system", "content": "You are a helpful assistant. Answer the question based on the provided context."},
      #                                 {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}])

      # return response.choices[0].message.content

    except Exception as e:
      raise QueryProcessingError(f"Error processing query: {str(e)}")

  def list_documents(self) -> list[str]:
    """List all documents in the system."""
    metadata = self._load_metadata()
    return list(metadata.keys())


documentStore = DocumentStore()


def parse_and_extract_text(file_path: str) -> str:
  click.echo(f"Parsing and extracting text from pdf: {file_path}")
  pdf_file = open(file_path, "rb")
  pdf_reader = PyPDF2.PdfReader(pdf_file)
  text = ""
  for page in pdf_reader.pages:
    # page = pdf_reader.getPage(page_num)
    text += page.extract_text()
  pdf_file.close()
  return text


def load_util(file_path: str) -> str:
  try:
    if not os.path.isabs(file_path):
      click.secho(
        f"Path is relative, converting to absolute path...", fg="yellow")
      file_path = os.path.abspath(file_path)

    if file_path.split(".")[-1] not in acceptable_file_types:
      raise ValueError(f"Unsupported file type: {file_path.split('.')[-1]}")

    if file_path.endswith(".pdf"):
      return parse_and_extract_text(file_path)
    else:
      with open(file_path, "r") as file:
        return '\n'.join(file.readlines())
    click.secho(f"File parsed and read: {file_path}", fg="green")

  except IsADirectoryError:
    raise IsADirectoryError(f"Is a directory: {file_path}")
  except PermissionError:
    raise PermissionError(f"Permission denied: {file_path}")
  except IOError:
    raise IOError(f"Error loading file: {file_path}")
  except FileNotFoundError:
    raise FileNotFoundError(f"File not found: {file_path}")


def create_chunks(text: str, chunk_size: int) -> list[str]:
  """
  Create chunks of text from a given text of a specified size.
  """
  click.secho(f"Creating chunks of text...", bg="green")
  return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


@click.command(name="load_files")
@click.argument("file_paths", nargs=-1)
@click.pass_context
@timing_decorator
def load_files(ctx: click.Context, file_paths: tuple[str, ...]) -> list:
  """
  Load files from a list of (absolute) file paths. \n
  At the moment, this command only reads text files and pdfs and will throw errors for any other file type.
  """

  click.secho(f"Loading all files for context ...", bg="green")
  files_added = 0
  for file_path in file_paths:
    try:
      click.secho(f"Loading file: {file_path}", fg="yellow")
      # chunks = textSplitter.split_documents(
      #   load_util(file_path), chunk_size=chunk_size)
      # embeddings_wrapper(chunks, file_path, f"{uuid()}.index")
      documentStore.add_document(Path.absolute(Path(file_path)))
      files_added += 1
    except (RelativePathError, ValueError, IsADirectoryError, PermissionError, IOError, FileNotFoundError) as e:
      click.secho(e, fg="red")
      return None
  click.secho(f"Files loaded: {files_added}", fg="green")


@click.command(name="show_files")
@click.pass_context
@timing_decorator
def show_files(ctx: click.Context) -> None:
  """
  Show the files that have been loaded.
  """

  click.secho("Showing all files loaded...", fg="yellow")
  try:
    docs = documentStore.list_documents()
    if len(docs) > 0:
      for itr, doc in enumerate(docs):
        click.secho(f"{itr + 1}: {doc}", fg="green")
    else:
      click.secho("No files loaded.", fg="red")

  except FileNotFoundError:
    click.secho("No files loaded.", fg="red")
    return None
  except Exception as e:
    click.secho(f"Error showing files: {e}", fg="red")
    return None


@click.command(name="clear_context")
@timing_decorator
def clear_context() -> None:
  """
  Clear the context of the files loaded.
  """
  click.secho("Clearing all context and metadata...", fg="yellow")
  try:
    documentStore.delete_all()
    click.secho("Context cleared.", fg="green")
  except Exception as e:
    click.secho(f"Error clearing context: {e}", fg="red")
    return None


@click.command(name="remove_file")
@click.argument("file_path", type=str)
@click.pass_context
@timing_decorator
def remove_file(ctx: click.Context, file_path: str) -> None:
  """
  Remove a file from the context.
  """
  click.secho(f"Removing file: {file_path}", fg="yellow")
  try:
    documentStore.delete_document(Path.absolute(Path(file_path)))
    click.secho(f"File with path: {file_path}, has been removed.", fg="yellow")
  except FileNotFoundError:
    click.secho("No files loaded.", fg="red")
    return None
  except PermissionError:
    click.secho(f"Permission denied accessing {file_path}", fg="red")
    return None
  except Exception as e:
    click.secho(f"Error removing file: {e}", fg="red")
    return None
