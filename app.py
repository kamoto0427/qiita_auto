import os
import asyncio

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

from fastapi import Request
from src.qiita_client import fetch_all_articles, delete_article, fetch_trend_articles, QiitaAPIError

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


@app.get("/prompt", response_class=HTMLResponse)
async def prompt_page():
    return render("prompt.html", active_menu="prompt")


@app.get("/api/prompt")
async def api_prompt():
    token = get_token()
    if not token:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "QIITA_TOKEN が設定されていません。.env を確認してください。"},
        )
    try:
        articles = await asyncio.to_thread(fetch_all_articles, token)
        prompt_text = _generate_prompt(articles)
        return {"status": "ok", "prompt": prompt_text}
    except QiitaAPIError as e:
        return JSONResponse(status_code=401, content={"status": "error", "message": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"予期しないエラー: {e}"})


def _generate_prompt(articles: list[dict]) -> str:
    from collections import Counter

    total = len(articles)

    # 人気記事（いいね数上位5件）
    top_likes = sorted(articles, key=lambda a: a["likes_count"], reverse=True)[:5]

    # 頻出タグ（上位10件）
    all_tags: list[str] = []
    for a in articles:
        all_tags.extend(a.get("tags", []))
    tag_counts = Counter(all_tags).most_common(10)

    # 全タイトル一覧
    titles = [a["title"] for a in articles]

    lines = [
        "# Qiita記事分析レポート",
        "",
        f"## 基本情報",
        f"- 総記事数: {total}件",
        "",
        "## 人気記事（いいね数トップ5）",
    ]
    for i, a in enumerate(top_likes, 1):
        lines.append(f"{i}. {a['title']}（いいね: {a['likes_count']}、ストック: {a['stocks_count']}）")

    lines += [
        "",
        "## 頻出タグ（使用回数順）",
    ]
    for tag, count in tag_counts:
        lines.append(f"- {tag}: {count}回")

    lines += [
        "",
        "## 既存記事タイトル一覧",
    ]
    for t in titles:
        lines.append(f"- {t}")

    lines += [
        "",
        "---",
        "",
        "## AIへの依頼文",
        "",
        "上記の情報を参考に、以下をお願いします。",
        "",
        "1. **新しい記事テーマの提案**",
        "   - 既存記事と重複しない新しいテーマを10件提案してください。",
        "   - 人気タグやトレンドを考慮してください。",
        "",
        "2. **記事タイトルの改善案**",
        "   - いいね数が少ない記事のタイトルを、より魅力的に改善する案を提案してください。",
        "",
        "3. **未開拓テーマの発掘**",
        "   - 頻出タグと関連するが、まだ書いていないテーマを提案してください。",
    ]

    return "\n".join(lines)


@app.get("/delete", response_class=HTMLResponse)
async def delete_page():
    return render("delete.html", active_menu="delete")


class DeleteRequest(BaseModel):
    item_ids: list[str]


@app.post("/api/delete")
async def api_delete(req: DeleteRequest):
    token = get_token()
    if not token:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "QIITA_TOKEN が設定されていません。.env を確認してください。"},
        )
    if not req.item_ids:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "削除する記事が選択されていません。"},
        )
    deleted = []
    errors = []
    for item_id in req.item_ids:
        try:
            await asyncio.to_thread(delete_article, token, item_id)
            deleted.append(item_id)
        except QiitaAPIError as e:
            errors.append({"id": item_id, "message": str(e)})
        except Exception as e:
            errors.append({"id": item_id, "message": f"予期しないエラー: {e}"})
    return {
        "status": "ok",
        "deleted_count": len(deleted),
        "deleted": deleted,
        "errors": errors,
    }


@app.get("/trend-article", response_class=HTMLResponse)
async def trend_article_page():
    return render("trend_article.html", active_menu="trend_article")


class TrendArticleRequest(BaseModel):
    query: str
    date_from: str = ""
    date_to: str = ""
    min_likes: int = 10
    min_stocks: int = 10


@app.post("/api/trend-article")
async def api_trend_article(req: TrendArticleRequest):
    token = get_token()
    if not token:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "QIITA_TOKEN が設定されていません。.env を確認してください。"},
        )
    if not req.query.strip():
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "検索キーワードまたはタグを入力してください。"},
        )
    try:
        articles = await asyncio.to_thread(
            fetch_trend_articles,
            token,
            req.query,
            req.date_from or None,
            req.date_to or None,
        )
        # いいね・ストックフィルター
        filtered = [
            a for a in articles
            if a["likes_count"] >= req.min_likes and a["stocks_count"] >= req.min_stocks
        ]
        markdown = _generate_trend_markdown(filtered, req)
        return {
            "status": "ok",
            "total_fetched": len(articles),
            "total_filtered": len(filtered),
            "markdown": markdown,
        }
    except QiitaAPIError as e:
        return JSONResponse(status_code=401, content={"status": "error", "message": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"予期しないエラー: {e}"})


def _generate_trend_markdown(articles: list[dict], req: "TrendArticleRequest") -> str:
    from collections import Counter
    from datetime import datetime, timezone

    if not articles:
        return "# 該当記事なし\n\n条件に一致する記事が見つかりませんでした。"

    now = datetime.now(timezone.utc)

    # スコア = いいね + ストック
    scored = sorted(articles, key=lambda a: a["likes_count"] + a["stocks_count"], reverse=True)

    # 期間ラベル
    period_label = ""
    if req.date_from and req.date_to:
        period_label = f"{req.date_from} 〜 {req.date_to}"
    elif req.date_from:
        period_label = f"{req.date_from} 以降"
    elif req.date_to:
        period_label = f"{req.date_to} 以前"
    else:
        period_label = "全期間"

    today_str = now.strftime("%Y-%m-%d")
    query_display = req.query

    lines = [
        f"# 【{period_label}版】{query_display} 関連記事まとめ｜人気記事ランキングTOP10",
        "",
        f"{query_display} 関連の記事を人気順でまとめました。",
        "",
        "## 集計条件",
        "",
        f"* 期間：{period_label}",
        "* ソート：いいね数 + ストック数",
        f"* 対象：{query_display} に関連する記事",
        f"* 最低いいね数：{req.min_likes}以上 / 最低ストック数：{req.min_stocks}以上",
        "",
        "---",
        "",
        "## ランキング",
        "",
    ]

    top10 = scored[:10]
    for i, a in enumerate(top10):
        article_label = f"記事{i + 1}"
        tags_str = " / ".join(a["tags"]) if a["tags"] else "-"
        author_url = f"https://qiita.com/{a['user']}"
        post_date = a["created_at"][:10]
        lines += [
            f"### {article_label}",
            "",
            f"#### [{a['title']}]({a['url']})",
            "",
            "| 項目 | 内容 |",
            "| --- | --- |",
            f"| 著者 | [@{a['user']}]({author_url}) |",
            f"| 投稿日 | {post_date} |",
            f"| いいね | {a['likes_count']} |",
            f"| ストック | {a['stocks_count']} |",
            f"| コメント | {a['comments_count']} |",
            f"| タグ | {tags_str} |",
            "",
            "---",
            "",
        ]

    # タグランキング
    all_tags: list[str] = []
    for a in articles:
        all_tags.extend(a["tags"])
    tag_counts = Counter(all_tags).most_common(10)

    lines += ["## 人気タグランキング", ""]
    lines.append("| 順位 | タグ | 記事数 |")
    lines.append("| --- | --- | --- |")
    for rank, (tag, count) in enumerate(tag_counts, 1):
        lines.append(f"| {rank} | {tag} | {count} |")
    lines += ["", "---", ""]

    # 著者ランキング
    author_articles: dict[str, list] = {}
    for a in articles:
        author_articles.setdefault(a["user"], []).append(a)
    author_stats = sorted(
        [
            {
                "user": user,
                "count": len(arts),
                "total_likes": sum(a["likes_count"] for a in arts),
            }
            for user, arts in author_articles.items()
        ],
        key=lambda x: (x["total_likes"], x["count"]),
        reverse=True,
    )[:10]

    lines += ["## 人気著者ランキング", ""]
    lines.append("| 順位 | 著者 | 記事数 | 総いいね |")
    lines.append("| --- | --- | --- | --- |")
    for rank, s in enumerate(author_stats, 1):
        author_url = f"https://qiita.com/{s['user']}"
        lines.append(f"| {rank} | [@{s['user']}]({author_url}) | {s['count']} | {s['total_likes']:,} |")
    lines += ["", "---", ""]

    # 急上昇記事（エンゲージメント速度が高い記事）
    def engagement_velocity(a: dict) -> float:
        try:
            posted = datetime.fromisoformat(a["created_at"].replace("Z", "+00:00"))
            days = max((now - posted).days, 1)
            return (a["likes_count"] + a["stocks_count"]) / days
        except Exception:
            return 0.0

    rising = sorted(articles, key=engagement_velocity, reverse=True)[:5]
    lines += ["## 今週急上昇記事", ""]
    lines.append("| 記事 | いいね | ストック |")
    lines.append("| --- | --- | --- |")
    for a in rising:
        lines.append(f"| [{a['title']}]({a['url']}) | {a['likes_count']} | {a['stocks_count']} |")
    lines += ["", "---", ""]

    # データサマリー
    total_likes = sum(a["likes_count"] for a in articles)
    total_stocks = sum(a["stocks_count"] for a in articles)
    top_tag = tag_counts[0][0] if tag_counts else "-"
    top_article = scored[0]["title"] if scored else "-"
    authors_count = len(set(a["user"] for a in articles))

    lines += [
        "## データサマリー",
        "",
        f"* 対象記事数：{len(articles)}件",
        f"* 対象著者数：{authors_count}名",
        f"* 総いいね数：{total_likes:,}",
        f"* 総ストック数：{total_stocks:,}",
        f"* 最も使われたタグ：{top_tag}",
        f"* 最も人気だった記事：{top_article}",
        "",
        "---",
        "",
        f"最終更新：{today_str}",
        "",
        "---",
        "",
        "::: note info",
        "エンジニアなら読むべき本を30冊以上紹介しています。",
        "正直、私の仕事のやり方をガラッと変えた神本やSQLのチューニングに悩んだ時にめちゃくちゃ役に立ったもあります👇",
        "[→記事を読む\n](https://www.kamome-susume.com/recommended-books-for-engineers/)",
        ":::",
    ]

    return "\n".join(lines)


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
