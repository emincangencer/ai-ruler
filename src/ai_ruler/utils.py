from pathlib import Path

def get_rules_dir() -> Path:
    rules_dir = Path.home() / ".ai_ruler" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    return rules_dir
