from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredential
from core.security import verify_jwt_token
from core.database import get_db
from sqlalchemy import select
from models.database import Tenant
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_tenant(
    credentials: HTTPAuthCredential = Depends(security),
    db = Depends(get_db)
) -> Tenant:
    """
    Extract tenant from JWT or API key.
    """
    token = credentials.credentials

    # Verify JWT
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch tenant
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=401, detail="Tenant not found or inactive")

    return tenant
