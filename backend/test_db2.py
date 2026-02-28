import asyncio, time
from app.db.session import _to_session_mode, settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    async_base = _to_session_mode(settings.DATABASE_URL)
    if async_base.startswith("postgresql://"):
        url = async_base.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Try connecting with sslmode
    if "?" not in url:
        url += "?sslmode=require"
        
    print(f"URL: {url}")
        
    engine = create_async_engine(url)
    
    t0 = time.time()
    try:
        async with engine.connect() as conn:
            t1 = time.time()
            print(f"Connect: {t1-t0:.2f}s")
            res = await conn.execute(text("SELECT 1"))
            print(res.scalar())
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
