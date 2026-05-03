import psycopg
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests

from app.config import get_settings
from app.database import get_db, init_db
from app.services.scraper import get_content

settings = get_settings()
app = FastAPI(title="Ingestion Scraper API")


@app.on_event("startup")
async def startup():
    app.state.db = psycopg.connect(settings.dsn)
    init_db(settings.dsn)


@app.on_event("shutdown")
async def shutdown():
    db = getattr(app.state, "db", None)
    if db is not None:
        db.close()


class ScrapeRequest(BaseModel):
    url: HttpUrl


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok"}


@app.post("/scrape", tags=["scrape"])
async def scrape(req: ScrapeRequest, db: psycopg.Connection = Depends(get_db)):
    """Scrape the provided URL, save it to Postgres, and return the scraped result."""
    try:
        result = get_content(str(req.url))
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"scrape failed: {exc}")

    try:
        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO scraped_pages (url, title, content)
                VALUES (%s, %s, %s)
                ON CONFLICT (url) DO UPDATE
                  SET title = EXCLUDED.title,
                      content = EXCLUDED.content,
                      scraped_at = NOW()
                """,
                (str(req.url), result["title"], result["content"]),
            )
        db.commit()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"db save failed: {exc}")

    return result
