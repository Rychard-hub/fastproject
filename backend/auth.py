"""Shared admin-key auth dependency for mutating endpoints."""
import os
import secrets
from typing import Optional
from fastapi import Header, HTTPException


def require_admin(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """Require a valid X-Admin-Key header matching ADMIN_API_KEY."""
    expected = os.getenv("ADMIN_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="Admin API key not configured on server")
    if not x_admin_key or not secrets.compare_digest(x_admin_key, expected):
        raise HTTPException(status_code=401, detail="Invalid admin key")
