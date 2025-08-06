import pytest
from click.testing import CliRunner
from ai_ruler.main import cli
from ai_ruler.config import AI_TOOLS
from pathlib import Path

@pytest.fixture
def mock_home(monkeypatch, tmp_path):
    """Mocks the user's home directory to a temporary directory."""
    monkeypatch.setattr(Path, 'home', lambda: tmp_path)
    # Also ensure the rules directory is created inside this mocked home
    rules_dir = tmp_path / ".ai_ruler" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    return tmp_path

def test_save_and_list_rule(mock_home):
    """Tests saving a new rule and then listing it."""
    runner = CliRunner()
    
    # Create a dummy rule file to save
    source_file = mock_home / "my-test-rule.md"
    source_file.write_text("this is a test rule")

    # --- Test save ---
    result_save = runner.invoke(cli, ["save", str(source_file)])
    assert result_save.exit_code == 0, result_save.output
    assert "Rule 'my-test-rule.md' saved." in result_save.output

    # Check that the file exists in the mocked rules directory
    rules_dir = mock_home / ".ai_ruler" / "rules"
    saved_rule_path = rules_dir / "my-test-rule.md"
    assert saved_rule_path.exists()
    assert saved_rule_path.read_text() == "this is a test rule"

    # --- Test list ---
    result_list = runner.invoke(cli, ["list"])
    assert result_list.exit_code == 0, result_list.output
    assert "my-test-rule.md" in result_list.output

def test_delete_rule(mock_home):
    """Tests deleting a rule."""
    runner = CliRunner()
    rules_dir = mock_home / ".ai_ruler" / "rules"
    
    # Pre-populate a rule to be deleted
    rule_to_delete = rules_dir / "deletable-rule.md"
    rule_to_delete.write_text("delete me")
    assert rule_to_delete.exists()

    # --- Test delete ---
    # The command is interactive, so we pipe '1' (for the first rule) and 'y' (for confirm)
    result_delete = runner.invoke(cli, ["delete"], input="1\ny\n")
    
    assert result_delete.exit_code == 0, result_delete.output
    assert "Rule 'deletable-rule.md' deleted." in result_delete.output
    
    # Check that the file no longer exists
    assert not rule_to_delete.exists()

@pytest.mark.parametrize("tool_name, tool_config_data", AI_TOOLS.items())
def test_apply_rule(mock_home, tool_name, tool_config_data):
    """Tests applying a rule for different AI tools."""
    runner = CliRunner()
    rules_dir = mock_home / ".ai_ruler" / "rules"
    
    # Pre-populate a rule to be applied
    rule_to_apply = rules_dir / "applicable-rule.md"
    rule_to_apply.write_text("apply me")

    # --- Test apply ---
    # The command is interactive.
    # 1. Select the rule (there's only one, so "1")
    # 2. Select the tool dynamically
    tool_index = list(AI_TOOLS.keys()).index(tool_name) + 1 # +1 because fzf is 1-indexed

    with runner.isolated_filesystem() as project_dir:
        result_apply = runner.invoke(cli, ["apply"], input=f"1\n{tool_index}\n")

        assert result_apply.exit_code == 0, result_apply.output
        assert "Applied rule 'applicable-rule.md'" in result_apply.output
        assert f"for '{tool_name}'" in result_apply.output

        # Determine expected applied file path
        if '{rule_name}' in tool_config_data['filename']:
            # Apply extension logic if filename is a format string
            rule_name_stem = Path(rule_to_apply.name).stem
            if tool_name == "roo":
                expected_filename = f"{rule_name_stem}.md"
            elif tool_name == "cursor":
                expected_filename = f"{rule_name_stem}.mdc"
            else:
                expected_filename = rule_to_apply.name # Should not happen with current config
        else:
            expected_filename = tool_config_data['filename']

        applied_file_path = Path(project_dir) / tool_config_data['path'] / expected_filename
        
        assert applied_file_path.exists()
        expected_content = """---description: applicable-rule.md
globs:
alwaysApply: false
---
apply me"""
        assert applied_file_path.read_text() == expected_content
