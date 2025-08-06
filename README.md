# AI Ruler

AI Ruler is a Python-based command-line interface (CLI) application designed to manage and deploy configuration "rule files" for various AI-powered development tools. It provides a centralized, global repository for rule templates and allows users to quickly apply them to their individual projects in the format required by specific AI tools like Gemini, Cursor, Roo, etc.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/emincangencer/ai-ruler.git
    cd ai-ruler
    ```

2.  **Install dependencies using `uv`:**

    ```bash
    uv sync
    ```

3.  **Install as a `uv` tool:**

    ```bash
    uv tool install .
    ```

## Usage

AI Ruler provides a simple and intuitive command-line interface for managing your AI tool rule files.

### `ai-ruler list`

Displays a list of all rule files currently saved in the global rules directory.

```bash
ai-ruler list
```

### `ai-ruler save <source_file> [rule_name]`

Copies a file from the current directory to the global storage.

-   `<source_file>`: The path to the file in the current project to be saved.
-   `[rule_name]` (optional): The name to save the rule as in the global store. If omitted, it defaults to the original filename.

```bash
ai-ruler save ./my-project-rules.md
```

### `ai-ruler apply`

Triggers an interactive workflow to apply a rule to the current project.

1.  Displays a list of available rules.
2.  Prompts you to select a rule.
3.  Displays a list of supported AI tools.
4.  Prompts you to select a tool.
5.  Copies the selected rule to the correct path and filename for the chosen tool.

```bash
ai-ruler apply
```

### `ai-ruler delete`

Triggers an interactive workflow to delete a rule from the global store.

1.  Displays a list of available rules.
2.  Prompts you to select a rule to delete.
3.  Asks for confirmation before permanently deleting the file.

```bash
ai-ruler delete
```
