"""System API endpoints

This module handles all system-related API routes including:
- GET /api/settings - Get system settings
- PUT /api/settings - Update system settings
- GET /api/version - Get version information
- GET /api/check-update - Check for updates
- GET /api/health - Lightweight health check
"""

import re
import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from backend.config.constants import (
    DEFAULT_TRADE_FEE_RATE,
    DEFAULT_MARKET_REFRESH_INTERVAL,
    DEFAULT_PORTFOLIO_REFRESH_INTERVAL,
    DEFAULT_TRADING_FREQUENCY_MINUTES,
    SUCCESS_MSG_SETTINGS_UPDATED,
    ERROR_MSG_UPDATE_SETTINGS_FAILED,
    INFO_MSG_GITHUB_API_ERROR,
    WARN_MSG_UPDATE_CHECK_FAILED,
    WARN_MSG_NETWORK_ERROR,
)
from backend.utils.version import (
    __version__,
    __github_owner__,
    __repo__,
    GITHUB_REPO_URL,
    LATEST_RELEASE_URL
)

logger = logging.getLogger(__name__)
system_bp = Blueprint('system', __name__, url_prefix='/api')


@system_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get system settings"""
    db = g.container.db
    
    try:
        settings = db.get_settings()
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Failed to get settings: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@system_bp.route('/config', methods=['GET'])
def get_config():
    """Get frontend configuration"""
    from flask import current_app
    config = current_app.config['app_config']
    db = g.container.db
    settings = db.get_settings()
    
    try:
        return jsonify({
            'market_refresh_interval': settings.get('market_refresh_interval', DEFAULT_MARKET_REFRESH_INTERVAL),
            'portfolio_refresh_interval': settings.get('portfolio_refresh_interval', DEFAULT_PORTFOLIO_REFRESH_INTERVAL),
            'trading_coins': config.DEFAULT_COINS,
            'trade_fee_rate': settings.get('trading_fee_rate', DEFAULT_TRADE_FEE_RATE)
        })
    except Exception as e:
        logger.error(f"Failed to get config: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@system_bp.route('/settings', methods=['PUT'])
def update_settings():
    """Update system settings"""
    db = g.container.db
    
    try:
        data = request.json or {}
        trading_frequency_minutes = max(
            int(data.get('trading_frequency_minutes', DEFAULT_TRADING_FREQUENCY_MINUTES)),
            1
        )
        trading_fee_rate = max(float(data.get('trading_fee_rate', DEFAULT_TRADE_FEE_RATE)), 0.0)
        market_refresh_interval = max(
            int(data.get('market_refresh_interval', DEFAULT_MARKET_REFRESH_INTERVAL)),
            1
        )
        portfolio_refresh_interval = max(
            int(data.get('portfolio_refresh_interval', DEFAULT_PORTFOLIO_REFRESH_INTERVAL)),
            1
        )

        success = db.update_settings(
            trading_frequency_minutes,
            trading_fee_rate,
            market_refresh_interval,
            portfolio_refresh_interval
        )

        if success:
            trading_service = g.container.trading_service
            if trading_service:
                trading_service.update_trade_fee_rate(trading_fee_rate)
            return jsonify({'message': SUCCESS_MSG_SETTINGS_UPDATED})
        else:
            return jsonify({'error': ERROR_MSG_UPDATE_SETTINGS_FAILED}), 500
    except Exception as e:
        logger.error(f"{ERROR_MSG_UPDATE_SETTINGS_FAILED}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@system_bp.route('/version', methods=['GET'])
def get_version():
    """Get current version information"""
    return jsonify({
        'current_version': __version__,
        'github_repo': GITHUB_REPO_URL,
        'latest_release_url': LATEST_RELEASE_URL
    })


@system_bp.route('/check-update', methods=['GET'])
def check_update():
    """Check for GitHub updates"""
    try:
        import requests

        # Get latest release from GitHub
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AITradeGame/1.0'
        }

        # Try to get latest release
        try:
            response = requests.get(
                f"https://api.github.com/repos/{__github_owner__}/{__repo__}/releases/latest",
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get('tag_name', '').lstrip('v')
                release_url = release_data.get('html_url', '')
                release_notes = release_data.get('body', '')

                # Compare versions
                is_update_available = compare_versions(latest_version, __version__) > 0

                return jsonify({
                    'update_available': is_update_available,
                    'current_version': __version__,
                    'latest_version': latest_version,
                    'release_url': release_url,
                    'release_notes': release_notes,
                    'repo_url': GITHUB_REPO_URL
                })
            else:
                # If API fails, still return current version info
                return jsonify({
                    'update_available': False,
                    'current_version': __version__,
                    'error': WARN_MSG_UPDATE_CHECK_FAILED
                })
        except Exception as e:
            logger.warning(INFO_MSG_GITHUB_API_ERROR.format(error=str(e)))
            return jsonify({
                'update_available': False,
                'current_version': __version__,
                'error': WARN_MSG_NETWORK_ERROR
            })

    except Exception as e:
        logger.error(f"Check update failed: {e}", exc_info=True)
        return jsonify({
            'update_available': False,
            'current_version': __version__,
            'error': str(e)
        }), 500


@system_bp.route('/health', methods=['GET'])
def health_check():
    """Lightweight health check for frontend status indicator."""
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        db = g.container.db
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        finally:
            conn.close()
        return jsonify({
            'status': 'ok',
            'database': 'ok',
            'timestamp': timestamp
        })
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        return jsonify({
            'status': 'error',
            'database': 'error',
            'timestamp': timestamp,
            'message': str(exc)
        }), 503


def compare_versions(version1, version2):
    """Compare two version strings.

    Returns:
        1 if version1 > version2
        0 if version1 == version2
        -1 if version1 < version2
    """
    def normalize(v):
        # Extract numeric parts from version string
        parts = re.findall(r'\d+', v)
        # Pad with zeros to make them comparable
        return [int(p) for p in parts]

    v1_parts = normalize(version1)
    v2_parts = normalize(version2)

    # Pad shorter version with zeros
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))

    # Compare
    if v1_parts > v2_parts:
        return 1
    elif v1_parts < v2_parts:
        return -1
    else:
        return 0
