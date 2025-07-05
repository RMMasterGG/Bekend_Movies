import logging
import time
from http.client import responses
from logging import DEBUG

from redis import Redis
from functools import wraps
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import Redis

from app.security.limiter import limiter

from app.LoggingLogic import create_logger
from .DatabaseLogic import database
from .api.v1.v1_router import v1_router
API_STR="/api"

redis = Redis(host="localhost", port=6379, db=1)

def setup_cache():
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

uvicorn_logger = create_logger(name="Uvicorn", get_logger="uvicorn")

logging.getLogger("uvicorn.access").handlers.clear()
logging.getLogger("uvicorn.error").handlers.clear()
middleware_logger = create_logger(name="FastAPI", get_logger="app.core", level=DEBUG)

app = FastAPI()
app.state.limiter = limiter


@app.on_event("startup")
async def startup():
    setup_cache()
    await database.create_database()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    middleware_logger.debug(f"{request.headers}")
    start_time = time.time()
    protocol = request.scope["type"]
    http_version = request.scope.get("http_version")
    http_version_protocol = f"{str(protocol).upper()}/{http_version}"
    path = f"\"{request.method} /{str(request.url).strip(str(request.base_url))} {http_version_protocol}\""

    client = f"{request.client[0]}:{request.client[1]}"

    try:
        response = await call_next(request)
        duration = round(time.time() - start_time, 5)
        response_status_code_detail = f"{response.status_code} {responses.get(response.status_code)}"

        middleware_logger.info(f"{client} - {path} {response_status_code_detail} [{duration}s]")
        return response
    except Exception as e:
        middleware_logger.error(f"{str(e)}")

app.include_router(v1_router, prefix=API_STR)
