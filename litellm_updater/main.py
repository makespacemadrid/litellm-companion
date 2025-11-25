"""Entrypoint for running the LiteLLM updater service."""
from __future__ import annotations

import logging
import os

import uvicorn

from .web import create_app

logging.basicConfig(level=logging.INFO)


def run(host: str = "0.0.0.0", port: int | None = None):
    """Run the FastAPI app using Uvicorn."""

    resolved_port = port or int(os.getenv("PORT", "8000"))
    app = create_app()
    uvicorn.run(app, host=host, port=resolved_port)


if __name__ == "__main__":
    run()
