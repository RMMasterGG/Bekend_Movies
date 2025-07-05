import redis
from fastapi import Request
from limits.storage import MemoryStorage, RedisStorage

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")