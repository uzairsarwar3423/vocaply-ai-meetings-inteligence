import asyncio, time
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as db:
        t0 = time.time()
        await db.execute(text("SELECT 1"))
        t1 = time.time()
        print(f"SELECT 1 took: {t1-t0:.2f}s")
        
        t2 = time.time()
        await db.execute(text("SELECT 1"))
        t3 = time.time()
        print(f"Second SELECT 1 took: {t3-t2:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
