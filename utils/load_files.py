import click
import os
import PyPDF2

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
# all the file paths added
files_added = []


def parse_and_extract_text(file_path: str) -> None:
	pdf_file = open(file_path, "rb")
	pdf_reader = PyPDF2.PdfFileReader(pdf_file)
	text = ""
	for page_num in range(pdf_reader.numPages):
		page = pdf_reader.getPage(page_num)
		text += page.extractText()
	pdf_file.close()
	return text

def load_util(file_path: str) -> str:
	try:
		if not os.path.isabs(file_path):
			raise RelativePathError(f"Please provide an absolute path: {file_path}")

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

@click.command()
@click.argument("file_paths", nargs=-1)
@click.pass_context
def load_files(ctx: click.Context, file_paths: tuple[str, ...]) -> list:
	"""
	Load files from a list of (absolute) file paths. \n
	At the moment, this command only reads text files and pdfs and will throw errors for any other file type.
	"""
	res = {}
	for file_path in file_paths:
		try:
			res[file_path] = load_util(file_path)
			files_added.append(file_path)
		except (RelativePathError, ValueError, IsADirectoryError, PermissionError, IOError, FileNotFoundError) as e:
			click.secho(e, fg="red")
			return None
	ctx.obj["files"] = res
	return res


@click.command()
def show_files() -> None:
	"""
	Show the files that have been loaded.
	"""
	if not files_added:
		click.secho("No files have been loaded yet.", fg="red")
	else:
		click.secho("Files loaded:", fg="green")
		for file in files_added:
			click.echo(file)


@click.command()
def clear_context(ctx: click.Context) -> None:
	"""
	Clear the context of the files loaded.
	"""
	ctx.obj["files"] = []
	files_added.clear()
	click.secho("Context cleared.", fg="green")

@click.command()
@click.argument("file_path", type=str)
@click.pass_context
def remove_file(ctx: click.Context, file_path: str) -> None:
	"""
	Remove a file from the context.
	"""
	if file_path not in files_added:
		click.secho(f"File not found: {file_path}", fg="red")
		return None
	files_added.remove(file_path)
	ctx.obj["files"][file_path] = None
	click.secho(f"File removed: {file_path}", fg="green")