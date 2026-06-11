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


def search_articles(query: str, token: str | None = None) -> list[dict]:
    """
    Qiita API でキーワードに合致する公開記事を検索・取得する。
    最大 500 件（5 ページ）まで取得する。
    返却: [{"title": ..., "url": ..., "created_at": ..., "likes_count": ..., "tags": [...]}, ...]
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    articles = []
    for page in range(1, 6):
        response = requests.get(
            "https://qiita.com/api/v2/items",
            headers=headers,
            params={"query": query, "per_page": 100, "page": page},
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
                "title": item["title"],
                "url": item["url"],
                "created_at": item["created_at"],
                "likes_count": item["likes_count"],
                "tags": [t["name"] for t in item.get("tags", [])],
            })

    return articles


def fetch_trending_articles(token: str) -> list[dict]:
    """
    Qiita API から ClaudeCode タグの当月記事をいいね数順で30件取得する。
    返却: [{"title": ..., "url": ..., "created_at": ..., "likes_count": ..., "stocks_count": ..., "user": ..., "tags": [...]}, ...]
    """
    from datetime import date

    today = date.today()
    since = today.strftime("%Y-%m-01")
    query = f"ClaudeCode created:>={since}"

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        "https://qiita.com/api/v2/items",
        headers=headers,
        params={"query": query, "per_page": 30, "sort": "likes"},
        timeout=10,
    )

    if response.status_code == 401:
        raise QiitaAPIError("トークンが無効です。Qiita のアクセストークンを確認してください。")

    if not response.ok:
        raise QiitaAPIError(f"通信エラー: {response.status_code}")

    items = response.json()
    articles = []
    for item in items:
        articles.append({
            "title": item["title"],
            "url": item["url"],
            "created_at": item["created_at"],
            "likes_count": item["likes_count"],
            "stocks_count": item["stocks_count"],
            "user": item["user"]["id"] if item.get("user") else "",
            "tags": [t["name"] for t in item.get("tags", [])],
        })

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
