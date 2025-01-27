from utils.index import call_func, hello
import click
import os
from utils.crud_files import load_files, show_files, clear_context, remove_file
from utils.rag import query

@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None :
	ctx.obj = {}

@cli.command()
@click.pass_context
def set_value(ctx):
    """Set a value in the context."""
    os.environ['value'] = "Hello, World!"  # Store a value in the context
    click.echo("Value set!")

@cli.command()
@click.pass_context
def get_value(ctx):
    """Get the value from the context."""
    value = os.getenv('value', 'No value set.')
    click.echo(f'Value: {value}')

cli.add_command(hello)
cli.add_command(load_files)
cli.add_command(show_files)
cli.add_command(clear_context)
cli.add_command(remove_file)
cli.add_command(set_value)
cli.add_command(get_value)
cli.add_command(query)


if __name__ == "__main__":
	cli()