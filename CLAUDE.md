# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LiteLLM Updater is a FastAPI service that synchronizes models from Ollama or other LiteLLM/OpenAI-compatible servers into a LiteLLM proxy. It periodically fetches models from upstream sources and registers them with LiteLLM's admin API.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -e .

# Install with dev dependencies (for testing and linting)
pip install -e ".[dev]"
```

### Running the service
```bash
# Using the CLI entrypoint
PORT=8000 litellm-updater

# Or using uvicorn directly
PORT=8000 uvicorn litellm_updater.web:create_app --host 0.0.0.0 --port $PORT
```

### Testing
```bash
# Run all tests
pytest

# Run integration tests (requires live endpoints configured in tests/.env)
pytest tests/test_sources_integration.py -q

# Setup integration tests
cp tests/example.env tests/.env
# Edit tests/.env with TEST_OLLAMA_URL, TEST_OPENAI_URL and optional API keys
```

### Docker
```bash
# Build and run directly
docker build -t litellm-updater .
docker run --rm -e PORT=8000 -p 8000:8000 -v $(pwd)/data:/app/data litellm-updater

# Using docker-compose
cp example.env .env
docker-compose --env-file .env up --build
```

### Linting
```bash
# Run ruff for linting/formatting
ruff check .
ruff format .
```

## Deployment & Live Testing

### Detecting Docker Deployment

**IMPORTANT**: If a `.env` file exists in the project root directory, the service is running in Docker Compose. This means:
- Changes to Python code require rebuilding the Docker image
- The service is accessible at the configured PORT (check `docker-compose.yml` or `.env`)
- Data is persisted in `./data` volume mount
- Live testing can be performed against the running instance

### Making Code Changes in Docker Deployment

When the service is running via Docker Compose (`.env` exists):

```bash
# 1. Make your code changes to Python files

# 2. REBUILD the Docker image (required for code changes to take effect)
docker compose build litellm-updater

# 3. Restart the service with the new image
docker compose restart litellm-updater

# 4. Verify the service is running
docker compose logs --tail=20 litellm-updater

# Alternative: Build and restart in one command
docker compose up --build -d litellm-updater
```

**Why rebuild is necessary**: The Docker image copies the Python code during build. Simply restarting won't pick up code changes - you must rebuild the image first.

### Live Testing

When deployed via Docker Compose, the service is typically accessible at:
- Web UI: `http://localhost:<PORT>` (check `.env` or `docker-compose.yml` for PORT)
- Common routes for testing:
  - `/` - Dashboard
  - `/sources` - View source models
  - `/litellm` - View LiteLLM destination models
  - `/admin` - Configure sources and sync

Example workflow for testing a fix:
```bash
# 1. Make code changes
# 2. Rebuild and restart
docker compose build litellm-updater && docker compose restart litellm-updater

# 3. Test in browser or via curl
curl http://localhost:8005/

# 4. Check logs for errors
docker compose logs -f litellm-updater
```

### Checking Service Status

```bash
# View running containers
docker compose ps

# Follow logs in real-time
docker compose logs -f litellm-updater

# Check last N log lines
docker compose logs --tail=50 litellm-updater

# Restart all services
docker compose restart

# Stop all services
docker compose down
```

## Architecture

### Core Components

**Database Layer** (`database.py`, `db_models.py`, `crud.py`)
- SQLite database (`data/models.db`) with async SQLAlchemy 2.0+
- **Providers table**: Stores provider configuration with prefix and default_ollama_mode
- **Models table**: Persists model metadata, tracks orphan status, preserves user edits
- Alembic migrations for schema versioning
- CRUD operations for all database entities
- Session management with FastAPI dependency injection

**Configuration Layer** (`config.py`, `config_db.py`)
- `config.json` now only stores LiteLLM destination and sync interval
- **Providers migrated to database** - use `config_db.py` helpers to load from DB
- `migrate_sources_to_db()` - One-time migration from config.json to database
- Default config auto-created on first run with LiteLLM at `http://localhost:4000`
- Uses Pydantic validation with `AppConfig` model

**Source Fetchers** (`sources.py`)
- Supports two source types: Ollama (`/api/tags`) and LiteLLM/OpenAI (`/v1/models`)
- `fetch_source_models()` dispatches to the correct fetcher based on `SourceType`
- Ollama fetcher includes `_clean_ollama_payload()` to strip large/redundant fields (tensors, modelfile, license)
- For LiteLLM sources, fetches list then individual model details from `/v1/models/{id}`
- `fetch_litellm_target_models()` uses LiteLLM's `/model/info` endpoint which includes model UUIDs and complete metadata

**Model Normalization** (`models.py`)
- `ModelMetadata.from_raw()` normalizes diverse upstream formats into consistent structure
- Supports `database_id` parameter for LiteLLM models to separate display name (`id`) from database UUID (`database_id`)
  - Display name used in UI (e.g., "ollama/qwen3:8b")
  - Database UUID used for deletion operations (e.g., "3dbd2639-ccf1-4628-86ff-60a8e9d93fce")
- Extraction functions (`_extract_numeric`, `_extract_text`, `_extract_capabilities`) search multiple nested sections (metadata, details, model_info, summary)
- `litellm_fields` property maps normalized metadata to LiteLLM-compatible fields including:
  - Context window and token limits
  - Capabilities → supports_* boolean fields (vision, function_calling, etc.)
  - Default pricing based on GPT-4/Whisper/DALL-E 3 rates
  - Ollama parameters → OpenAI-compatible parameters mapping
- Always sets `litellm_provider: "ollama"` for Ollama models

**Synchronization** (`sync.py`)
- `sync_once()` fetches models from all sources and **persists to database**
  - Accepts optional `AsyncSession` parameter for database persistence
  - Uses `upsert_model()` to create/update models in database
  - Detects orphaned models (no longer in provider fetch)
  - Preserves user-edited parameters during sync
- `start_scheduler()` runs sync in a loop with database session maker
  - Creates fresh session for each sync iteration
  - Commits changes per provider
- Registration to LiteLLM only happens when configured; fetching always occurs
- Errors are logged but don't stop sync for other sources/models

**LiteLLM Integration** (`web.py`)
- Model registration: `POST /model/new` with `{model_name, litellm_params, model_info}`
  - `litellm_params`: Connection configuration (model, api_base)
  - `model_info`: Metadata fields (max_tokens, capabilities, pricing, etc.)
- Model deletion: `POST /model/delete` with `{id: <database_uuid>}`
- Model listing: `GET /model/info` returns complete model data including database UUIDs

**Web Layer** (`web.py`)
- FastAPI app with Jinja2 templates and static files
- Database initialization in lifespan context manager
- `SyncState` class maintains backward-compatible in-memory cache
- `ModelDetailsCache` provides TTL-based caching (600s default) for Ollama `/api/show` calls

**UI Routes:**
  - `/` - Overview dashboard
  - `/sources` - Database-driven providers and models page
  - `/admin` - Provider management, migration, LiteLLM config, sync interval
  - `/litellm` - View models in LiteLLM destination

**Provider Management API:**
  - `GET /api/providers` - List all providers from database
  - `POST /admin/providers` - Create provider (with prefix, default_ollama_mode)
  - `POST /admin/providers/{id}` - Update provider
  - `DELETE /admin/providers/{id}` - Delete provider (cascades to models)
  - `POST /admin/migrate-to-db` - Migrate sources from config.json

**Model Management API:**
  - `GET /api/providers/{id}/models` - Get models for provider (with orphan filtering)
  - `GET /api/models/db/{id}` - Get specific model by database ID
  - `POST /api/models/db/{id}/params` - Update model user parameters
  - `DELETE /api/models/db/{id}/params` - Reset to provider defaults
  - `POST /api/models/db/{id}/refresh` - Refresh single model from provider
  - `POST /api/models/db/{id}/push` - Push model to LiteLLM with effective params

**Legacy/Compatibility API:**
  - `POST /sync` - Manual sync trigger (uses database session)
  - `/models/show?source=X&model=Y` - Fetch Ollama model details on demand
  - `/api/sources`, `/api/models` - JSON APIs (SyncState-based)

### Key Data Flow

**Initial Setup:**
1. User adds providers in `/admin` (stored in database)
2. Or migrates existing config.json sources via "Migrate from config.json" button

**Synchronization Flow:**
1. Scheduler (or manual `/sync` trigger) calls `sync_once()` with database session
2. For each provider:
   - `fetch_source_models()` retrieves raw model list from provider
   - Each raw model is normalized via `ModelMetadata.from_raw()`
   - `upsert_model()` creates or updates model in database
   - User-edited parameters (`user_params`) are preserved during update
   - Models not in fetch are marked as `is_orphaned = True`
   - If LiteLLM configured, models are POSTed to `/model/new`
3. Results also stored in `SyncState` for backward compatibility

**Model Management Flow:**
1. User views providers/models at `/sources` (loads from database via API)
2. Orphaned models displayed in RED
3. Per-model actions:
   - **Refresh**: Fetches latest data from provider, updates database
   - **Edit Params**: Updates `user_params` (preserved across syncs)
   - **Push to LiteLLM**: Sends `effective_params` (user_params or litellm_params) with prefix applied

**Database Schema:**
- **Providers**: id, name, base_url, type, prefix, default_ollama_mode, api_key
- **Models**: id, provider_id, model_id, litellm_params, user_params, is_orphaned, user_modified, first_seen, last_seen

### Important Patterns

**Database Operations**
- Use `Depends(get_session)` for FastAPI dependency injection
- Sessions auto-commit on success, auto-rollback on exceptions
- CRUD functions handle model relationships (e.g., `selectinload(Model.provider)`)
- JSON fields: Use `_dict` properties (e.g., `model.litellm_params_dict`) for parsed data
- Orphan detection: Compare active_model_ids set with existing database models
- User edits: `user_modified` flag prevents automatic overwrites during sync

**Prefix Application**
- Store original model name in `model_id` field (NO prefix)
- Apply prefix only for display: `display_name = f"{prefix}/{model_id}"`
- LiteLLM `model_name` uses prefix (display), `litellm_params.model` uses original
- Example: Display shows `mks-ollama/qwen3:8b`, but params have `ollama/qwen3:8b`

**Effective Parameters**
- `litellm_params`: Auto-updated from provider during sync
- `user_params`: Manual edits via UI, preserved during sync
- `effective_params`: Returns `user_params` if set, else `litellm_params`
- Always use `effective_params` when pushing to LiteLLM

**Ollama Mode Configuration**
- Provider-level: `default_ollama_mode` (applies to all models)
- Model-level: `ollama_mode` (overrides provider default)
- Effective mode: `model.ollama_mode or provider.default_ollama_mode or "ollama"`
- Values: "ollama" (native format) or "openai" (OpenAI-compatible format)

**Error Handling**
- Network errors (httpx.RequestError) are logged but don't crash the sync
- HTTP errors (httpx.HTTPStatusError) are logged with response text
- Validation errors use Pydantic's ValidationError
- Config errors raise RuntimeError with descriptive messages
- Database errors rollback transaction automatically

**Ollama Payload Cleaning**
- The `/api/show` endpoint returns very large responses (tensors, full modelfile)
- Always use `_clean_ollama_payload()` before storing/caching Ollama responses
- Cleaned payload is used in `ModelDetailsCache` and returned by `/models/show`

**URL Normalization**
- All URLs stored as Pydantic `HttpUrl` type
- Use `normalized_base_url` property to get string without trailing slash for path joining
- Don't manually strip slashes; use the property

**Thread Safety**
- `SyncState` and `ModelDetailsCache` use asyncio locks (`asyncio.Lock()`)
- Always use `async with self._lock` pattern when accessing/modifying shared state
- Database sessions are async-safe via SQLAlchemy async engine

## Configuration Notes

**NEW: Providers are now in the database!**

The `data/config.json` schema (reduced):
```json
{
  "litellm": {"base_url": "http://localhost:4000", "api_key": null},
  "sources": [],
  "sync_interval_seconds": 300
}
```

- `sync_interval_seconds`: 0 = disabled, minimum 30 when enabled
- `litellm.base_url`: Can be null to disable LiteLLM registration (still fetches models)
- **`sources` array is legacy** - providers are now managed in database

**Database Schema (`data/models.db`):**

Providers table:
```sql
CREATE TABLE providers (
    id INTEGER PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    base_url VARCHAR NOT NULL,
    type VARCHAR NOT NULL,  -- 'ollama' or 'litellm'
    api_key VARCHAR,
    prefix VARCHAR,  -- e.g., 'mks-ollama'
    default_ollama_mode VARCHAR,  -- 'ollama' or 'openai'
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

Models table:
```sql
CREATE TABLE models (
    id INTEGER PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    model_id VARCHAR NOT NULL,  -- Original name WITHOUT prefix
    model_type VARCHAR,
    context_window INTEGER,
    max_input_tokens INTEGER,
    max_output_tokens INTEGER,
    max_tokens INTEGER,
    capabilities TEXT,  -- JSON array
    litellm_params TEXT NOT NULL,  -- JSON object (provider defaults)
    raw_metadata TEXT NOT NULL,  -- JSON object (full raw response)
    user_params TEXT,  -- JSON object (user edits)
    ollama_mode VARCHAR,  -- Per-model override
    first_seen DATETIME NOT NULL,
    last_seen DATETIME NOT NULL,
    is_orphaned BOOLEAN NOT NULL DEFAULT FALSE,
    orphaned_at DATETIME,
    user_modified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE(provider_id, model_id)
);
```

## Migration Guide

### From config.json to Database

If you have existing sources in `config.json`:

1. **Automatic Migration (Recommended):**
   - Visit `/admin` page
   - Click "Migrate from config.json" button
   - Providers are created in database
   - `config.json` sources array remains for backward compatibility

2. **Manual via API:**
   ```bash
   curl -X POST http://localhost:8000/admin/migrate-to-db
   ```

3. **Verify Migration:**
   ```bash
   # List providers in database
   curl http://localhost:8000/api/providers
   ```

4. **What Happens:**
   - Each source in `config.json` becomes a Provider in database
   - Prefix and default_ollama_mode are NULL initially (add via UI)
   - Migration is idempotent (safe to run multiple times)

### Adding New Providers

**Via Admin UI:**
1. Go to `/admin`
2. Scroll to "Add Provider" form
3. Fill in: Name, Base URL, Type, Optional: API Key, Prefix, Ollama Mode
4. Click "Add Provider"

**Via API:**
```bash
curl -X POST http://localhost:8000/admin/providers \
  -F "name=my-ollama" \
  -F "base_url=http://localhost:11434" \
  -F "type=ollama" \
  -F "prefix=local" \
  -F "default_ollama_mode=ollama"
```

### Managing Models

**Refresh Single Model:**
```bash
curl -X POST http://localhost:8000/api/models/db/123/refresh
```

**Edit Model Parameters:**
```bash
curl -X POST http://localhost:8000/api/models/db/123/params \
  -H "Content-Type: application/json" \
  -d '{"max_tokens": 4096, "temperature": 0.7}'
```

**Push to LiteLLM:**
```bash
curl -X POST http://localhost:8000/api/models/db/123/push
```

**Reset to Defaults:**
```bash
curl -X DELETE http://localhost:8000/api/models/db/123/params
```

## Testing Strategy

**Unit Tests:**
- `tests/test_ollama_payload_cleaning.py` - Ollama payload cleaning
- `tests/test_model_details_cache.py` - Model details caching

**Integration Tests:**
- `tests/test_sources_integration.py` - Live endpoint tests (requires `.env` configuration)
- Uses `pytest-asyncio` for async test support
- Tests skip when endpoints not configured (graceful degradation)

**Database Testing:**
- All new database functionality has been manually tested
- Tested: Provider CRUD, model persistence, orphan detection, migration
- See commit history for test results

**Manual Testing Workflow:**
```bash
# 1. Install dependencies
pip install -e .

# 2. Run unit tests
pytest tests/test_model_details_cache.py tests/test_ollama_payload_cleaning.py -v

# 3. Test migration (with existing config.json)
# Visit http://localhost:8000/admin and click "Migrate from config.json"

# 4. Test API endpoints
curl http://localhost:8000/api/providers
curl http://localhost:8000/api/providers/1/models

# 5. Test model management
# Use UI at /sources to refresh, edit, and push models
```
