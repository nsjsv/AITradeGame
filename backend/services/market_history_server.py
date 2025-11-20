"""Standalone market history server runner using FastAPI."""

from __future__ import annotations

import logging
import os

import uvicorn

from backend.config.settings import Config
from backend.services.history_service import create_app

logger = logging.getLogger(__name__)


def main():
    config = Config()
    app = create_app(config)
    host = os.getenv("COLLECTOR_HOST", "0.0.0.0")
    port = int(os.getenv("COLLECTOR_PORT", os.getenv("PORT", "5100")))
    uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
