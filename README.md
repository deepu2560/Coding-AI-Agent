# Python LLM Coding Agent

A small, educational coding agent that uses an OpenAI-compatible chat-completions
API through [OpenRouter](https://openrouter.ai/). Given a command-line prompt, the
agent can inspect, modify, and run code in a deliberately restricted workspace.

The repository also includes a calculator project under `calculator/`. It is both
an example application and the only directory exposed to the agent's tools by
default.

## How it works

1. `main.py` loads `OPENROUTER_API_KEY`, sends the system and user prompts to
   OpenRouter, and advertises the available function tools.
2. The selected model can respond normally or request one or more tool calls.
3. `call_function.py` validates the tool name, injects `./calculator` as the
   working directory, invokes the matching local Python function, and appends its
   result to the conversation.
4. The loop repeats for up to 20 model responses. A response without tool calls
   is printed as the final answer.

The agent currently requests the `openrouter/free` model with temperature `0`.

## Available tools

| Tool | Purpose | Important behavior |
| --- | --- | --- |
| `get_files_info` | List a directory | Reports each entry's size and whether it is a directory. |
| `get_file_content` | Read a text file | Returns at most 10,000 characters and marks truncated results. |
| `write_file` | Create or overwrite a text file | Creates missing parent directories. |
| `run_python_file` | Execute a Python file | Accepts optional arguments and has a 30-second timeout. |

All paths supplied by the model are resolved beneath `./calculator`. Each tool
rejects paths that escape that directory, including absolute paths outside it and
`..` traversal. This boundary limits accidental access, but it is **not a complete
security sandbox**: Python code executed inside the calculator project still runs
as a normal local process with the permissions of the current user. Review the
code and run the agent only in an environment you trust.

## Requirements

- Python 3.12 or newer
- An [OpenRouter](https://openrouter.ai/) API key
- [`uv`](https://docs.astral.sh/uv/) (recommended), or another Python environment
  manager capable of installing the dependencies in `pyproject.toml`

Runtime dependencies are pinned in `pyproject.toml` and `uv.lock`:

- `openai==2.44.0` for the OpenAI-compatible client
- `python-dotenv==1.2.2` for loading local environment variables

## Installation

Clone the repository and install the locked dependencies:

```bash
git clone <repository-url>
cd Coding-AI-Agent
uv sync
```

Create a `.env` file in the repository root (or export the variable in your
shell):

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
```

Do not commit real API keys.

## Usage

Pass the request as one quoted positional argument:

```bash
uv run python main.py "Inspect the calculator and explain how it evaluates expressions"
```

Ask the agent to edit or test the example project:

```bash
uv run python main.py "Add exponentiation support to the calculator and run its tests"
```

Use `--verbose` to print every invoked function (including its arguments) and
token usage for each model response:

```bash
uv run python main.py --verbose "List the files and summarize the calculator project"
```

If `OPENROUTER_API_KEY` is missing, the program exits with a `RuntimeError`. If no
final answer is produced within 20 model responses, it exits with status `1`.

## Example calculator

The bundled calculator evaluates **space-separated** infix expressions using
`+`, `-`, `*`, and `/`, with standard multiplication/division precedence. Its CLI
prints JSON containing the original expression and result:

```bash
uv run python calculator/main.py "2 * 3 - 8 / 2 + 5"
```

```json
{
  "expression": "2 * 3 - 8 / 2 + 5",
  "result": 7
}
```

Operators and operands must be separated by spaces; for example, use `3 + 5`
rather than `3+5`. Parentheses and unary operators are not implemented.

## Testing

Run the calculator's unit tests from its own directory so its `pkg` imports
resolve correctly:

```bash
cd calculator
python -m unittest tests.py
```

The root-level `test_*.py` files are lightweight manual smoke scripts for the four
tools:

```bash
python test_get_files_info.py
python test_get_file_content.py
python test_run_python_file.py
python test_write_file.py
```

> **Note:** `test_write_file.py` is destructive: it overwrites
> `calculator/lorem.txt` and `calculator/pkg/morelorem.txt`. Restore those fixtures
> with Git after running it if you need their previous contents.

## Project structure

```text
.
├── main.py                     # CLI and model/tool-call loop
├── prompts.py                  # System prompt presented to the model
├── call_function.py            # Tool registry and dispatcher
├── functions/
│   ├── get_files_info.py       # Directory listing tool and JSON schema
│   ├── get_file_content.py     # Bounded file-reading tool and schema
│   ├── write_file.py           # File-writing tool and schema
│   └── run_python_file.py      # Python execution tool and schema
├── calculator/                 # Agent workspace and example project
│   ├── main.py
│   ├── tests.py
│   └── pkg/
├── test_*.py                   # Manual tool smoke scripts
├── pyproject.toml
└── uv.lock
```

## Extending the agent

To add a tool:

1. Implement a function in `functions/` that accepts `working_directory` plus its
   tool-specific arguments and returns a string.
2. Define its OpenAI function-tool JSON schema in the same module.
3. Import the function and schema in `call_function.py`.
4. Add the schema to `available_functions` and the callable to `function_map`.
5. Update `prompts.py` when the model needs additional guidance about the new
   capability.

Keep the injected working-directory boundary in place for every filesystem or
execution tool, and add success, invalid-input, and path-traversal checks when
introducing new behavior.
