import asyncio, time
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.db.session import _to_session_mode, settings

async def main():
    async_base = _to_session_mode(settings.DATABASE_URL)
    url = async_base.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Supabase uses IPv6/IPv4 magic or proxy that requires SSL
    conn_args = {"ssl": "require"}
    print(f"URL: {url}")
        
    engine = create_async_engine(url, connect_args=conn_args)
    
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
