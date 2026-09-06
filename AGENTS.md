# Repository Guidelines

## Project Structure & Module Organization

This repository contains a small Python CLI package for generating commit messages from staged diffs.

- `commitstash/cli.py` defines the Click command group, interactive prompts, and subcommands.
- `commitstash/git.py` wraps git operations such as reading staged files and creating commits.
- `commitstash/llm.py` builds prompts and calls Anthropic or OpenAI providers.
- `commitstash/config.py` loads and saves user preferences in `~/.commitstash/config.json`.
- `README.md` documents user-facing installation, setup, and CLI usage.
- `pyproject.toml` contains package metadata, dependencies, console script wiring, and Ruff settings.

Tests live in `tests/`, organized by source module as `test_<module>.py`.

## Build, Test, and Development Commands

Use a virtual environment for local work:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Common commands:

- `commitstash version` verifies the editable console script is installed.
- `pytest` runs the test suite.
- `ruff check .` runs lint checks with the repository line length setting.
- `python -m build` builds distribution artifacts, if the `build` package is installed.

For manual testing, stage a small change in a disposable git repo and run `commitstash`.

## Coding Style & Naming Conventions

Target Python 3.9+. Use 4-space indentation, clear function names, and focused modules. Private helpers use a leading underscore, for example `_build_prompt` and `_do_commit`.

Keep lines at or below 100 characters per `[tool.ruff]`. Prefer standard library facilities before adding dependencies. Keep CLI output consistent with the existing Click and Rich style.

## Testing Guidelines

Use `pytest` for new tests. Place tests under `tests/` and name files `test_<module>.py`, such as `tests/test_config.py`. Prefer unit tests for prompt construction, config behavior, and git wrapper error handling. Mock network clients and subprocess calls; do not require real API keys or commits.

## Commit & Pull Request Guidelines

Recent history uses Conventional Commit-style messages, for example `docs: add README` and `feat: initial commitstash CLI`. Continue using concise prefixes such as `feat:`, `fix:`, `docs:`, `test:`, and `chore:`.

Pull requests should include a short summary, testing performed, and any user-facing CLI behavior changes. Link related issues when available. Include terminal output only when it clarifies interactive CLI changes.

## Security & Configuration Tips

Never commit API keys or generated local config. `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` must stay in environment variables. Do not persist secrets in `~/.commitstash/config.json` or test fixtures.
