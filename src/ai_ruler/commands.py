import click
import shutil
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table
from iterfzf import iterfzf

from .utils import get_rules_dir
from .config import AI_TOOLS

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

    tool_names = list(AI_TOOLS.keys())
    selected_tool = iterfzf(tool_names, prompt="Select an AI tool to save for: ")
    if selected_tool is None:
        console.print("[yellow]AI tool selection cancelled. Rule not saved.[/yellow]")
        return

    # Determine the correct extension based on the selected tool
    if selected_tool == "roo":
        target_extension = ".md"
    elif selected_tool == "cursor":
        target_extension = ".mdc"
    else:
        target_extension = "" # Default or no specific extension for other tools

    # Handle filename and extension for saving
    rule_name_path = Path(rule_name)
    rule_name_stem = rule_name_path.stem
    rule_name_suffix = rule_name_path.suffix

    if target_extension:
        if rule_name_suffix and rule_name_suffix != target_extension:
            # Replace existing extension if different
            final_rule_name = f"{rule_name_stem}{target_extension}"
        elif not rule_name_suffix:
            # Add extension if none exists
            final_rule_name = f"{rule_name_stem}{target_extension}"
        else:
            # Use existing extension if it matches target
            final_rule_name = rule_name
    else:
        # No specific target extension, use original rule name
        final_rule_name = rule_name

    destination_path = rules_dir / final_rule_name
    if destination_path.exists():
        if not click.confirm(f"Rule ''{final_rule_name}'' already exists. Overwrite?"):
            return
    shutil.copy(source_path, destination_path)
    console.print(f"Rule '[bold green]{final_rule_name}[/bold green]' saved.")

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

    selected_rule = iterfzf(rules, prompt="Select a rule to apply: ")
    if selected_rule is None:
        console.print("[yellow]Rule selection cancelled.[/yellow]")
        return

    tool_names = list(AI_TOOLS.keys())
    selected_tool = iterfzf(tool_names, prompt="Select an AI tool: ")
    if selected_tool is None:
        console.print("[yellow]AI tool selection cancelled.[/yellow]")
        return

    tool_config = AI_TOOLS[selected_tool]
    dest_path = Path(tool_config['path'])
    dest_path.mkdir(parents=True, exist_ok=True)

    # Determine the correct extension based on the selected tool
    if selected_tool == "roo":
        target_extension = ".md"
    elif selected_tool == "cursor":
        target_extension = ".mdc"
    else:
        target_extension = "" # Default or no specific extension for other tools

    # Handle filename and extension
    rule_name_stem = Path(selected_rule).stem
    rule_name_suffix = Path(selected_rule).suffix

    if target_extension:
        if rule_name_suffix and rule_name_suffix != target_extension:
            # Replace existing extension if different
            filename = f"{rule_name_stem}{target_extension}"
        elif not rule_name_suffix:
            # Add extension if none exists
            filename = f"{rule_name_stem}{target_extension}"
        else:
            # Use existing extension if it matches target
            filename = selected_rule
    else:
        # No specific target extension, use original rule name
        filename = selected_rule

    # If filename is still a format string, format it
    if '{rule_name}' in tool_config['filename']:
        filename = tool_config['filename'].format(rule_name=filename)
    
    destination = dest_path / filename

    source_rule_path = rules_dir / selected_rule
    
    # Read the content of the source rule file
    rule_content = source_rule_path.read_text()

    # Extract the rule body by skipping any existing header
    header_match = re.match(r"---.*?---", rule_content, re.DOTALL)
    if header_match:
        rule_body = rule_content[header_match.end():].strip()
    else:
        rule_body = rule_content.strip()

    # Construct the new header
    new_header = f"""---description: {selected_rule}
globs:
alwaysApply: false
---"""
    
    # Combine the new header with the rule body
    final_content = f"{new_header}\n{rule_body}"

    if destination.exists():
        action = click.prompt(f"File ''{destination}'' already exists. Choose an action: (m)erge, (r)ename, (o)verwrite", type=click.Choice(['m', 'r', 'o']))
        if action == 'm':
            with open(destination, 'a') as f:
                f.write("\n")
                f.write(final_content)
            console.print(f"Merged rule ''[bold green]{selected_rule}[/bold green]'' into ''[cyan]{destination}[/cyan]")
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
    
    # Write the final content to the destination file
    with open(destination, 'w') as f:
        f.write(final_content)
    console.print(f"Applied rule '[bold green]{selected_rule}[/bold green]' for '[bold blue]{selected_tool}[/bold blue]' at [cyan]{destination}[/cyan]")

@click.command()
def delete():
    """Deletes a rule from the global store."""
    rules_dir = get_rules_dir()
    rules = [f.name for f in rules_dir.iterdir() if f.is_file()]
    if not rules:
        console.print("[yellow]No rules found to delete.[/yellow]")
        return

    selected_rule = iterfzf(rules, prompt="Select a rule to delete: ")
    if selected_rule is None:
        console.print("[yellow]Rule selection cancelled.[/yellow]")
        return

    if click.confirm(f"Are you sure you want to delete ''{selected_rule}''?"):
        rule_path = rules_dir / selected_rule
        rule_path.unlink()
        console.print(f"Rule '[bold red]{selected_rule}[/bold red]' deleted.")
