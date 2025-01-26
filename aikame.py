from utils.index import call_func, hello_world
import click

@click.group()
def cli() -> None :
	print("this is the entrypoint of the application", call_func(1, 2))

cli.add_command(hello_world)

if __name__ == "__main__":
	cli()