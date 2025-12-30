"""Background sync worker that periodically syncs models from providers to LiteLLM."""
import asyncio
import logging
import signal
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database import create_engine, init_session_maker, ensure_minimum_schema, get_database_url
from shared.crud import get_config, get_all_providers, get_provider_by_id
from backend.provider_sync import sync_provider

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class _ConfigWrapper:
    """Lightweight config wrapper to avoid session-bound ORM objects."""

    def __init__(self, data: dict[str, str | None]):
        self.litellm_base_url = data.get("litellm_base_url")
        self.litellm_api_key = data.get("litellm_api_key")
        self.default_pricing_profile = data.get("default_pricing_profile")
        self._default_pricing_override = data.get("default_pricing_override") or {}
        self.sync_interval_seconds = None

    @property
    def default_pricing_override_dict(self) -> dict:
        """Match Config.default_pricing_override_dict interface."""
        return dict(self._default_pricing_override)


class SyncWorker:
    """Main sync worker that runs the sync loop."""

    def __init__(self):
        self.running = True
        self.engine = None
        self.session_maker = None
        self.last_sync_times: dict[int, datetime] = {}  # provider_id -> last sync time

    async def initialize(self):
        """Initialize database connection."""
        logger.info("Initializing database...")

        # Create engine and session maker (using async URL)
        async_db_url = get_database_url()
        self.engine = create_engine(async_db_url)
        # Ensure schema is up to date BEFORE creating session maker
        # This prevents SQLAlchemy from caching old table structure
        await ensure_minimum_schema(self.engine)
        self.session_maker = init_session_maker(self.engine)
        logger.info("Database initialized")

    async def run(self):
        """Main sync loop."""
        logger.info("🚀 Sync worker starting...")

        # Initialize database
        await self.initialize()

        # Setup graceful shutdown
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)

        logger.info("✅ Sync worker ready")

        # Check interval: check every 30 seconds which providers need syncing
        CHECK_INTERVAL = 30

        while self.running:
            try:
                # Grab config and providers in a short-lived session
                async with self.session_maker() as session:
                    config_obj = await get_config(session)
                    all_providers = await get_all_providers(session)

                    # Create provider snapshots with intervals
                    providers_info = []
                    for p in all_providers:
                        # Use provider-specific interval, or global if not set
                        interval = p.sync_interval_seconds if p.sync_interval_seconds else config_obj.sync_interval_seconds
                        providers_info.append({
                            "id": p.id,
                            "name": p.name,
                            "sync_enabled": p.sync_enabled,
                            "sync_interval_seconds": interval,
                        })

                # Snapshot config values to avoid session-bound objects
                config_snapshot = {
                    "litellm_base_url": config_obj.litellm_base_url,
                    "litellm_api_key": config_obj.litellm_api_key,
                    "default_pricing_profile": config_obj.default_pricing_profile,
                    "default_pricing_override": config_obj.default_pricing_override_dict,
                }

                # Check which providers need syncing
                now = datetime.now(UTC)
                providers_to_sync = []
                for provider_info in providers_info:
                    if not provider_info["sync_enabled"]:
                        continue

                    interval = provider_info["sync_interval_seconds"]
                    if interval == 0:
                        continue  # Sync disabled for this provider

                    provider_id = provider_info["id"]
                    last_sync = self.last_sync_times.get(provider_id)

                    # Sync if never synced or interval has passed
                    if last_sync is None or (now - last_sync).total_seconds() >= interval:
                        providers_to_sync.append(provider_id)

                # Sync providers that are due
                if providers_to_sync:
                    logger.info("⏰ Syncing %d provider(s)...", len(providers_to_sync))
                    await self.sync_providers(providers_to_sync, config_snapshot)

                # Wait before next check
                await asyncio.sleep(CHECK_INTERVAL)

            except Exception as e:
                logger.exception("❌ Error in sync loop: %s", e)
                await asyncio.sleep(60)  # Retry after error

        logger.info("🛑 Sync worker stopped")

        # Cleanup
        if self.engine:
            await self.engine.dispose()

    async def sync_providers(self, provider_ids: list[int], config_snapshot: dict[str, str | None]):
        """Sync models from specified providers and update their last sync times."""
        if not provider_ids:
            logger.info("No providers configured")
            return

        for provider_id in provider_ids:
            async with self.session_maker() as session:
                provider = await get_provider_by_id(session, provider_id)
                if not provider:
                    logger.debug("Provider id %s no longer exists, skipping", provider_id)
                    continue
                if not provider.sync_enabled:
                    logger.debug("Skipping disabled provider: %s", provider.name)
                    continue

                try:
                    # Handle compat providers separately (push-only, no fetch)
                    if provider.type in ("compat", "completion"):
                        logger.info("📤 Pushing compat provider to LiteLLM: %s", provider.name)

                        # Import here to avoid circular dependency
                        from shared.crud import get_models_by_provider
                        from backend.litellm_client import reconcile_litellm_models

                        # Get all non-orphaned, sync-enabled models
                        all_models = await get_models_by_provider(session, provider.id, include_orphaned=True)

                        # Push to LiteLLM (reconcile will add/update/delete as needed)
                        if config_snapshot.get("litellm_base_url"):
                            stats = await reconcile_litellm_models(
                                session,
                                _ConfigWrapper(config_snapshot),
                                provider,
                                all_models,
                                remove_orphaned=True
                            )
                            await session.commit()

                            logger.info(
                                "✓ Provider %s pushed: %d added, %d updated, %d deleted",
                                provider.name,
                                stats.get("added", 0) if stats else 0,
                                stats.get("updated", 0) if stats else 0,
                                stats.get("deleted", 0) if stats else 0
                            )
                            # Mark successful sync time
                            self.last_sync_times[provider_id] = datetime.now(UTC)
                        else:
                            logger.debug("LiteLLM not configured, skipping push for %s", provider.name)
                        continue

                    logger.info("📡 Syncing provider: %s (%s)", provider.name, provider.type)

                    # Sync this provider (fetch + push)
                    stats = await sync_provider(session, _ConfigWrapper(config_snapshot), provider, push_to_litellm=True)

                    await session.commit()

                    logger.info(
                        "✓ Provider %s synced: %d added, %d updated, %d orphaned",
                        provider.name,
                        stats.get("added", 0),
                        stats.get("updated", 0),
                        stats.get("orphaned", 0)
                    )

                    # Mark successful sync time
                    self.last_sync_times[provider_id] = datetime.now(UTC)

                except Exception as e:
                    logger.error("❌ Failed to sync provider %s: %s", provider.name, e, exc_info=True)
                    await session.rollback()

    def handle_shutdown(self, signum, frame):
        """Handle graceful shutdown on SIGTERM/SIGINT."""
        logger.info("Received signal %d, shutting down gracefully...", signum)
        self.running = False


async def main():
    """Entry point."""
    worker = SyncWorker()
    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        sys.exit(1)
