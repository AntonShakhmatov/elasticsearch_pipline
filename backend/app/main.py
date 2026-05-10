import uvicorn
from fastapi import FastAPI
from db import pages_collection
from crawler import fetch_page
from parser import parse_html
from search import index_page, search_pages

app = FastAPI()

@app.get("/")
async def root():
    return{"status": "running"}

@app.post("/crawl")
async def crawl(url: str):
    html = await fetch_page(url)
    parsed = parse_html(html)
    document = {
        "url": url,
        **parsed
    }

    result = await pages_collection.insert_one(document)
    document_id = str(result.inserted_id)
    await index_page(document_id, document)

    return {
        "inserted_id": document_id,
        "url": document["url"],
        "title": parsed["title"],
        "emails": parsed["emails"],
        "phones": parsed["phones"],
        "links_count": len(parsed["links"]),
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