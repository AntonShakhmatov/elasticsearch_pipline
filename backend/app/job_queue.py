import os
import json
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL","redis://redis:6379")
# REDIS_URL = "redis://localhost:6379"

redis_client = redis.from_url(REDIS_URL)

CRAWL_QUEUE = "crawl_queue"

async def add_crawl_job(job_id: str, url: str):
    job = {
        "job_id": job_id,
        "url": url
    }

    await redis_client.lpush(CRAWL_QUEUE, json.dumps(job))

async def get_crawl_job():
    result = await redis_client.brpop(CRAWL_QUEUE, timeout=5)

    if result is None:
        return None
    
    _, raw_job = result

    return json.loads(raw_job)