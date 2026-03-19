import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(text("SELECT pid, state, query, wait_event_type, wait_event FROM pg_stat_activity WHERE state != 'idle'"))
            rows = result.all()
            print(f"Active connections: {len(rows)}")
            for row in rows:
                print(f"PID: {row.pid} | State: {row.state} | Wait: {row.wait_event_type}/{row.wait_event} | Query: {row.query[:100]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
