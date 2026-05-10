import os
from elasticsearch import AsyncElasticsearch

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")

es = AsyncElasticsearch(ELASTICSEARCH_URL)

INDEX_NAME = "pages"

async def index_page(document_id: str, document: dict):
    document.pop("_id", None)
    await es.index(
        index=INDEX_NAME,
        id=document_id,
        document=document
    )

async def search_pages(query: str):
    response = await es.search(
        index=INDEX_NAME,
        query={
            "multi_match": {
                "query": query,
                "fields": ["title^2", "text", "emails", "phones", "url"]
            }
        }
    )

    return response["hits"]["hits"]