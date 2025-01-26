import click

def call_func(a: int, b: int) -> int:
	return a + b



@click.command()
@click.argument("name", type=str)
def hello(name: str) -> str:
	click.echo(f"Hello, {name}!")