"""Model API endpoints

This module handles all Model-related API routes including:
- GET /api/models - List all models
- POST /api/models - Add new model
- DELETE /api/models/<id> - Delete model
- POST /api/models/<id>/execute - Execute trading cycle for model
"""

from flask import Blueprint, request, jsonify, current_app

models_bp = Blueprint('models', __name__, url_prefix='/api/models')


@models_bp.route('', methods=['GET'])
def get_models():
    """Get all trading models"""
    db = current_app.config['db']
    models = db.get_all_models()
    return jsonify(models)


@models_bp.route('', methods=['POST'])
def add_model():
    """Add new trading model"""
    db = current_app.config['db']
    trading_service = current_app.config['trading_service']
    data = request.json
    
    try:
        # Get provider info
        provider = db.get_provider(data['provider_id'])
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404

        model_id = db.add_model(
            name=data['name'],
            provider_id=data['provider_id'],
            model_name=data['model_name'],
            initial_capital=float(data.get('initial_capital', 100000))
        )

        # Initialize trading engine through service
        trading_service.get_or_create_engine(model_id)
        print(f"[INFO] Model {model_id} ({data['name']}) initialized")

        return jsonify({'id': model_id, 'message': 'Model added successfully'})

    except Exception as e:
        print(f"[ERROR] Failed to add model: {e}")
        return jsonify({'error': str(e)}), 500


@models_bp.route('/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    """Delete trading model"""
    db = current_app.config['db']
    trading_service = current_app.config['trading_service']
    
    try:
        model = db.get_model(model_id)
        model_name = model['name'] if model else f"ID-{model_id}"
        
        db.delete_model(model_id)
        
        # Remove engine from trading service
        if model_id in trading_service.engines:
            del trading_service.engines[model_id]
        
        print(f"[INFO] Model {model_id} ({model_name}) deleted")
        return jsonify({'message': 'Model deleted successfully'})
    except Exception as e:
        print(f"[ERROR] Delete model {model_id} failed: {e}")
        return jsonify({'error': str(e)}), 500


@models_bp.route('/<int:model_id>/execute', methods=['POST'])
def execute_trading(model_id):
    """Execute trading cycle for specific model"""
    db = current_app.config['db']
    trading_service = current_app.config['trading_service']
    
    # Ensure model exists
    model = db.get_model(model_id)
    if not model:
        return jsonify({'error': 'Model not found'}), 404
    
    try:
        # Get or create engine and execute
        result = trading_service.execute_trading_cycle(model_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
