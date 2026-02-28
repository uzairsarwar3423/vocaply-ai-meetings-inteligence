"""
Performance optimization utilities for Vocaply API
- Response caching middleware
- Query timing tracking
- Performance monitoring
"""
import time
import logging
from typing import Callable, Optional
from datetime import datetime, timedelta
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import json

logger = logging.getLogger(__name__)

# Simple in-memory cache with TTL
class SimpleCache:
    def __init__(self):
        self.cache = {}
    
    def get(self, key: str) -> Optional[dict]:
        """Get cached value if not expired"""
        if key in self.cache:
            value, expiry = self.cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: dict, ttl_seconds: int = 300):
        """Set cache value with TTL"""
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        self.cache[key] = (value, expiry)
    
    def clear_expired(self):
        """Remove expired entries"""
        now = datetime.now()
        expired_keys = [k for k, (_, expiry) in self.cache.items() if now >= expiry]
        for k in expired_keys:
            del self.cache[k]

response_cache = SimpleCache()

def get_cache_key(request: Request) -> Optional[str]:
    """Generate cache key for GET requests"""
    # Only cache GET requests without query parameters for list endpoints
    if request.method != "GET":
        return None
    
    # Cache list endpoints but with user context
    path = request.url.path
    query_string = request.url.query
    
    # Only cache certain paths
    cacheable_paths = [
        "/api/v1/action-items",
        "/api/v1/meetings",
        "/api/v1/transcripts",
        "/api/v1/summaries",
    ]
    
    if any(path.startswith(p) for p in cacheable_paths):
        # Include minimal query params in cache key
        return f"{path}?{query_string}"
    
    return None

async def timing_middleware(request: Request, call_next: Callable) -> Response:
    """Track request timing and log slow queries"""
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    # Log slow requests (> 500ms)
    if duration > 0.5:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} took {duration:.2f}s"
        )
    
    # Add timing header
    response.headers["X-Process-Time"] = str(duration)
    
    return response

async def cache_middleware(request: Request, call_next: Callable) -> Response:
    """Cache GET responses for list endpoints"""
    cache_key = get_cache_key(request)
    
    # Check cache for GET requests
    if cache_key:
        cached_data = response_cache.get(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for {cache_key}")
            return JSONResponse(
                content=cached_data,
                headers={"X-Cache": "HIT"}
            )
    
    # Process request
    response = await call_next(request)
    
    # Cache successful responses
    if cache_key and response.status_code == 200:
        try:
            # Try to cache the response
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            if body:
                data = json.loads(body)
                response_cache.set(cache_key, data, ttl_seconds=300)
            
            # Return the response with cache headers
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        except Exception as e:
            logger.error(f"Cache write error: {e}")
            # Return response normally if caching fails
            return response
    
    return response
