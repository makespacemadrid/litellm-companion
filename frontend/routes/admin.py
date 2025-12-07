"""Admin configuration API routes."""
from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_session
from shared.crud import get_config, update_config

router = APIRouter()


@router.get("/config")
async def get_configuration(session: AsyncSession = Depends(get_session)):
    """Get current configuration."""
    config = await get_config(session)

    return {
        "litellm_base_url": config.litellm_base_url,
        "sync_interval_seconds": config.sync_interval_seconds,
        "default_pricing_profile": config.default_pricing_profile,
        "default_pricing_override": config.default_pricing_override_dict,
    }


@router.post("/config")
async def update_configuration(
    litellm_base_url: str | None = Form(None),
    litellm_api_key: str | None = Form(None),
    sync_interval_seconds: int | None = Form(None),
    default_pricing_profile: str | None = Form(None),
    default_input_cost_per_token: str | None = Form(None),
    default_output_cost_per_token: str | None = Form(None),
    session: AsyncSession = Depends(get_session),
):
    """Update configuration."""
    pricing_override: dict | None = {}
    for key, raw in (
        ("input_cost_per_token", default_input_cost_per_token),
        ("output_cost_per_token", default_output_cost_per_token),
    ):
        if raw not in (None, ""):
            try:
                pricing_override[key] = float(raw)
            except ValueError:
                continue
    if pricing_override == {}:
        pricing_override = None

    await update_config(
        session,
        litellm_base_url=litellm_base_url,
        litellm_api_key=litellm_api_key,
        sync_interval_seconds=sync_interval_seconds,
        default_pricing_profile=default_pricing_profile,
        default_pricing_override=pricing_override,
    )

    return {"status": "updated"}
