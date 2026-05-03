import psycopg
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
import asyncio
from starlette.concurrency import run_in_threadpool

from app.config import get_settings
from app.database import get_db, init_db, Database
from app.services.scraper import get_content, get_list_of_links

settings = get_settings()
app = FastAPI(title="Ingestion Scraper API")


@app.on_event("startup")
async def startup():
    conn = psycopg.connect(settings.dsn)
    app.state.db = Database(conn)
    init_db(settings.dsn)


@app.on_event("shutdown")
async def shutdown():
    db = getattr(app.state, "db", None)
    if db is not None:
        # Database.close() will close underlying connection
        try:
            db.close()
        except Exception:
            pass


class ScrapeRequest(BaseModel):
    url: HttpUrl


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok"}


@app.post("/scrape", tags=["scrape"])
async def scrape(req: ScrapeRequest, db: Database = Depends(get_db)):
    """"Scrape the provided URL and save the title and content to the database.
    Also extracts all links from the page and attempts to scrape them as well."""
    try:
        links = await run_in_threadpool(get_list_of_links, str(req.url))
        for link in links:
            try:
                print(f"Scraping {link}...")
                result = await run_in_threadpool(get_content, link)
                db.save_scraped_page(link, result["title"], result["content"])
            except requests.RequestException as exc:
                print(f"Failed to scrape {link}: {exc}")
                continue
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return {"message": f"Scraped {len(links)} pages from {req.url}", "total_links": len(links)}
@app.post("/list_links", tags=["scrape"])
async def list_links(req: ScrapeRequest):
    """List all links found on the provided URL."""
    try:
        links = get_list_of_links(str(req.url))
        # filter out link with *.html extension
        links = [link for link in links if link.endswith(".html")]
        print(f"Found {len(links)} links on {req.url}")
        # deduplicate links        
        links = list(set(links))
        print(f"Deduplicated to {len(links)} links")
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"failed to list links: {exc}")

    return {"links": links}
