# AGENTS.md

This repository includes instructions for AI coding assistants.

## For AI Coding Assistants

- **Claude Code** users should read [CLAUDE.md](CLAUDE.md) for project guidance and workflow notes
- **Other AI agents** should follow the same practices outlined in [CLAUDE.md](CLAUDE.md) unless a tool-specific guide is added later

## Important Notes

- When making changes, bump the project version in `pyproject.toml` and all `__version__` files (`backend/__init__.py`, `frontend/__init__.py`, `shared/__init__.py`, `proxy/__init__.py`)
- Current version: **0.6.0**
- See [CLAUDE.md](CLAUDE.md) for architecture overview, development commands, and recent changes
- See [README.md](README.md) for user-facing documentation and quick start

## Documentation Structure

- **README.md** - User-facing documentation (installation, configuration, usage)
- **CLAUDE.md** - Developer documentation (architecture, patterns, workflows)
- **docs/** - Additional guides and technical references

## Version History

- **v0.6.0** (2025-12-29) - Performance improvements, compat provider auto-sync, API key support for all Ollama modes
- See [CLAUDE.md - Recent Changes](CLAUDE.md#recent-changes--gotchas) for detailed changelog
