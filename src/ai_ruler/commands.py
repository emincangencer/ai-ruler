import click
import shutil
from pathlib import Path
from .utils import get_rules_dir
from .config import AI_TOOLS
from rich.console import Console
from rich.table import Table

console = Console()

@click.command()
@click.argument('source_file', type=click.Path(exists=True))
@click.argument('rule_name', required=False)
def save(source_file, rule_name):
    """Saves a rule file to the global store."""
    rules_dir = get_rules_dir()
    source_path = Path(source_file)
    if rule_name is None:
        rule_name = source_path.name
    destination_path = rules_dir / rule_name
    if destination_path.exists():
        if not click.confirm(f"Rule ''{rule_name}'' already exists. Overwrite?"):
            return
    shutil.copy(source_path, destination_path)
    console.print(f"Rule '[bold green]{rule_name}[/bold green]' saved.")

@click.command(name='list')
def list_rules():
    """Lists all saved rules."""
    rules_dir = get_rules_dir()
    rules = [f.name for f in rules_dir.iterdir() if f.is_file()]
    if not rules:
        console.print("[yellow]No rules found.[/yellow]")
        return

    table = Table(title="Available Rules")
    table.add_column("Rule Name", style="cyan")
    for rule in rules:
        table.add_row(rule)
    console.print(table)

@click.command()
def apply():
    """Applies a rule to the current project."""
    rules_dir = get_rules_dir()
    rules = [f.name for f in rules_dir.iterdir() if f.is_file()]
    if not rules:
        console.print("[yellow]No rules found to apply.[/yellow]")
        return

    table = Table(title="Available Rules")
    table.add_column("N", style="bold magenta")
    table.add_column("Rule Name", style="cyan")
    for i, rule in enumerate(rules):
        table.add_row(str(i + 1), rule)
    console.print(table)

    rule_num = click.prompt("Select a rule to apply", type=int)
    if not 1 <= rule_num <= len(rules):
        console.print("[red]Invalid selection.[/red]")
        return
    selected_rule = rules[rule_num - 1]

    console.print("Supported AI tools:")
    tool_names = list(AI_TOOLS.keys())
    for i, tool in enumerate(tool_names):
        console.print(f"{i + 1}. {tool}")

    tool_num = click.prompt("Select an AI tool", type=int)
    if not 1 <= tool_num <= len(tool_names):
        console.print("[red]Invalid selection.[/red]")
        return
    selected_tool = tool_names[tool_num - 1]

    tool_config = AI_TOOLS[selected_tool]
    dest_path = Path(tool_config['path'])
    dest_path.mkdir(parents=True, exist_ok=True)
    filename = tool_config['filename'].format(rule_name=selected_rule)
    destination = dest_path / filename

    source_rule_path = rules_dir / selected_rule
    if destination.exists():
        action = click.prompt(f"File ''{destination}'' already exists. Choose an action: (m)erge, (r)ename, (o)verwrite", type=click.Choice(['m', 'r', 'o']))
        if action == 'm':
            with open(destination, 'a') as f:
                f.write("\n")
                f.write(source_rule_path.read_text())
            console.print(f"Merged rule ''[bold green]{selected_rule}[/bold green]'' into ''[cyan]{destination}[/cyan]''")
            return
        elif action == 'r':
            new_filename = click.prompt(f"Enter new filename for ''{destination.name}''")
            destination = dest_path / new_filename
            if destination.exists():
                console.print(f"[red]File ''{destination}'' already exists. Aborting.[/red]")
                return
        elif action == 'o':
            if not click.confirm(f"Are you sure you want to overwrite ''{destination}''?"):
                return
    shutil.copy(source_rule_path, destination)
    console.print(f"Applied rule '[bold green]{selected_rule}[/bold green]' for '[bold blue]{selected_tool}[/bold blue]' at [cyan]{destination}[/cyan]")

@click.command()
def delete():
    """Deletes a rule from the global store."""
    rules_dir = get_rules_dir()
    rules = [f.name for f in rules_dir.iterdir() if f.is_file()]
    if not rules:
        console.print("[yellow]No rules found to delete.[/yellow]")
        return

    table = Table(title="Available Rules")
    table.add_column("N", style="bold magenta")
    table.add_column("Rule Name", style="cyan")
    for i, rule in enumerate(rules):
        table.add_row(str(i + 1), rule)
    console.print(table)

    rule_num = click.prompt("Select a rule to delete", type=int)
    if not 1 <= rule_num <= len(rules):
        console.print("[red]Invalid selection.[/red]")
        return
    selected_rule = rules[rule_num - 1]

    if click.confirm(f"Are you sure you want to delete ''{selected_rule}''?"):
        rule_path = rules_dir / selected_rule
        rule_path.unlink()
        console.print(f"Rule '[bold red]{selected_rule}[/bold red]' deleted.")
