"""Model API endpoints implemented with FastAPI."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Body, Response

from backend.api.dependencies import ContainerDep
from backend.api.responses import success_response
from backend.config.constants import (
    ERROR_MSG_ADD_MODEL_FAILED,
    ERROR_MSG_DELETE_MODEL_FAILED,
    ERROR_MSG_MODEL_NOT_FOUND,
    ERROR_MSG_PROVIDER_NOT_FOUND,
    INFO_MSG_MODEL_DELETED,
    INFO_MSG_MODEL_INITIALIZED,
)
from backend.utils.errors import (
    ExternalServiceError,
    NotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("")
def get_models(container=ContainerDep) -> Dict[str, Any]:
    """Get all trading models."""
    db = container.db
    models = db.get_all_models()
    return success_response(models)


@router.post("", status_code=201)
def add_model(payload: Dict[str, Any] = Body(...), container=ContainerDep):
    """Add new trading model."""
    db = container.db
    trading_service = container.trading_service

    try:
        # Validate required fields
        required_fields = ["name", "provider_id", "model_name"]
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            raise ValidationError(
                message="缺少必填字段",
                details={"missing_fields": missing_fields}
            )

        provider = db.get_provider(payload["provider_id"])
        if not provider:
            raise NotFoundError(
                message=ERROR_MSG_PROVIDER_NOT_FOUND,
                details={"provider_id": payload["provider_id"]}
            )

        model_id = db.add_model(
            name=payload["name"],
            provider_id=payload["provider_id"],
            model_name=payload["model_name"],
            initial_capital=float(payload.get("initial_capital", 100000)),
        )

        trading_service.get_or_create_engine(model_id)
        logger.info(
            INFO_MSG_MODEL_INITIALIZED.format(model_id=model_id, name=payload["name"])
        )

        return success_response({"id": model_id})

    except (NotFoundError, ValidationError):
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("%s: %s", ERROR_MSG_ADD_MODEL_FAILED, exc, exc_info=True)
        raise ExternalServiceError(
            message=ERROR_MSG_ADD_MODEL_FAILED,
            status_code=500,
            details={"error": str(exc)}
        )


@router.delete("/{model_id}", status_code=204)
def delete_model(model_id: int, container=ContainerDep):
    """Delete trading model."""
    db = container.db
    trading_service = container.trading_service

    try:
        model = db.get_model(model_id)
        model_name = model["name"] if model else f"ID-{model_id}"

        db.delete_model(model_id)

        if model_id in trading_service.engines:
            del trading_service.engines[model_id]

        logger.info(INFO_MSG_MODEL_DELETED.format(model_id=model_id, name=model_name))
        return Response(status_code=204)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("%s %s: %s", ERROR_MSG_DELETE_MODEL_FAILED, model_id, exc, exc_info=True)
        raise ExternalServiceError(
            message=ERROR_MSG_DELETE_MODEL_FAILED,
            status_code=500,
            details={"model_id": model_id, "error": str(exc)}
        )


@router.post("/{model_id}/execute")
def execute_trading(model_id: int, container=ContainerDep):
    """Execute trading cycle for specific model."""
    db = container.db
    trading_service = container.trading_service

    model = db.get_model(model_id)
    if not model:
        raise NotFoundError(
            message=ERROR_MSG_MODEL_NOT_FOUND,
            details={"model_id": model_id}
        )

    try:
        result = trading_service.execute_trading_cycle(model_id)
        return success_response(result)
    except NotFoundError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Execute trading for model %s failed: %s", model_id, exc, exc_info=True)
        raise ExternalServiceError(
            message="执行交易失败",
            status_code=500,
            details={"model_id": model_id, "error": str(exc)}
        )
