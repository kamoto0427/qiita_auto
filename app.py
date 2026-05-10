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
