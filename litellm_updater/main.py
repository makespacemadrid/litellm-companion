"""Entrypoint for running the LiteLLM updater service."""
from __future__ import annotations

import logging

import uvicorn

from .web import create_app

logging.basicConfig(level=logging.INFO)


def run(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI app using Uvicorn."""

    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run()
