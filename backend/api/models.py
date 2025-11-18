"""Model API endpoints

This module handles all Model-related API routes including:
- GET /api/models - List all models
- POST /api/models - Add new model
- DELETE /api/models/<id> - Delete model
- POST /api/models/<id>/execute - Execute trading cycle for model
"""

import logging
from flask import Blueprint, request, jsonify, g

from backend.config.constants import (
    ERROR_MSG_PROVIDER_NOT_FOUND,
    ERROR_MSG_MODEL_NOT_FOUND,
    ERROR_MSG_ADD_MODEL_FAILED,
    ERROR_MSG_DELETE_MODEL_FAILED,
    SUCCESS_MSG_MODEL_ADDED,
    SUCCESS_MSG_MODEL_DELETED,
    INFO_MSG_MODEL_INITIALIZED,
    INFO_MSG_MODEL_DELETED,
)

logger = logging.getLogger(__name__)
models_bp = Blueprint('models', __name__, url_prefix='/api/models')


@models_bp.route('', methods=['GET'])
def get_models():
    """Get all trading models"""
    db = g.container.db
    models = db.get_all_models()
    return jsonify(models)


@models_bp.route('', methods=['POST'])
def add_model():
    """Add new trading model"""
    db = g.container.db
    trading_service = g.container.trading_service
    data = request.json
    
    try:
        # Get provider info
        provider = db.get_provider(data['provider_id'])
        if not provider:
            return jsonify({'error': ERROR_MSG_PROVIDER_NOT_FOUND}), 404

        model_id = db.add_model(
            name=data['name'],
            provider_id=data['provider_id'],
            model_name=data['model_name'],
            initial_capital=float(data.get('initial_capital', 100000))
        )

        # Initialize trading engine through service
        trading_service.get_or_create_engine(model_id)
        logger.info(INFO_MSG_MODEL_INITIALIZED.format(model_id=model_id, name=data['name']))

        return jsonify({'id': model_id, 'message': SUCCESS_MSG_MODEL_ADDED}), 201

    except Exception as e:
        logger.error(f"{ERROR_MSG_ADD_MODEL_FAILED}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@models_bp.route('/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    """Delete trading model"""
    db = g.container.db
    trading_service = g.container.trading_service
    
    try:
        model = db.get_model(model_id)
        model_name = model['name'] if model else f"ID-{model_id}"
        
        db.delete_model(model_id)
        
        # Remove engine from trading service
        if model_id in trading_service.engines:
            del trading_service.engines[model_id]
        
        logger.info(INFO_MSG_MODEL_DELETED.format(model_id=model_id, name=model_name))
        return jsonify({'message': SUCCESS_MSG_MODEL_DELETED})
    except Exception as e:
        logger.error(f"{ERROR_MSG_DELETE_MODEL_FAILED} {model_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@models_bp.route('/<int:model_id>/execute', methods=['POST'])
def execute_trading(model_id):
    """Execute trading cycle for specific model"""
    db = g.container.db
    trading_service = g.container.trading_service
    
    # Ensure model exists
    model = db.get_model(model_id)
    if not model:
        return jsonify({'error': ERROR_MSG_MODEL_NOT_FOUND}), 404
    
    try:
        # Get or create engine and execute
        result = trading_service.execute_trading_cycle(model_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Execute trading for model {model_id} failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
