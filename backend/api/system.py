"""System API endpoints implemented with FastAPI."""

import logging
import re
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import APIRouter, Body, HTTPException, Response

from backend.api.dependencies import ConfigDep, ContainerDep
from backend.api.responses import error_response, success_response
from backend.config.constants import (
    DEFAULT_MARKET_REFRESH_INTERVAL,
    DEFAULT_PORTFOLIO_REFRESH_INTERVAL,
    DEFAULT_TRADE_FEE_RATE,
    DEFAULT_TRADING_FREQUENCY_MINUTES,
    ERROR_MSG_UPDATE_SETTINGS_FAILED,
    INFO_MSG_GITHUB_API_ERROR,
    WARN_MSG_NETWORK_ERROR,
    WARN_MSG_UPDATE_CHECK_FAILED,
)
from backend.config.error_types import (
    CONNECTION_ERROR,
    DATABASE_UNAVAILABLE,
    INTERNAL_SERVER_ERROR,
    SETTINGS_UPDATE_FAILED,
    UPDATE_CHECK_FAILED,
)
from backend.utils.version import (
    GITHUB_REPO_URL,
    LATEST_RELEASE_URL,
    __github_owner__,
    __repo__,
    __version__,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["system"])


@router.get("/settings")
def get_settings(container=ContainerDep):
    """Get system settings."""
    db = container.db

    try:
        settings = db.get_settings()
        return success_response(settings)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Failed to get settings: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=error_response(
                INTERNAL_SERVER_ERROR,
                "Failed to retrieve system settings",
                {"error": str(exc)}
            )
        )


@router.get("/config")
def get_config(container=ContainerDep, config=ConfigDep):
    """Get frontend configuration."""
    db = container.db
    settings = db.get_settings()

    try:
        return success_response(
            {
                "market_refresh_interval": settings.get(
                    "market_refresh_interval", DEFAULT_MARKET_REFRESH_INTERVAL
                ),
                "portfolio_refresh_interval": settings.get(
                    "portfolio_refresh_interval", DEFAULT_PORTFOLIO_REFRESH_INTERVAL
                ),
                "trading_coins": config.DEFAULT_COINS,
                "trade_fee_rate": settings.get("trading_fee_rate", DEFAULT_TRADE_FEE_RATE),
            }
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Failed to get config: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=error_response(
                INTERNAL_SERVER_ERROR,
                "Failed to retrieve frontend configuration",
                {"error": str(exc)}
            )
        )


@router.put("/settings", status_code=204)
def update_settings(payload: Dict[str, Optional[float]] = Body(default={}), container=ContainerDep):
    """Update system settings."""
    db = container.db

    try:
        trading_frequency_minutes = max(
            int(payload.get("trading_frequency_minutes", DEFAULT_TRADING_FREQUENCY_MINUTES)), 1
        )
        trading_fee_rate = max(float(payload.get("trading_fee_rate", DEFAULT_TRADE_FEE_RATE)), 0.0)
        market_refresh_interval = max(
            int(payload.get("market_refresh_interval", DEFAULT_MARKET_REFRESH_INTERVAL)), 1
        )
        portfolio_refresh_interval = max(
            int(payload.get("portfolio_refresh_interval", DEFAULT_PORTFOLIO_REFRESH_INTERVAL)), 1
        )

        success = db.update_settings(
            trading_frequency_minutes,
            trading_fee_rate,
            market_refresh_interval,
            portfolio_refresh_interval,
        )

        if success:
            trading_service = container.trading_service
            trading_service.update_trade_fee_rate(trading_fee_rate)
            return Response(status_code=204)

        raise HTTPException(
            status_code=500,
            detail=error_response(
                SETTINGS_UPDATE_FAILED,
                ERROR_MSG_UPDATE_SETTINGS_FAILED
            )
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("%s: %s", ERROR_MSG_UPDATE_SETTINGS_FAILED, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=error_response(
                INTERNAL_SERVER_ERROR,
                ERROR_MSG_UPDATE_SETTINGS_FAILED,
                {"error": str(exc)}
            )
        )


@router.get("/version")
def get_version():
    """Get current version information."""
    return success_response(
        {
            "current_version": __version__,
            "github_repo": GITHUB_REPO_URL,
            "latest_release_url": LATEST_RELEASE_URL,
        }
    )


@router.get("/check-update")
def check_update():
    """Check for GitHub updates."""
    try:
        import requests

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AITradeGame/1.0",
        }

        try:
            response = requests.get(
                f"https://api.github.com/repos/{__github_owner__}/{__repo__}/releases/latest",
                headers=headers,
                timeout=5,
            )

            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get("tag_name", "").lstrip("v")
                release_url = release_data.get("html_url", "")
                release_notes = release_data.get("body", "")

                is_update_available = compare_versions(latest_version, __version__) > 0

                return success_response(
                    {
                        "update_available": is_update_available,
                        "current_version": __version__,
                        "latest_version": latest_version,
                        "release_url": release_url,
                        "release_notes": release_notes,
                        "repo_url": GITHUB_REPO_URL,
                    }
                )

            raise HTTPException(
                status_code=response.status_code,
                detail=error_response(
                    UPDATE_CHECK_FAILED,
                    WARN_MSG_UPDATE_CHECK_FAILED,
                    {"status_code": response.status_code}
                )
            )
        except requests.exceptions.RequestException as exc:
            logger.warning(INFO_MSG_GITHUB_API_ERROR.format(error=str(exc)))
            raise HTTPException(
                status_code=503,
                detail=error_response(
                    CONNECTION_ERROR,
                    WARN_MSG_NETWORK_ERROR,
                    {"error": str(exc)}
                )
            ) from exc

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Check update failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=error_response(
                INTERNAL_SERVER_ERROR,
                "Failed to check for updates",
                {"error": str(exc)}
            )
        )


@router.get("/health")
def health_check(container=ContainerDep):
    """Lightweight health check for frontend status indicator."""
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        db = container.db
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        finally:
            conn.close()
        return success_response({"status": "ok", "database": "ok", "timestamp": timestamp})
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Health check failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=error_response(
                DATABASE_UNAVAILABLE,
                "Database is unavailable",
                {"error": str(exc), "timestamp": timestamp}
            )
        )


def compare_versions(version1, version2):
    """Compare two version strings.

    Returns:
        1 if version1 > version2
        0 if version1 == version2
        -1 if version1 < version2
    """

    def normalize(v):
        parts = re.findall(r"\d+", v)
        return [int(p) for p in parts]

    v1_parts = normalize(version1)
    v2_parts = normalize(version2)

    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))

    if v1_parts > v2_parts:
        return 1
    if v1_parts < v2_parts:
        return -1
    return 0
