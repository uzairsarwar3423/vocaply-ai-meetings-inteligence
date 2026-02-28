import asyncio, time
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.db.session import settings, _to_session_mode

async def main():
    async_base = settings.DATABASE_URL
    url = async_base.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    engine = create_async_engine(
        url, 
        pool_size=10,
        max_overflow=10,
        pool_pre_ping=False, # TRY DISABLING THIS
        connect_args={
            "statement_cache_size": 0,    # Fix PgBouncer issue
            "prepared_statement_cache_size": 0
        }
    )
    
    t0 = time.time()
    try:
        async with engine.connect() as conn:
            t1 = time.time()
            print(f"Connect with statement_cache=0: {t1-t0:.2f}s")
            res = await conn.execute(text("SELECT 1"))
            print(res.scalar())
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
