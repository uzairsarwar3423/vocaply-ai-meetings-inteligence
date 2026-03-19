import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as db:
        for table in ["users", "companies", "meetings", "action_items", "calendar_events"]:
            try:
                result = await db.execute(text(f"SELECT count(*) FROM {table}"))
                count = result.scalar()
                print(f"Table {table}: {count} rows")
            except Exception as e:
                print(f"Error counting {table}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
