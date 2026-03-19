import asyncio, time
from app.db.session import AsyncSessionLocal
from sqlalchemy import select, func
from app.models.meeting import Meeting

async def main():
    async with AsyncSessionLocal() as db:
        t0 = time.time()
        # Common query pattern for meeting list
        stmt = select(Meeting).where(Meeting.company_id == "f81d4fae-7dec-11d0-a765-00a0c91e6bf6", Meeting.deleted_at.is_(None)).limit(20)
        result = await db.execute(stmt)
        meetings = result.scalars().all()
        t1 = time.time()
        print(f"Fetch {len(meetings)} meetings: {t1-t0:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
