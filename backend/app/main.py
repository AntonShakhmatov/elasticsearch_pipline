import uvicorn
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import jobs_collection
from search import search_pages
from job_queue import add_crawl_job


app = FastAPI()


class CrawlRequest(BaseModel):
    url: str


@app.get("/")
async def root():
    return {"status": "running"}


@app.post("/crawl")
async def crawl(request: CrawlRequest):
    job_doc = {
        "url": request.url,
        "status": "queued",
        "error": None,
        "document_id": None,
    }

    result = await jobs_collection.insert_one(job_doc)

    job_id = str(result.inserted_id)

    await add_crawl_job(job_id, request.url)

    return {
        "job_id": job_id,
        "status": "queued",
        "url": request.url,
    }


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    try:
        object_id = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job_id")

    job = await jobs_collection.find_one({"_id": object_id})

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": str(job["_id"]),
        "url": job["url"],
        "status": job["status"],
        "error": job.get("error"),
        "document_id": job.get("document_id"),
    }


@app.get("/search")
async def search(query: str):
    results = await search_pages(query)

    return [
        {
            "id": item["_id"],
            "score": item["_score"],
            "url": item["_source"].get("url"),
            "title": item["_source"].get("title"),
            "emails": item["_source"].get("emails", []),
            "phones": item["_source"].get("phones", []),
        }
        for item in results
    ]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)