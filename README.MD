Pipeline:

Client / Swagger / curl
        │
        ▼
FastAPI API
        │
        │  POST /crawl
        ▼
MongoDB: jobs
        │
        │  создаём job со статусом queued
        ▼
Redis Queue
        │
        │  кладём задачу: job_id + url
        ▼
Worker
        │
        │  забирает задачу
        │  меняет статус на processing
        ▼
aiohttp Crawler
        │
        │  скачивает HTML страницы
        ▼
BeautifulSoup Parser
        │
        │  извлекает title, text, emails, phones, links
        ▼
MongoDB: pages
        │
        │  сохраняет распарсенный документ
        ▼
Elasticsearch: pages index
        │
        │  индексирует документ для быстрого поиска
        ▼
MongoDB: jobs
        │
        │  обновляет job: done / failed
        ▼
GET /jobs/{job_id}
GET /search?query=...