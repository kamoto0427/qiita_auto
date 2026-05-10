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
                "title": item["title"],
                "url": item["url"],
                "created_at": item["created_at"],
            })

        page += 1

    return articles
