"""Shared FastAPI dependencies for accessing application state."""

from fastapi import Depends, HTTPException, Request

from backend.config.settings import Config
from backend.core.service_container import ServiceContainer


def get_container(request: Request) -> ServiceContainer:
    """Retrieve the service container from application state."""
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise HTTPException(status_code=500, detail="Service container not initialized")
    return container


def get_config(request: Request) -> Config:
    """Retrieve the configuration object from application state."""
    config = getattr(request.app.state, "app_config", None)
    if config is None:
        raise HTTPException(status_code=500, detail="Application configuration missing")
    return config


def get_trading_loop_manager(request: Request):
    """Retrieve the trading loop manager for lifecycle operations."""
    manager = getattr(request.app.state, "trading_loop_manager", None)
    if manager is None:
        raise HTTPException(status_code=500, detail="Trading loop manager not initialized")
    return manager


ContainerDep = Depends(get_container)
ConfigDep = Depends(get_config)
