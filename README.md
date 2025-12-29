# LiteLLM Companion

> **Version 0.6.0** - Automatically sync and manage models from Ollama and OpenAI-compatible APIs into LiteLLM

A FastAPI service that discovers, synchronizes, and manages models from multiple providers into a LiteLLM proxy. Features database persistence, web UI, and efficient model reconciliation.

## Key Features

- **Multi-provider support** - Ollama, OpenAI-compatible APIs, and compatibility aliases
- **Auto-sync** - Periodic background synchronization with configurable intervals
- **Efficient updates** - Only pushes to LiteLLM when models actually change (v0.6.0: eliminated ~264 unnecessary API calls/hour)
- **Web UI** - Provider management, model browser, and real-time status
- **Database persistence** - SQLite storage with automatic migrations
- **Orphan detection** - Highlights models removed from providers
- **User overrides** - Custom parameters preserved across syncs
- **Full OpenAI compatibility** - 30+ parameters supported across 100+ models

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd litellm-companion

# Install dependencies
pip install -e .
```

### Running Locally

```bash
# Start the web service
PORT=8000 uvicorn frontend.api:create_app --factory --port 8000
```

Open `http://localhost:8000` in your browser.

### Running with Docker Compose (Recommended)

```bash
# Copy and edit environment
cp example.env .env
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f litellm-companion-web
```

**Services:**
- **Web UI**: `http://localhost:4001` (or port in `.env`)
- **LiteLLM Proxy**: `http://localhost:4000`
- **Backend Worker**: Automatic background sync

## Configuration

### First-Time Setup

1. **Open Admin page** - `http://localhost:4001/admin`
2. **Set LiteLLM URL** - Default: `http://localhost:4000`
3. **Set sync interval** - 0 = disabled, minimum 30 seconds
4. **Add providers**:

**Ollama Example:**
```
Name: my-ollama
Base URL: http://ollama:11434
Type: ollama
Prefix: local (optional)
Default Ollama Mode: ollama_chat
API Key: (optional - for Ollama Cloud)
```

**OpenAI-Compatible Example:**
```
Name: localai
Base URL: http://localai:8080/v1
Type: openai
Prefix: local
API Key: (if required)
```

5. **Enable sync** - Toggle "Sync Enabled" for each provider
6. **Wait for sync** - Or click "Sync" to trigger manually

### Configuration File

`data/config.json` (auto-created):
```json
{
  "litellm": {
    "base_url": "http://localhost:4000",
    "api_key": null
  },
  "sync_interval_seconds": 300
}
```

Providers are managed via the database (not config file).

## What's New in v0.6.0

### Performance Improvements
- **Fixed compat model updates** - Eliminated ~264 unnecessary API calls per hour
- **95% faster compat sync** - Reduced from 1.6s to 0.08s per cycle
- **Pricing normalization** - Fixed string/float comparison bug

### New Features
- **Auto-sync for compat providers** - Enable background sync for OpenAI API aliases
- **API key support for all Ollama modes** - Works with Ollama Cloud
- **Improved UI** - Sync toggle available for all provider types

## Documentation

### User Guides
- [Model Statistics](MODEL_STATISTICS.md) - Coverage and OpenAI API compatibility
- [Migration Guide](docs/guides/MIGRATION.md) - Upgrade from previous versions
- [FIM Code Completion](docs/guides/FIM_CODE_COMPLETION.md) - Setup for code editors
- [Compat Mapping](docs/guides/COMPAT_MAPPING_PROPOSAL.md) - Model alias strategies

### Developer Docs
- [CLAUDE.md](CLAUDE.md) - Architecture, development guide, and workflows
- [docs/](docs/) - Technical references and API documentation
- [AGENTS.md](AGENTS.md) - Notes for AI coding assistants

## Common Tasks

### Add a New Provider
1. Go to `/admin`
2. Click "Add Provider"
3. Fill in details (name, URL, type)
4. Enable sync and save

### Create OpenAI API Aliases
1. Go to `/compat`
2. Map OpenAI model names (e.g., `gpt-4`) to your actual models
3. Enable sync on compat provider for auto-push

### Manual Sync
- **Per provider**: Click "Sync" button next to provider
- **All providers**: Click "Sync All" on overview page

### View Models in LiteLLM
- Go to `/litellm` page
- Filter by tags (provider, type, etc.)
- See registered models with metadata

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────┐
│  Providers      │─────▶│  LiteLLM         │─────▶│  Clients    │
│  (Ollama, etc)  │      │  Companion       │      │             │
└─────────────────┘      └──────────────────┘      └─────────────┘
                               │
                         ┌─────┴─────┐
                         │           │
                    ┌────▼────┐ ┌────▼────┐
                    │ Frontend│ │ Backend │
                    │ (UI/API)│ │ (Worker)│
                    └────┬────┘ └────┬────┘
                         │           │
                         └─────┬─────┘
                               │
                         ┌─────▼─────┐
                         │  SQLite   │
                         │ Database  │
                         └───────────┘
```

**Data Flow:**
1. **Fetch** - Pull models from providers
2. **Normalize** - Convert to standard format
3. **Reconcile** - Compare with database
4. **Update** - Sync changes, preserve user edits
5. **Push** - Register with LiteLLM

## Terminology

- **Fetch** - Pull models from provider into database only
- **Push** - Send database models to LiteLLM only
- **Sync** - Fetch + Push in one operation
- **Compat** - OpenAI API alias provider (virtual)
- **Orphan** - Model removed from provider but still in database

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Configure test endpoints
cp tests/example.env tests/.env
nano tests/.env

# Run tests
pytest tests/ -v
```

## Contributing

1. Read [CLAUDE.md](CLAUDE.md) for development practices
2. Create feature branch from `main`
3. Make changes with clear commits
4. Bump version in `pyproject.toml` and `__init__.py` files
5. Test with Docker Compose
6. Submit pull request

## License

See LICENSE file for details.

---

**Need help?** Check [docs/](docs/) for detailed guides and technical references.
