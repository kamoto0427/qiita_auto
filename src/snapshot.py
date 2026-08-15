import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

SNAPSHOT_PATH = Path("data/snapshot.json")

JST = timezone(timedelta(hours=9))


def load_snapshot() -> dict | None:
    try:
        return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_snapshot(articles: list[dict]) -> None:
    SNAPSHOT_PATH.parent.mkdir(exist_ok=True)
    data = {
        "saved_at": datetime.now(JST).isoformat(),
        "articles": {
            a["id"]: {
                "title": a["title"],
                "likes_count": a["likes_count"],
                "stocks_count": a["stocks_count"],
            }
            for a in articles
        },
    }
    SNAPSHOT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def calc_diff(current: list[dict], snapshot: dict) -> list[dict]:
    snap_articles = snapshot.get("articles", {})
    result = []
    for a in current:
        aid = a["id"]
        snap = snap_articles.get(aid)
        likes_diff = a["likes_count"] - snap["likes_count"] if snap else None
        stocks_diff = a["stocks_count"] - snap["stocks_count"] if snap else None
        result.append({
            "id": aid,
            "title": a["title"],
            "url": a["url"],
            "likes_count": a["likes_count"],
            "stocks_count": a["stocks_count"],
            "likes_diff": likes_diff,
            "stocks_diff": stocks_diff,
        })
    return result
