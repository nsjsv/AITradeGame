#!/usr/bin/env python3
"""Script to encrypt existing API keys in database

This script should be run once to encrypt all existing unencrypted API keys.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from urllib.parse import urlparse

from backend.config.settings import Config
from backend.data.postgres_db import PostgreSQLDatabase
from backend.utils.encryption import encrypt_api_key
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Encrypt all existing API keys"""
    config = Config()
    db = PostgreSQLDatabase(config.POSTGRES_URI)
    
    logger.info("Starting API key encryption...")
    parsed = urlparse(config.POSTGRES_URI)
    safe_db = f"{parsed.scheme}://{parsed.hostname or ''}"
    if parsed.port:
        safe_db += f":{parsed.port}"
    safe_db += parsed.path or ""
    logger.info("Database: %s", safe_db)
    
    # Get all providers
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, api_key FROM providers")
    providers = cursor.fetchall()
    
    if not providers:
        logger.info("No providers found in database")
        conn.close()
        return
    
    logger.info(f"Found {len(providers)} providers")
    
    encrypted_count = 0
    skipped_count = 0
    
    for provider_id, name, api_key in providers:
        # Check if already encrypted (Fernet encrypted strings start with 'gAAAAAB')
        if api_key and api_key.startswith('gAAAAAB'):
            logger.info(f"Provider '{name}' (ID: {provider_id}) - Already encrypted, skipping")
            skipped_count += 1
            continue
        
        try:
            # Encrypt the API key
            encrypted_key = encrypt_api_key(api_key)
            
            # Update in database
            cursor.execute(
                "UPDATE providers SET api_key = %s WHERE id = %s",
                (encrypted_key, provider_id)
            )
            
            logger.info(f"Provider '{name}' (ID: {provider_id}) - Encrypted successfully")
            encrypted_count += 1
            
        except Exception as e:
            logger.error(f"Provider '{name}' (ID: {provider_id}) - Encryption failed: {e}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Encryption complete!")
    logger.info(f"  Encrypted: {encrypted_count}")
    logger.info(f"  Skipped: {skipped_count}")
    logger.info(f"  Total: {len(providers)}")
    logger.info("=" * 60)
    
    if encrypted_count > 0:
        logger.info("")
        logger.info("IMPORTANT: Backup your .encryption_key file!")
        logger.info("If lost, encrypted API keys cannot be recovered.")


if __name__ == '__main__':
    main()
