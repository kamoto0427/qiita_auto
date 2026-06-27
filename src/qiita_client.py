import requests


class QiitaAPIError(Exception):
    pass


def fetch_all_articles(token: str) -> list[dict]:
    """
    Qiita API からログインユーザーの全記事を取得する。
    ページネーションで空になるまでループし全件返す。
    返却: [{"title": ..., "url": ..., "created_at": ...}, ...]
    """
    headers = {"Authorization": f"Bearer {token}"}
    articles = []
    page = 1

    while True:
        response = requests.get(
            "https://qiita.com/api/v2/authenticated_user/items",
            headers=headers,
            params={"per_page": 100, "page": page},
            timeout=10,
        )

        if response.status_code == 401:
            raise QiitaAPIError("トークンが無効です。Qiita のアクセストークンを確認してください。")

        if not response.ok:
            raise QiitaAPIError(f"通信エラー: {response.status_code}")

        items = response.json()
        if not items:
            break

        for item in items:
            articles.append({
                "id": item["id"],
                "title": item["title"],
                "url": item["url"],
                "created_at": item["created_at"],
                "likes_count": item["likes_count"],
                "stocks_count": item["stocks_count"],
                "tags": [t["name"] for t in item.get("tags", [])],
            })

        page += 1

    return articles


def fetch_trend_articles(token: str, query: str, date_from: str = None, date_to: str = None) -> list[dict]:
    """
    Qiita API で公開記事を検索して取得する。
    query: 検索クエリ文字列 (例: "tag:ClaudeCode", "Claude Code")
    date_from: YYYY-MM (開始年月、含む)
    date_to:   YYYY-MM (終了年月、含む)
    返却: 記事情報のリスト
    """
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    articles = []
    page = 1

    search_query = query.strip()
    if date_from:
        search_query += f" created:>={date_from}-01"
    if date_to:
        year, month = map(int, date_to.split("-"))
        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1
        search_query += f" created:<{next_year:04d}-{next_month:02d}-01"

    while page <= 10:  # 最大 1000 件
        response = requests.get(
            "https://qiita.com/api/v2/items",
            headers=headers,
            params={"query": search_query, "per_page": 100, "page": page},
            timeout=15,
        )

        if response.status_code == 401:
            raise QiitaAPIError("トークンが無効です。Qiita のアクセストークンを確認してください。")

        if not response.ok:
            raise QiitaAPIError(f"通信エラー: {response.status_code}")

        items = response.json()
        if not items:
            break

        for item in items:
            articles.append({
                "id": item["id"],
                "title": item["title"],
                "url": item["url"],
                "created_at": item["created_at"],
                "likes_count": item.get("likes_count", 0),
                "stocks_count": item.get("stocks_count", 0),
                "comments_count": item.get("comments_count", 0),
                "tags": [t["name"] for t in item.get("tags", [])],
                "user": item.get("user", {}).get("id", ""),
            })

        page += 1

    return articles


def delete_article(token: str, item_id: str) -> None:
    """
    Qiita API で記事を1件削除する。
    成功時は None を返す。失敗時は QiitaAPIError を送出。
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"https://qiita.com/api/v2/items/{item_id}",
        headers=headers,
        timeout=10,
    )

    if response.status_code == 401:
        raise QiitaAPIError("トークンが無効です。Qiita のアクセストークンを確認してください。")

    if response.status_code == 403:
        raise QiitaAPIError(
            f"記事 {item_id} を削除する権限がありません。"
            " トークンに write_qiita スコープが必要です。"
        )

    if response.status_code == 404:
        raise QiitaAPIError(f"記事 {item_id} が見つかりません。")

    if not response.ok:
        try:
            detail = response.json().get("message", "")
        except Exception:
            detail = response.text[:200]
        raise QiitaAPIError(f"削除に失敗しました (HTTP {response.status_code}): {detail}")
