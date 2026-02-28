import asyncio, time
import socket
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.db.session import settings, _to_session_mode

async def main():
    async_base = settings.DATABASE_URL
    url = async_base.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    engine = create_async_engine(
        url, 
        pool_size=5,
        max_overflow=0
    )
    
    t0 = time.time()
    try:
        async with engine.connect() as conn:
            t1 = time.time()
            print(f"Connect port 6543 (PgBouncer mode): {t1-t0:.2f}s")
            res = await conn.execute(text("SELECT 1"))
            print(res.scalar())
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
