import asyncio, time
import socket
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.db.session import settings, _to_session_mode

async def main():
    async_base = _to_session_mode(settings.DATABASE_URL)
    url = async_base.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    conn_args = {"ssl": "require"}
    
    # Let's try explicit IPv4 since Supabase asyncpg has issues with IPv6 fallback sometimes
    # Using host resolution or TCP timeout
    conn_args['command_timeout'] = 10
    conn_args['timeout'] = 10
        
    engine = create_async_engine(
        url, 
        connect_args=conn_args,
        pool_size=5,
        max_overflow=0
    )
    
    t0 = time.time()
    try:
        async with engine.connect() as conn:
            t1 = time.time()
            print(f"Connect: {t1-t0:.2f}s")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
