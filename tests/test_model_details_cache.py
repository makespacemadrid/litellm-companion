import pytest

from litellm_updater.web import ModelDetailsCache


@pytest.mark.asyncio
async def test_model_details_cache_update_replaces_payload():
    cache = ModelDetailsCache(ttl_seconds=60)

    await cache.set("alpha", "model-a", {"initial": True})
    await cache.update("alpha", "model-a", {"initial": False, "custom": "value"})

    cached = await cache.get("alpha", "model-a")

    assert cached == {"initial": False, "custom": "value"}
