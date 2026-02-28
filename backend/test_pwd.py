import asyncio, time
from app.utils.password import verify_password_async, get_password_hash

async def main():
    h = get_password_hash("test")
    t0 = time.time()
    await verify_password_async("test", h)
    t1 = time.time()
    print(f"Time: {t1-t0:.2f}s")

asyncio.run(main())
