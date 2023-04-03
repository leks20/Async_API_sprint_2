import aioredis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from api.v1 import films, genre, person
from core.config import settings
from db import elastic, redis

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = await aioredis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}",
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis.redis), prefix="fastapi-cache")

    elastic.es = AsyncElasticsearch(
        hosts=[
            f"{settings.elastic_schema}://{settings.elastic_host}:{settings.elastic_port}"
        ]
    )

@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await redis.redis.wait_closed()
    await elastic.es.close()

@app.middleware("http")
async def check_header(request: Request, call_next):
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise HTTPException(status_code=400, detail='Request id is required')
    response = await call_next(request)
    return response

app.include_router(films.router, prefix="/api/v1/films")
app.include_router(genre.router, prefix="/api/v1/genre")
app.include_router(person.router, prefix="/api/v1/person")
