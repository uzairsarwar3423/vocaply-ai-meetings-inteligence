import asyncio, time
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def main():
    t0 = time.time()
    async with AsyncSessionLocal() as db:
        t1 = time.time()
        print(f"Checkout connection: {t1-t0:.2f}s")
        stmt = select(User).where(User.email == "test@example.com")
        result = await db.execute(stmt)
        t2 = time.time()
        print(f"Execute query: {t2-t1:.2f}s")
        print(result.scalar_one_or_none())

asyncio.run(main())
