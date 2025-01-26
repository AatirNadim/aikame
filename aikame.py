from utils.index import call_func, hello
import click
from utils.load_files import load_files

@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None :
	pass

cli.add_command(hello)
cli.add_command(load_files)

if __name__ == "__main__":
	cli()