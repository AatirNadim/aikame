import click
from .constants import parent_path
from functools import wraps
import time

def call_func(a: int, b: int) -> int:
	return a + b

def timing_decorator(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		result = f(*args, **kwargs)
		end = time.perf_counter()
		click.secho(f"{f.__name__} took {end - start:.2f} seconds", fg="yellow")
		return result
	return wrapper


@click.command()
@click.argument("name", type=str)
def hello(name: str) -> str:
	"""
	A simple health check.
	"""
	click.echo(f"Hello, {name}!")


def get_embeddings_path_from_key(key: str) -> str:
	click.echo(f"Getting embeddings path for key: {key}")
	try:
		with open(f'{parent_path}/central_ledger.txt', 'r') as f:
			central_ledger = f.readlines()
		for line in central_ledger:
			if key == line.split(':')[0].strip():
				return line.split(':')[1].strip()
		raise Exception(f"Key not found: {key}")
	except Exception as e:
		click.secho(f"Error getting embeddings path: {e}", fg='red')
		return None