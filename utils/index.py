import click
from .crud_files import parent_path

def call_func(a: int, b: int) -> int:
	return a + b



@click.command()
@click.argument("name", type=str)
def hello(name: str) -> str:
	click.echo(f"Hello, {name}!")


def get_embeddings_path_from_key(key: str) -> str:
	try:
		with open(f'{parent_path}/central_ledger.txt', 'r') as f:
			central_ledger = f.readlines()
			for line in central_ledger:
				if key == line.split(':')[0].strip():
					return line.split(':')[1].strip()
	except Exception as e:
		click.secho(f"Error getting embeddings path: {e}", fg='red')
		return None