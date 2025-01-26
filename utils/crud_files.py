import click
import os
import PyPDF2
import json
from datetime import datetime
from .embeddings import embeddings_wrapper
from .index import get_embeddings_path_from_key

class RelativePathError(Exception):
	pass

'''
Structure of context object:
{
	"files": {
		"file_path": "file_content"
	}
}
'''


acceptable_file_types = ["txt", "pdf"]
parent_path = '../data'


def parse_and_extract_text(file_path: str) -> None:
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
			file_path = os.path.abspath(file_path)

		if file_path.split(".")[-1] not in acceptable_file_types:
			raise ValueError(f"Unsupported file type: {file_path.split('.')[-1]}")

		if file_path.endswith(".pdf"):
			return parse_and_extract_text(file_path)
		else:
			with open(file_path, "r") as file:
				return '\n'.join(file.readlines())

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
	return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


@click.command()
@click.argument("file_paths", nargs=-1)
@click.pass_context
def load_files(ctx: click.Context, file_paths: tuple[str, ...]) -> list:
	"""
	Load files from a list of (absolute) file paths. \n
	At the moment, this command only reads text files and pdfs and will throw errors for any other file type.
	"""
	res = {}
	files_added = 0
	for file_path in file_paths:
		try:
			chunks = create_chunks(load_util(file_path))
			embeddings_wrapper(chunks, file_path, f"{parent_path}/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.index")
			files_added += 1
		except (RelativePathError, ValueError, IsADirectoryError, PermissionError, IOError, FileNotFoundError) as e:
			click.secho(e, fg="red")
			return None
	click.secho(f"Files loaded: {files_added}", fg="green")
	return res


@click.command()
@click.pass_context
def show_files(ctx: click.Context) -> None:
	"""
	Show the files that have been loaded.
	"""
	try:
		if os.path.exists(f"{parent_path}/central_ledger.txt"):
			with open(f"{parent_path}/central_ledger.txt", "r") as file:
				central_ledger = file.readlines()
				click.secho("Files loaded:", fg="green")
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
def clear_context() -> None:
	"""
	Clear the context of the files loaded.
	"""
	try:
		click.secho("Clearing all context and metadata...", fg="yellow")
		os.removedirs(parent_path)
		click.secho("Context cleared.", fg="green")
	except Exception as e:
		click.secho(f"Error clearing context: {e}", fg="red")
		return None

@click.command()
@click.argument("file_path", type=str)
@click.pass_context
def remove_file(ctx: click.Context, file_path: str) -> None:
	"""
	Remove a file from the context.
	"""
	try:
		embeddings_path = get_embeddings_path_from_key(file_path)
		if not os.path.exists(embeddings_path):
			raise FileNotFoundError(f"File not found: {file_path}")
		os.remove(embeddings_path)
		with open(f"{parent_path}/central_ledger.txt", "r") as file:
			central_ledger = file.readlines()
		with open(f"{parent_path}/central_ledger.txt", "w") as file:
			for line in central_ledger:
				if file_path != line.split(":")[0].strip():
					file.write(line)

		click.secho(f"File removed: {file_path}", fg="green")
	except FileNotFoundError:
		click.secho("No files loaded.", fg="red")
		return None
	except Exception as e:
		click.secho(f"Error removing file: {e}", fg="red")
		return None