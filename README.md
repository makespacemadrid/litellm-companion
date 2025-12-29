# LiteLLM Companion

> **Version 0.6.0** - Synchronize models from Ollama or other OpenAI-compatible servers into LiteLLM

A FastAPI service that automatically discovers, syncs, and manages models from multiple providers (Ollama, OpenAI-compatible APIs) into a LiteLLM proxy. Features database persistence, a web UI for management, and efficient model reconciliation.

## ✨ Features

### Provider Management
- **Multi-provider support** - Ollama, OpenAI-compatible APIs, and compatibility aliases
- **Provider prefixes** - Namespace organization (e.g., `mks-ollama/qwen3:8b`)
- **Ollama mode configuration** - Native Ollama vs OpenAI-compatible format
- **API key support** - Authentication for Ollama Cloud and other secure endpoints
- **Auto-sync** - Periodic background synchronization with configurable intervals
- **Compat providers** - Create OpenAI API aliases for any model

### Model Synchronization
- **Efficient reconciliation** - Only updates models when changes detected
- **Orphaned model detection** - Highlights models no longer available from provider
- **User parameter preservation** - Custom settings survive automatic syncs
- **Manual controls** - Fetch, Sync, and Push actions per provider or globally
- **Performance optimized** - Fixed v0.6.0: Eliminated ~264 unnecessary API calls/hour

### Model Management
- **Full OpenAI API compatibility** - 30+ parameters supported across 100+ models
- **Multi-capability models** - Vision (19), Function calling (34), Embeddings (9), Audio (4)
- **Per-model actions** - Refresh from source, Push to LiteLLM, Edit parameters
- **Pricing configuration** - Per-model pricing overrides and profiles
- **Access control** - Model-level access groups for LiteLLM

### Web UI
- **Provider management** - Add, edit, configure providers with modal dialogs
- **Model browser** - View all models with filtering and status indicators
- **Real-time status** - Visual indicators for orphaned and modified models
- **LiteLLM integration** - Direct view of registered models with tag filtering

> **📊 Model Statistics**: See [MODEL_STATISTICS.md](MODEL_STATISTICS.md) for detailed statistics on available models and OpenAI API coverage.

## 🚀 Quick Start

### Installation

```bash
# Install package
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Running Locally

```bash
# Start the web service
PORT=8000 uvicorn frontend.api:create_app --factory --port 8000

# Or use the convenience command
PORT=8000 litellm-companion
```

The UI will be available at `http://localhost:8000`

### Running with Docker Compose

```bash
# Copy environment template
cp example.env .env

# Edit .env with your configuration
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f litellm-companion-web
```

The compose stack includes:
- **litellm-companion-web** - UI and API on `:4001`
- **litellm-companion-backend** - Background sync worker
- **litellm** - LiteLLM proxy on `:4000`
- **db** - PostgreSQL for LiteLLM
- **watchtower** - Optional auto-update service

## ⚙️ Configuration

### First-Time Setup

1. **Navigate to the Admin page** - `http://localhost:4001/admin`
2. **Configure LiteLLM** - Set base URL (default: `http://localhost:4000`)
3. **Set sync interval** - 0 = disabled, minimum 30 seconds when enabled
4. **Add providers**:
   - **Ollama**: URL `http://ollama:11434`, type `ollama`
   - **OpenAI-compatible**: URL with `/v1` endpoint, type `openai`
   - **Compat**: Virtual provider for OpenAI API aliases

5. **Migrate from config.json** (optional) - Use the migration button if upgrading

### Provider Configuration

**Ollama Provider:**
```
Name: my-ollama
Base URL: http://ollama:11434
Type: ollama
Prefix: local (optional)
Default Ollama Mode: ollama_chat (recommended)
API Key: (optional - for Ollama Cloud)
```

**OpenAI-Compatible Provider:**
```
Name: localai
Base URL: http://localai:8080/v1
Type: openai
Prefix: local
API Key: (if required)
```

**Compat Provider:**
```
Name: compat_models
Type: compat
Sync Enabled: ✓ (to auto-push aliases)
```

### Ollama Modes

LiteLLM Companion supports three Ollama modes:

- **`ollama_chat`** (recommended) - Native chat format, best compatibility
- **`ollama`** - Native completion format
- **`openai`** - OpenAI-compatible format via `/v1` endpoint

Set default mode per provider, or override per-model in the UI.

### Config File

Configuration is now stored in database. The config file (`data/config.json`) only contains:

```json
{
  "litellm": {
    "base_url": "http://localhost:4000",
    "api_key": null
  },
  "sync_interval_seconds": 300
}
```

## 🗄️ Database Schema

### Providers Table
```sql
CREATE TABLE providers (
    id INTEGER PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    base_url VARCHAR NOT NULL,
    type VARCHAR NOT NULL,  -- 'ollama', 'openai', 'compat'
    api_key VARCHAR,
    prefix VARCHAR,
    default_ollama_mode VARCHAR,  -- 'ollama', 'ollama_chat', 'openai'
    sync_enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Models Table
```sql
CREATE TABLE models (
    id INTEGER PRIMARY KEY,
    provider_id INTEGER REFERENCES providers(id),
    model_id VARCHAR NOT NULL,
    litellm_params TEXT NOT NULL,  -- JSON: provider defaults
    user_params TEXT,              -- JSON: user overrides
    is_orphaned BOOLEAN DEFAULT FALSE,
    user_modified BOOLEAN DEFAULT FALSE,
    sync_enabled BOOLEAN DEFAULT TRUE,
    first_seen DATETIME,
    last_seen DATETIME,
    orphaned_at DATETIME,
    UNIQUE(provider_id, model_id)
);
```

### Compat Models Table
```sql
CREATE TABLE compat_models (
    id INTEGER PRIMARY KEY,
    model_name VARCHAR UNIQUE,     -- e.g., 'gpt-4', 'gpt-3.5-turbo'
    mapped_provider_id INTEGER REFERENCES providers(id),
    mapped_model_id VARCHAR,       -- model_id in models table
    access_groups TEXT,            -- JSON array
    created_at DATETIME,
    updated_at DATETIME
);
```

## 🧪 Testing

### Integration Tests

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dev dependencies
pip install -e ".[dev]"

# Configure test endpoints
cp tests/example.env tests/.env
nano tests/.env  # Set TEST_OLLAMA_URL, TEST_OPENAI_URL

# Run tests
pytest tests/test_sources_integration.py -v
```

## 📚 Documentation

### User Guides
- [MODEL_STATISTICS.md](MODEL_STATISTICS.md) - Model coverage and OpenAI API statistics
- [docs/guides/MIGRATION.md](docs/guides/MIGRATION.md) - Upgrade guide from previous versions
- [docs/guides/FIM_CODE_COMPLETION.md](docs/guides/FIM_CODE_COMPLETION.md) - Fill-in-the-Middle setup for code completion
- [docs/guides/COMPAT_MAPPING_PROPOSAL.md](docs/guides/COMPAT_MAPPING_PROPOSAL.md) - Model mapping strategies

### Developer Reference
- [CLAUDE.md](CLAUDE.md) - Development guide and architecture overview
- [docs/reference/](docs/reference/) - Technical API references and mappings

### For AI Coding Assistants
- **Claude Code** users should read [CLAUDE.md](CLAUDE.md) for project guidance
- When making changes, bump version in `pyproject.toml` and all `__init__.py` files

## 🆕 What's New in v0.6.0

### Performance Improvements
- **Fixed compat model updates** - Eliminated ~264 unnecessary API calls per hour
- **Pricing value normalization** - Fixed string/float comparison causing false updates
- **95% faster compat sync** - Reduced from 1.6s to 0.08s per cycle

### New Features
- **Auto-sync for compat providers** - Enable background sync for OpenAI API aliases
- **API key support for all Ollama modes** - Works with Ollama Cloud and authenticated endpoints
- **Improved UI controls** - Sync toggle now available for all provider types

### Bug Fixes
- Fixed false-positive change detection in model reconciliation
- Fixed UI restriction preventing sync toggle on compat providers
- Corrected pricing comparison to handle mixed type values

## 📝 Notes

- **LiteLLM registration** uses `/model/new` endpoint with metadata from provider
- **Prefixes** apply to display names only, not internal model paths
- **User parameters** preserved across syncs via `user_params` field
- **Orphaned models** (removed from provider) highlighted in red
- **Database migrations** handled automatically by Alembic on startup

## 🔧 Architecture

### Service Components
- **Frontend** (`frontend/`) - FastAPI UI + API for provider/model management
- **Backend** (`backend/`) - Background sync worker with configurable intervals
- **Shared** (`shared/`) - Database models, CRUD operations, source fetchers

### Data Flow
1. **Fetch** - Pull models from provider APIs
2. **Normalize** - Convert to standard format with metadata
3. **Reconcile** - Compare with database, detect changes
4. **Update** - Sync to database, preserve user edits
5. **Push** - Register with LiteLLM via admin API

### Key Features
- **Efficient updates** - Only pushes to LiteLLM when models actually change
- **Orphan detection** - Tracks models removed from providers
- **User override preservation** - Custom settings survive auto-sync
- **Multi-mode support** - Native Ollama and OpenAI-compatible formats

## 🤝 Contributing

1. Read [CLAUDE.md](CLAUDE.md) for development practices
2. Create feature branch from `main`
3. Make changes with clear commit messages
4. Bump version in `pyproject.toml` and `__init__.py` files
5. Test locally with Docker Compose
6. Submit pull request

## 📄 License

See LICENSE file for details.
