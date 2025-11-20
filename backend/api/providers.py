"""Provider API endpoints implemented with FastAPI routers."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Body, Response
from urllib.parse import urlparse
import ipaddress

from backend.api.dependencies import ContainerDep
from backend.api.responses import success_response, error_response
from backend.config import error_types
from backend.config.constants import (
    INFO_MSG_FETCHING_MODELS,
    INFO_MSG_MODELS_FOUND,
    INFO_MSG_RESPONSE_STATUS,
    TIMEOUT_API_REQUEST,
)
from backend.utils.errors import (
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ExternalServiceError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("")
def get_providers(container=ContainerDep) -> Dict[str, Any]:
    """Get all API providers，按统一响应格式返回。"""
    db = container.db
    providers = db.get_all_providers()
    return success_response(providers)


@router.post("", status_code=201)
def add_provider(payload: Dict[str, Any] = Body(...), container=ContainerDep):
    """Add new API provider."""
    db = container.db

    required_fields = ("name", "api_url", "api_key")
    missing_fields = [field for field in required_fields if not payload.get(field)]
    if missing_fields:
        raise ValidationError(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )

    try:
        provider_id = db.add_provider(
            name=payload["name"],
            api_url=payload["api_url"],
            api_key=payload["api_key"],
            models=payload.get("models", ""),
        )
        return success_response({"id": provider_id})
    except ValidationError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Failed to add provider: %s", exc, exc_info=True)
        raise ExternalServiceError(
            message="Failed to add provider",
            status_code=500,
            details={"error": str(exc)}
        )


@router.delete("/{provider_id}", status_code=204)
def delete_provider(provider_id: int, container=ContainerDep):
    """Delete API provider."""
    db = container.db

    try:
        db.delete_provider(provider_id)
        return Response(status_code=204)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Failed to delete provider %s: %s", provider_id, exc, exc_info=True)
        raise ExternalServiceError(
            message="Failed to delete provider",
            status_code=500,
            details={"provider_id": provider_id, "error": str(exc)}
        )


def _reject_private_host(hostname: str) -> None:
    """Raise if the host is clearly private/loopback."""
    lowered = hostname.lower()
    if lowered in ("localhost",) or lowered.startswith("localhost."):
        raise ValidationError(
            message="拒绝访问本地地址",
            details={"hostname": hostname}
        )
    try:
        ip = ipaddress.ip_address(lowered)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise ValidationError(
                message="拒绝访问内网地址",
                details={"hostname": hostname, "ip": str(ip)}
            )
    except ValueError:
        # Not an IP literal; best-effort block obvious private naming
        if lowered.startswith(("127.", "10.", "192.168.", "172.16.", "172.17.", "172.18.", "172.19.",
                               "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.",
                               "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.")):
            raise ValidationError(
                message="拒绝访问内网地址",
                details={"hostname": hostname}
            )


def _validate_external_url(raw_url: str) -> str:
    """Parse and validate provider URL to avoid SSRF against internal services."""
    parsed = urlparse(raw_url.strip())
    if parsed.scheme not in ("http", "https"):
        raise ValidationError(
            message="只允许 http/https 协议",
            details={"url": raw_url, "scheme": parsed.scheme}
        )
    if not parsed.hostname:
        raise ValidationError(
            message="无效的提供方地址",
            details={"url": raw_url}
        )
    _reject_private_host(parsed.hostname)
    return parsed.geturl()


@router.post("/models")
def fetch_provider_models(payload: Dict[str, Any] = Body(...)):
    """Fetch available models from provider's API."""
    api_url = payload.get("api_url")
    api_key = payload.get("api_key")

    if not api_url or not api_key:
        missing = []
        if not api_url:
            missing.append("api_url")
        if not api_key:
            missing.append("api_key")
        raise ValidationError(
            message="Missing required fields",
            details={"missing_fields": missing}
        )

    try:
        import requests

        api_url = _validate_external_url(api_url).rstrip("/")
        models_endpoint = f"{api_url}/models"

        logger.info(INFO_MSG_FETCHING_MODELS.format(endpoint=models_endpoint))

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(models_endpoint, headers=headers, timeout=TIMEOUT_API_REQUEST)

        logger.info(INFO_MSG_RESPONSE_STATUS.format(status=response.status_code))

        if response.status_code == 200:
            result = response.json()

            # 解析响应数据
            if "data" in result and isinstance(result["data"], list):
                models = [m["id"] for m in result["data"] if "id" in m]
            elif "models" in result and isinstance(result["models"], list):
                models = result["models"]
            elif isinstance(result, list):
                models = result
            else:
                logger.error("Unknown response format: %s", result)
                raise ExternalServiceError(
                    message="Unknown response format from provider API",
                    status_code=500,
                    details={"response": str(result)[:200]}
                )

            if not models:
                raise NotFoundError(
                    message="No models found from provider",
                    details={"api_url": api_url}
                )

            logger.info(INFO_MSG_MODELS_FOUND.format(count=len(models)))
            return success_response({"models": models})

        if response.status_code == 401:
            raise UnauthorizedError(
                message="Invalid API key",
                details={"api_url": api_url}
            )
        if response.status_code == 403:
            error_msg = "API access denied"
            try:
                error_data = response.json()
                if "error" in error_data:
                    detail = error_data["error"]
                    if isinstance(detail, dict) and "message" in detail:
                        error_msg = f"访问被拒绝: {detail['message']}"
                    elif isinstance(detail, str):
                        error_msg = f"访问被拒绝: {detail}"
                logger.error("403 response: %s", error_data)
            except Exception:
                pass
            raise ForbiddenError(
                message=error_msg,
                details={"api_url": api_url}
            )
        if response.status_code == 404:
            raise NotFoundError(
                message="API endpoint not found",
                details={"endpoint": models_endpoint}
            )

        error_msg = f"API 返回错误状态码: {response.status_code}"
        try:
            error_data = response.json()
            logger.error("Error response: %s", error_data)
            if "error" in error_data:
                detail = error_data["error"]
                if isinstance(detail, dict) and "message" in detail:
                    error_msg = detail["message"]
                elif isinstance(detail, str):
                    error_msg = detail
        except Exception:
            try:
                text = response.text[:200]
                if text:
                    logger.error("Response text: %s", text)
            except Exception:
                pass

        raise ExternalServiceError(
            message=error_msg,
            status_code=response.status_code if 500 <= response.status_code < 600 else 502,
            details={"api_url": api_url, "status_code": response.status_code}
        )

    except requests.exceptions.Timeout:
        raise ExternalServiceError(
            message="Request timeout",
            status_code=504,
            details={"api_url": api_url, "timeout": TIMEOUT_API_REQUEST}
        )
    except requests.exceptions.ConnectionError as exc:
        raise ExternalServiceError(
            message="Connection error",
            status_code=503,
            details={"api_url": api_url, "error": str(exc)}
        )
    except requests.exceptions.RequestException as exc:
        logger.error("Request exception: %s", exc, exc_info=True)
        raise ExternalServiceError(
            message=f"Request failed: {str(exc)}",
            status_code=500,
            details={"api_url": api_url}
        )
    except (ValidationError, NotFoundError, UnauthorizedError, ForbiddenError, ExternalServiceError):
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Fetch models failed: %s", exc, exc_info=True)
        raise ExternalServiceError(
            message=f"Failed to fetch models: {str(exc)}",
            status_code=500,
            details={"api_url": api_url}
        )
