from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24 * 7  # 7 days


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.secret_key,
        algorithm=JWT_ALGORITHM,
    )


def decode_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except JWTError:
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_google_id(db: AsyncSession, google_id: str) -> User | None:
    result = await db.execute(select(User).where(User.google_id == google_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    email: str,
    password: str | None = None,
    full_name: str | None = None,
    google_id: str | None = None,
    avatar_url: str | None = None,
    is_email_verified: bool = False,
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password) if password else None,
        full_name=full_name,
        google_id=google_id,
        avatar_url=avatar_url,
        is_email_verified=is_email_verified,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
