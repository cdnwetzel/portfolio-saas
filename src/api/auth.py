from fastapi import APIRouter, HTTPException, Depends
from core.database import get_db
from core.security import hash_password, verify_password, create_jwt_token
from models.database import Tenant, User
from sqlalchemy import select
import uuid
import logging

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)

@router.post("/signup")
async def signup(
    email: str,
    company_name: str,
    password: str,
    db = Depends(get_db)
):
    """Create new tenant account"""

    # Check if email already exists
    stmt = select(Tenant).where(Tenant.email == email)
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    # Create tenant
    tenant = Tenant(
        id=str(uuid.uuid4()),
        name=company_name,
        slug=company_name.lower().replace(" ", "-"),
        email=email,
        tier="free"
    )

    # Create admin user
    user = User(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        email=email,
        password_hash=hash_password(password),
        role="admin",
        name=company_name
    )

    db.add(tenant)
    db.add(user)
    await db.commit()

    logger.info(f"New tenant created: {company_name}")

    return {
        "tenant_id": tenant.id,
        "access_token": create_jwt_token(user.id, tenant.id),
        "token_type": "bearer"
    }

@router.post("/login")
async def login(
    email: str,
    password: str,
    db = Depends(get_db)
):
    """User login"""

    stmt = select(User).where(User.email == email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": create_jwt_token(user.id, user.tenant_id),
        "token_type": "bearer"
    }
