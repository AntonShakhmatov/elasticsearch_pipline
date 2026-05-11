import asyncio
from bson import ObjectId
from job_queue import get_crawl_job
from crawler import fetch_page
from parser import parse_html
from db import pages_collection, jobs_collection
from search import index_page


async def process_job(job: dict):
    job_id = job["job_id"]
    url = job["url"]

    print(f"Processing job {job_id}: {url}")

    await jobs_collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"status": "processing"}}
    )

    try:
        html = await fetch_page(url)
        parsed = parse_html(html)

        document = {
            "url": url,
            **parsed,
        }

        result = await pages_collection.insert_one(document)
        document_id = str(result.inserted_id)

        await index_page(document_id, document)

        await jobs_collection.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "status": "done",
                    "document_id": document_id,
                    "error": None
                }
            }
        )

        print(f"Done job {job_id}: {url}")

    except Exception as e:
        await jobs_collection.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e)
                }
            }
        )

        print(f"Failed job {job_id}: {e}")


async def main():
    print("Worker started")

    max_concurrent_jobs = 10
    semaphore = asyncio.Semaphore(max_concurrent_jobs)

    async def run_job(job: dict):
        async with semaphore:
            await process_job(job)

    while True:
        job = await get_crawl_job()

        if job is None:
            continue

        asyncio.create_task(run_job(job))


if __name__ == "__main__":
    asyncio.run(main())