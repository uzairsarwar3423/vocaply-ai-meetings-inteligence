from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# ──────────────────────────────────────────────────────────────────────────────
# Supabase connection modes:
#   port 6543 = PgBouncer TRANSACTION mode → incompatible with asyncpg
#                prepared statements (causes DuplicatePreparedStatementError)
#   port 5432 = Direct / SESSION pooler → safe for asyncpg & SQLAlchemy
#
# Solution: use port 5432 for BOTH engines.
# If your DATABASE_URL doesn't use 6543 this replace() is a no-op, so safe.
# ──────────────────────────────────────────────────────────────────────────────

def _to_session_mode(url: str) -> str:
    """Swap Supabase PgBouncer port 6543 → 5432 (direct session mode)."""
    return url.replace(":6543/", ":5432/")


# ── Sync engine (used by sync code / Celery workers) ─────────────────────────
SYNC_DATABASE_URL = _to_session_mode(settings.DATABASE_URL)

engine = create_engine(
    SYNC_DATABASE_URL,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Async engine (used by FastAPI async endpoints) ────────────────────────────
_async_base = _to_session_mode(settings.DATABASE_URL)

# Rewrite scheme: postgresql:// → postgresql+asyncpg://
if _async_base.startswith("postgresql://"):
    ASYNC_DATABASE_URL = _async_base.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _async_base.startswith("postgres://"):
    ASYNC_DATABASE_URL = _async_base.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = _async_base

# Optimized async engine for high performance and scalability
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=12,                # Balanced pool size
    max_overflow=20,             # Allow bursts
    pool_pre_ping=True,          # Essential for Supabase reliability
    pool_recycle=300,            # Refresh connections every 5 mins
    connect_args={
        "command_timeout": 30,    # Don't let queries hang forever
        "server_settings": {
            "jit": "off",         # JIT can slow down simple queries on small tables
            "statement_timeout": "60000", # 60s limit for any single statement
        }
    },
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
