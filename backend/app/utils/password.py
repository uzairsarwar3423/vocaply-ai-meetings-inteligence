import asyncio
from concurrent.futures import ThreadPoolExecutor
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Thread pool for CPU-intensive bcrypt operations to avoid blocking
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="bcrypt_")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Synchronous password verification (blocking)"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Synchronous password hashing (blocking)"""
    return pwd_context.hash(password)

async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    """
    Async password verification using thread pool.
    Prevents blocking the event loop during bcrypt verification.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, pwd_context.verify, plain_password, hashed_password)

async def get_password_hash_async(password: str) -> str:
    """
    Async password hashing using thread pool.
    Prevents blocking the event loop during bcrypt hashing.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, pwd_context.hash, password)
