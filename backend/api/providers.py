"""Provider API endpoints

This module handles all Provider-related API routes including:
- GET /api/providers - List all providers
- POST /api/providers - Add new provider
- DELETE /api/providers/<id> - Delete provider
- POST /api/providers/models - Fetch available models from provider
"""

from flask import Blueprint, request, jsonify, current_app

providers_bp = Blueprint('providers', __name__, url_prefix='/api/providers')


@providers_bp.route('', methods=['GET'])
def get_providers():
    """Get all API providers"""
    db = current_app.config['db']
    providers = db.get_all_providers()
    return jsonify(providers)


@providers_bp.route('', methods=['POST'])
def add_provider():
    """Add new API provider"""
    db = current_app.config['db']
    data = request.json
    
    try:
        provider_id = db.add_provider(
            name=data['name'],
            api_url=data['api_url'],
            api_key=data['api_key'],
            models=data.get('models', '')
        )
        return jsonify({'id': provider_id, 'message': 'Provider added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@providers_bp.route('/<int:provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    """Delete API provider"""
    db = current_app.config['db']
    
    try:
        db.delete_provider(provider_id)
        return jsonify({'message': 'Provider deleted successfully'})
    except Exception as e:
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
        return jsonify({'error': 'API URL and key are required'}), 400

    try:
        import requests
        
        # 智能处理 URL，自动添加 /v1
        api_url = normalize_api_url(api_url)
        models_endpoint = f'{api_url}/models'
        
        print(f"[INFO] Fetching models from: {models_endpoint}")
        
        # 使用标准的 OpenAI 兼容 API 格式
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 调用 /models 端点获取模型列表
        response = requests.get(models_endpoint, headers=headers, timeout=15)
        
        print(f"[INFO] Response status: {response.status_code}")
        
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
                print(f"[ERROR] Unknown response format: {result}")
                return jsonify({'error': '无法解析模型列表响应格式'}), 500
            
            if not models:
                return jsonify({'error': '未找到可用模型'}), 404
            
            print(f"[INFO] Found {len(models)} models")
            return jsonify({'models': models})
            
        elif response.status_code == 401:
            return jsonify({'error': 'API 密钥无效，请检查后重试'}), 401
        elif response.status_code == 403:
            # 403 通常表示权限不足或 API 密钥没有访问权限
            error_msg = 'API 访问被拒绝 (403)，可能原因：\n1. API 密钥权限不足\n2. API 密钥已过期\n3. 该 API 不支持列出模型'
            try:
                error_data = response.json()
                if 'error' in error_data:
                    detail = error_data['error']
                    if isinstance(detail, dict) and 'message' in detail:
                        error_msg = f"访问被拒绝: {detail['message']}"
                    elif isinstance(detail, str):
                        error_msg = f"访问被拒绝: {detail}"
                print(f"[ERROR] 403 response: {error_data}")
            except:
                pass
            return jsonify({'error': error_msg}), 403
        elif response.status_code == 404:
            return jsonify({'error': 'API 端点不存在，请检查 URL 是否正确 (可能需要添加或移除 /v1)'}), 404
        else:
            error_msg = f'API 返回错误状态码: {response.status_code}'
            try:
                error_data = response.json()
                print(f"[ERROR] Error response: {error_data}")
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
                        print(f"[ERROR] Response text: {text}")
                except:
                    pass
            return jsonify({'error': error_msg}), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({'error': '请求超时，请检查网络连接或 API 地址'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': '无法连接到 API，请检查 URL 是否正确'}), 503
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request exception: {e}")
        return jsonify({'error': f'请求失败: {str(e)}'}), 500
    except Exception as e:
        print(f"[ERROR] Fetch models failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取模型列表失败: {str(e)}'}), 500
