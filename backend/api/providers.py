"""Provider API endpoints

This module handles all Provider-related API routes including:
- GET /api/providers - List all providers
- POST /api/providers - Add new provider
- DELETE /api/providers/<id> - Delete provider
- POST /api/providers/models - Fetch available models from provider
"""

import logging
from flask import Blueprint, request, jsonify, g

from backend.config.constants import (
    TIMEOUT_API_REQUEST,
    ERROR_MSG_MISSING_REQUIRED_FIELDS,
    ERROR_MSG_INVALID_API_KEY,
    ERROR_MSG_API_ACCESS_DENIED,
    ERROR_MSG_API_ENDPOINT_NOT_FOUND,
    ERROR_MSG_NO_MODELS_FOUND,
    ERROR_MSG_UNKNOWN_RESPONSE_FORMAT,
    ERROR_MSG_REQUEST_TIMEOUT,
    ERROR_MSG_CONNECTION_ERROR,
    ERROR_MSG_REQUEST_FAILED,
    ERROR_MSG_FETCH_MODELS_FAILED,
    SUCCESS_MSG_PROVIDER_ADDED,
    SUCCESS_MSG_PROVIDER_DELETED,
    INFO_MSG_FETCHING_MODELS,
    INFO_MSG_RESPONSE_STATUS,
    INFO_MSG_MODELS_FOUND,
)

logger = logging.getLogger(__name__)
providers_bp = Blueprint('providers', __name__, url_prefix='/api/providers')


@providers_bp.route('', methods=['GET'])
def get_providers():
    """Get all API providers"""
    db = g.container.db
    providers = db.get_all_providers()
    return jsonify(providers)


@providers_bp.route('', methods=['POST'])
def add_provider():
    """Add new API provider"""
    db = g.container.db
    data = request.json
    
    try:
        provider_id = db.add_provider(
            name=data['name'],
            api_url=data['api_url'],
            api_key=data['api_key'],
            models=data.get('models', '')
        )
        return jsonify({'id': provider_id, 'message': SUCCESS_MSG_PROVIDER_ADDED}), 201
    except Exception as e:
        logger.error(f"Failed to add provider: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@providers_bp.route('/<int:provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    """Delete API provider"""
    db = g.container.db
    
    try:
        db.delete_provider(provider_id)
        return jsonify({'message': SUCCESS_MSG_PROVIDER_DELETED})
    except Exception as e:
        logger.error(f"Failed to delete provider {provider_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def normalize_api_url(url: str) -> str:
    """智能处理 API URL，自动添加 /v1 如果需要"""
    import re
    from urllib.parse import urlparse
    
    trimmed = url.strip().rstrip('/')
    
    # 如果已经包含版本号（/v1, /v2 等），直接返回
    if re.search(r'/v\d+$', trimmed, re.IGNORECASE):
        return trimmed
    
    # 解析 URL 获取路径部分
    parsed = urlparse(trimmed)
    path = parsed.path
    
    # 不需要添加 /v1 的情况：
    # 1. 路径中已经包含 /api/（注意是路径，不是域名）
    # 2. 本地服务
    if path and '/api/' in path:
        return trimmed
    
    if any(host in parsed.netloc for host in ['localhost', '127.0.0.1']) or \
       parsed.netloc.startswith('192.168.') or parsed.netloc.startswith('10.'):
        return trimmed
    
    # 默认添加 /v1（大多数 OpenAI 兼容 API 都需要）
    return f'{trimmed}/v1'


@providers_bp.route('/models', methods=['POST'])
def fetch_provider_models():
    """Fetch available models from provider's API"""
    data = request.json
    api_url = data.get('api_url')
    api_key = data.get('api_key')

    if not api_url or not api_key:
        return jsonify({'error': ERROR_MSG_MISSING_REQUIRED_FIELDS}), 400

    try:
        import requests
        
        # 智能处理 URL，自动添加 /v1
        api_url = normalize_api_url(api_url)
        models_endpoint = f'{api_url}/models'
        
        logger.info(INFO_MSG_FETCHING_MODELS.format(endpoint=models_endpoint))
        
        # 使用标准的 OpenAI 兼容 API 格式
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 调用 /models 端点获取模型列表
        response = requests.get(models_endpoint, headers=headers, timeout=TIMEOUT_API_REQUEST)
        
        logger.info(INFO_MSG_RESPONSE_STATUS.format(status=response.status_code))
        
        if response.status_code == 200:
            result = response.json()
            
            # 解析响应数据
            if 'data' in result and isinstance(result['data'], list):
                # 标准 OpenAI 格式: {"data": [{"id": "model-name", ...}, ...]}
                models = [m['id'] for m in result['data'] if 'id' in m]
            elif 'models' in result and isinstance(result['models'], list):
                # 某些提供方使用 "models" 字段
                models = result['models']
            elif isinstance(result, list):
                # 直接返回数组
                models = result
            else:
                logger.error(f"Unknown response format: {result}")
                return jsonify({'error': ERROR_MSG_UNKNOWN_RESPONSE_FORMAT}), 500
            
            if not models:
                return jsonify({'error': ERROR_MSG_NO_MODELS_FOUND}), 404
            
            logger.info(INFO_MSG_MODELS_FOUND.format(count=len(models)))
            return jsonify({'models': models})
            
        elif response.status_code == 401:
            return jsonify({'error': ERROR_MSG_INVALID_API_KEY}), 401
        elif response.status_code == 403:
            # 403 通常表示权限不足或 API 密钥没有访问权限
            error_msg = ERROR_MSG_API_ACCESS_DENIED
            try:
                error_data = response.json()
                if 'error' in error_data:
                    detail = error_data['error']
                    if isinstance(detail, dict) and 'message' in detail:
                        error_msg = f"访问被拒绝: {detail['message']}"
                    elif isinstance(detail, str):
                        error_msg = f"访问被拒绝: {detail}"
                logger.error(f"403 response: {error_data}")
            except:
                pass
            return jsonify({'error': error_msg}), 403
        elif response.status_code == 404:
            return jsonify({'error': ERROR_MSG_API_ENDPOINT_NOT_FOUND}), 404
        else:
            error_msg = f'API 返回错误状态码: {response.status_code}'
            try:
                error_data = response.json()
                logger.error(f"Error response: {error_data}")
                if 'error' in error_data:
                    detail = error_data['error']
                    if isinstance(detail, dict) and 'message' in detail:
                        error_msg = detail['message']
                    elif isinstance(detail, str):
                        error_msg = detail
            except:
                # 如果无法解析 JSON，尝试获取文本内容
                try:
                    text = response.text[:200]
                    if text:
                        logger.error(f"Response text: {text}")
                except:
                    pass
            return jsonify({'error': error_msg}), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({'error': ERROR_MSG_REQUEST_TIMEOUT}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': ERROR_MSG_CONNECTION_ERROR}), 503
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {e}", exc_info=True)
        return jsonify({'error': ERROR_MSG_REQUEST_FAILED.format(detail=str(e))}), 500
    except Exception as e:
        logger.error(f"Fetch models failed: {e}", exc_info=True)
        return jsonify({'error': ERROR_MSG_FETCH_MODELS_FAILED.format(detail=str(e))}), 500
