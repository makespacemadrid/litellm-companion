"""Pydantic models and enums used across the LiteLLM updater service."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class SourceType(str, Enum):
    """Supported upstream source types."""

    OLLAMA = "ollama"
    LITELLM = "litellm"


class SourceEndpoint(BaseModel):
    """Configuration for a single upstream source server."""

    name: str = Field(..., description="Display name for the source")
    base_url: HttpUrl = Field(..., description="Base URL for the upstream server")
    type: SourceType = Field(..., description="Type of the upstream server")
    api_key: Optional[str] = Field(
        None,
        description="Optional API key or bearer token used to authenticate against the source",
    )


class LitellmTarget(BaseModel):
    """Target LiteLLM proxy configuration."""

    base_url: HttpUrl = Field(..., description="LiteLLM base URL")
    api_key: Optional[str] = Field(None, description="API key to authenticate LiteLLM admin calls")


class ModelMetadata(BaseModel):
    """Normalized model description."""

    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    raw: Dict = Field(default_factory=dict, description="Raw metadata returned from the source")


class SourceModels(BaseModel):
    """Collection of models for a source."""

    source: SourceEndpoint
    models: List[ModelMetadata] = Field(default_factory=list)
    fetched_at: Optional[datetime] = None


class AppConfig(BaseModel):
    """Application configuration for the updater service."""

    litellm: LitellmTarget
    sources: List[SourceEndpoint] = Field(default_factory=list)
    sync_interval_seconds: int = Field(300, ge=30, description="Sync interval in seconds")

