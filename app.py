import os
import asyncio

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

from src.qiita_client import fetch_all_articles, QiitaAPIError

load_dotenv()

app = FastAPI(title="Qiita Admin Dashboard")
app.mount("/static", StaticFiles(directory="static"), name="static")
jinja_env = Environment(loader=FileSystemLoader("templates"), autoescape=True)


def get_token() -> str | None:
    return os.environ.get("QIITA_TOKEN")


def render(template_name: str, **ctx: object) -> HTMLResponse:
    html = jinja_env.get_template(template_name).render(**ctx)
    return HTMLResponse(content=html)


@app.get("/", response_class=HTMLResponse)
async def index():
    return render("articles.html", active_menu="articles")


@app.get("/articles", response_class=HTMLResponse)
async def articles_page():
    return render("articles.html", active_menu="articles")


@app.get("/ranking", response_class=HTMLResponse)
async def ranking_page():
    return render("ranking.html", active_menu="ranking")


async def _fetch_ranking(sort_key: str) -> JSONResponse | dict:
    token = get_token()
    if not token:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "QIITA_TOKEN が設定されていません。.env を確認してください。"},
        )
    try:
        articles = await asyncio.to_thread(fetch_all_articles, token)
        sorted_articles = sorted(articles, key=lambda a: a[sort_key], reverse=True)
        counts = [a[sort_key] for a in articles]
        ranking = [
            {
                "rank": i + 1,
                "title": a["title"],
                "url": a["url"],
                "created_at": a["created_at"],
                "count": a[sort_key],
            }
            for i, a in enumerate(sorted_articles)
        ]
        return {
            "status": "ok",
            "total": len(articles),
            "summary": {
                "total_count": sum(counts),
                "avg_count": round(sum(counts) / len(counts), 1) if counts else 0,
                "max_count": max(counts) if counts else 0,
            },
            "ranking": ranking,
        }
    except QiitaAPIError as e:
        return JSONResponse(status_code=401, content={"status": "error", "message": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"予期しないエラー: {e}"})


@app.get("/api/ranking/likes")
async def api_ranking_likes():
    return await _fetch_ranking("likes_count")


@app.get("/api/ranking/stocks")
async def api_ranking_stocks():
    return await _fetch_ranking("stocks_count")


@app.get("/monthly", response_class=HTMLResponse)
async def monthly_page():
    return render("monthly.html", active_menu="monthly")


@app.get("/api/monthly")
async def api_monthly():
    token = get_token()
    if not token:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "QIITA_TOKEN が設定されていません。.env を確認してください。"},
        )
    try:
        articles = await asyncio.to_thread(fetch_all_articles, token)
        monthly: dict[str, int] = {}
        for a in articles:
            month = a["created_at"][:7]
            monthly[month] = monthly.get(month, 0) + 1
        sorted_months = sorted(monthly.items())
        return {
            "status": "ok",
            "total": len(articles),
            "monthly": [{"month": m, "count": c} for m, c in sorted_months],
        }
    except QiitaAPIError as e:
        return JSONResponse(status_code=401, content={"status": "error", "message": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"予期しないエラー: {e}"})


@app.get("/api/articles")
async def api_articles():
    token = get_token()
    if not token:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "QIITA_TOKEN が設定されていません。.env を確認してください。",
            },
        )
    try:
        articles = await asyncio.to_thread(fetch_all_articles, token)
        return {"status": "ok", "count": len(articles), "articles": articles}
    except QiitaAPIError as e:
        return JSONResponse(
            status_code=401, content={"status": "error", "message": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"予期しないエラー: {e}"},
        )
