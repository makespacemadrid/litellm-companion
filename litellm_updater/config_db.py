"""Configuration helpers that use the database."""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from .config import load_config
from .crud import get_all_providers
from .models import AppConfig, SourceEndpoint, SourceType

logger = logging.getLogger(__name__)


async def load_providers_from_db(session: AsyncSession) -> list[SourceEndpoint]:
    """Load all providers from database as SourceEndpoint objects."""
    providers = await get_all_providers(session)

    sources = []
    for provider in providers:
        try:
            source = SourceEndpoint(
                name=provider.name,
                base_url=provider.base_url,
                type=SourceType(provider.type),
                api_key=provider.api_key,
                prefix=provider.prefix,
                default_ollama_mode=provider.default_ollama_mode or (
                    "ollama" if provider.type == "ollama" else None
                ),
                tags=provider.tags_list,
            )
            sources.append(source)
        except Exception as exc:
            logger.error("Failed to load provider %s from DB: %s", provider.name, exc)
            continue

    return sources


async def load_config_with_db_providers(session: AsyncSession) -> AppConfig:
    """Load config with providers from database instead of config.json."""
    # Load base config (litellm target, sync interval)
    config = load_config()

    # Replace sources with providers from database
    config.sources = await load_providers_from_db(session)

    return config
