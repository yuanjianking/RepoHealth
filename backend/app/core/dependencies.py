"""
Dependency injection functions for FastAPI routes.
"""

import logging
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import Settings, get_settings
from app.core.logger import get_logger
from app.services.storage_service import get_storage_service, StorageService

# Security scheme for token authentication (optional)
security = HTTPBearer(auto_error=False)

# Configuration dependency
async def get_config() -> Settings:
    """
    Get application configuration.
    """
    return get_settings()


# Logger dependency
async def get_logger_dep() -> logging.Logger:
    """
    Get application logger.
    """
    return get_logger()


# Storage service dependency
async def get_storage() -> AsyncGenerator[StorageService, None]:
    """
    Get storage service instance.
    """
    storage = await get_storage_service()
    yield storage

