"""Completion models API routes."""
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from shared.crud import (
    create_completion_model,
    delete_model,
    get_all_completion_models,
    get_model_by_id,
    get_or_create_completion_provider,
    get_provider_by_id,
)
from shared.database import get_session

router = APIRouter()


@router.get("/models")
async def list_completion_models(session: AsyncSession = Depends(get_session)):
    """List all completion models."""
    models = await get_all_completion_models(session)

    provider_cache: dict[int, dict] = {}
    result = []
    for model in models:
        mapped_provider = None
        if model.mapped_provider_id:
            if model.mapped_provider_id in provider_cache:
                mapped_provider = provider_cache[model.mapped_provider_id]
            else:
                provider = await get_provider_by_id(session, model.mapped_provider_id)
                if provider:
                    mapped_provider = {
                        "id": provider.id,
                        "name": provider.name,
                        "type": provider.type,
                        "base_url": provider.base_url,
                    }
                    provider_cache[provider.id] = mapped_provider

        result.append(
            {
                "id": model.id,
                "model_name": model.model_id,
                "mapped_model_id": model.mapped_model_id,
                "mapped_provider": mapped_provider,
            }
        )

    return result


@router.post("/models")
async def create_completion_model_endpoint(
    mapped_provider_id: int = Form(...),
    mapped_model_id: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    """Create a completion mapping."""
    try:
        model = await create_completion_model(
            session,
            mapped_provider_id=mapped_provider_id,
            mapped_model_id=mapped_model_id,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"id": model.id, "message": "Completion model created"}


@router.delete("/models/{model_id}")
async def delete_completion_model(model_id: int, session: AsyncSession = Depends(get_session)):
    """Delete completion model."""
    model = await get_model_by_id(session, model_id)
    if not model or not model.provider or model.provider.type != "completion":
        raise HTTPException(404, "Completion model not found")

    await delete_model(session, model)
    return {"message": "Completion model deleted"}


@router.get("/provider")
async def get_completion_provider(session: AsyncSession = Depends(get_session)):
    """Return completion provider details."""
    provider = await get_or_create_completion_provider(session)
    return {"id": provider.id, "name": provider.name}
