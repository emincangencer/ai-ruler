import click
from .commands import save, list_rules, apply, delete

@click.group()
def cli():
    pass

cli.add_command(save)
cli.add_command(list_rules)
cli.add_command(apply)
cli.add_command(delete)

if __name__ == '__main__':
    cli()