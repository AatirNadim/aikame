import click
import os
import PyPDF2
import json
from datetime import datetime
from .embeddings import embeddings_wrapper
from .index import timing_decorator, get_embeddings_path_from_key
from .constants import Constants
import shutil
import fileinput
from uuid import uuid4 as uuid
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader

class RelativePathError(Exception):
	pass

'''
Structure of central ledger:
{
	<file_path>: <embeddings_path>
}
'''


acceptable_file_types = ["txt", "pdf"]

def _init_directories(self):
	"""Initialize necessary directories and files."""

	Constants.parent_path.mkdir(exist_ok=True)
	Constants.docs_dir.mkdir(exist_ok=True)

	if not Constants.metadata_file.exists():
		_save_metadata({})

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

		# Generate embeddings and add to ChromaDB
		texts = [chunk.page_content for chunk in chunks]
		embeddings = self.embedding_model.encode(texts).tolist()

		# Generate IDs for chunks
		doc_id = str(file_path.stem)
		ids = [f"{doc_id}_{i}" for i in range(len(chunks))]

		# Add to ChromaDB
		self.collection.add(
				embeddings=embeddings,
				documents=texts,
				ids=ids,
				metadatas=[{"source": str(file_path)} for _ in chunks]
		)

		# Update metadata
		metadata = self._load_metadata()
		metadata[str(file_path)] = {
				"chunks": len(chunks),
				"ids": ids
		}
		self._save_metadata(metadata)

	except Exception as e:
		raise DocumentProcessingError(f"Error processing document {file_path}: {str(e)}")



# textSplitter = RecursiveCharacterTextSplitter(chunk_size=Constants.chunk_size, overlap=Constants.overlap)



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
			click.secho(f"Path is relative, converting to absolute path...", fg="yellow")
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


@click.command()
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
			click.echo(f"Loading file: {file_path}")
			chunks = textSplitter.split_documents(load_util(file_path), chunk_size=chunk_size)
			embeddings_wrapper(chunks, file_path, f"{uuid()}.index")
			files_added += 1
		except (RelativePathError, ValueError, IsADirectoryError, PermissionError, IOError, FileNotFoundError) as e:
			click.secho(e, fg="red")
			return None
	click.secho(f"Files loaded: {files_added}", fg="green")


@click.command()
@click.pass_context
@timing_decorator
def show_files(ctx: click.Context) -> None:
	"""
	Show the files that have been loaded.
	"""

	click.secho("Showing all files loaded...", fg="yellow")
	try:
		if os.path.exists(f"{parent_path}/central_ledger.txt"):
			with open(f"{parent_path}/central_ledger.txt", "r") as file:
				central_ledger = file.readlines()
				click.secho(f"Files loaded: \n{central_ledger}", fg="green")
		else:
			click.secho("No files loaded.", fg="red")
			return None
	except FileNotFoundError:
		click.secho("No files loaded.", fg="red")
		return None
	except Exception as e:
		click.secho(f"Error showing files: {e}", fg="red")
		return None


@click.command()
@timing_decorator
def clear_context() -> None:
	"""
	Clear the context of the files loaded.
	"""
	click.secho("Clearing all context and metadata...", fg="yellow")
	try:
		shutil.rmtree(parent_path, ignore_errors=False, onerror=None)
		click.secho("Context cleared.", fg="green")
	except Exception as e:
		click.secho(f"Error clearing context: {e}", fg="red")
		return None

@click.command()
@click.argument("file_path", type=str)
@click.pass_context
@timing_decorator
def remove_file(ctx: click.Context, file_path: str) -> None:
	"""
	Remove a file from the context.
	"""
	click.secho(f"Removing file: {file_path}", fg="yellow")
	try:
		embeddings_path = get_embeddings_path_from_key(file_path)
		click.echo(f"Embeddings path: {embeddings_path}")
		if not os.path.exists(embeddings_path):
			raise FileNotFoundError(f"File not found: {file_path}")
		click.echo(f"Removing embeddings file: {embeddings_path}, in parent path: {parent_path}")
		os.remove(os.path.join(parent_path, embeddings_path))
		click.secho(f"File with path: {file_path}, has been removed.", fg="yellow")
		ledger_path = os.path.join(parent_path, "central_ledger.txt")
		with fileinput.input(ledger_path, inplace=True) as file:
				for line in file:
						if not line.startswith(file_path):
								print(line, end='')
		click.secho(f"Central ledger has been updated: {file_path}", fg="green")
	except FileNotFoundError:
		click.secho("No files loaded.", fg="red")
		return None
	except PermissionError:
		click.secho(f"Permission denied accessing {file_path}", fg="red")
		return None
	except Exception as e:
		click.secho(f"Error removing file: {e}", fg="red")
		return None