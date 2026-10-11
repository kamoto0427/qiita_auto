"""
app.py の全エンドポイントに対する仕様ベーステスト。
Qiita API 呼び出しはすべて unittest.mock.patch でモック化する。
"""

import json as json_module
import pytest
from unittest.mock import patch
from src.qiita_client import QiitaAPIError


# ---------------------------------------------------------------------------
# ページ系エンドポイント（HTML レスポンス）
# ---------------------------------------------------------------------------

class TestPageEndpoints:
    """HTML ページを返すエンドポイントが 200 を返すことを確認する"""

    def test_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_articles_page_returns_200(self, client):
        response = client.get("/articles")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_performance_page_returns_200(self, client):
        response = client.get("/performance")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_ranking_page_returns_200(self, client):
        response = client.get("/ranking")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_monthly_page_returns_200(self, client):
        response = client.get("/monthly")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_prompt_page_returns_200(self, client):
        response = client.get("/prompt")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_delete_page_returns_200(self, client):
        response = client.get("/delete")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_trend_article_page_returns_200(self, client):
        response = client.get("/trend-article")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


# ---------------------------------------------------------------------------
# /api/articles
# ---------------------------------------------------------------------------

class TestApiArticles:
    def test_returns_articles_list(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/articles")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "articles" in body
        assert isinstance(body["articles"], list)
        assert body["count"] == len(articles_data)

    def test_no_token_returns_503(self, client_no_token):
        response = client_no_token.get("/api/articles")
        assert response.status_code == 503
        assert response.json()["status"] == "error"

    def test_api_error_returns_401(self, client):
        with patch("app.fetch_all_articles", side_effect=QiitaAPIError("invalid token")):
            response = client.get("/api/articles")
        assert response.status_code == 401
        assert response.json()["status"] == "error"

    def test_unexpected_error_returns_500(self, client):
        with patch("app.fetch_all_articles", side_effect=RuntimeError("unexpected")):
            response = client.get("/api/articles")
        assert response.status_code == 500
        assert response.json()["status"] == "error"


# ---------------------------------------------------------------------------
# /api/ranking/likes
# ---------------------------------------------------------------------------

class TestApiRankingLikes:
    def test_returns_ranking_structure(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/ranking/likes")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "ranking" in body
        assert "summary" in body
        assert isinstance(body["ranking"], list)

    def test_ranking_items_have_required_fields(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/ranking/likes")
        body = response.json()
        for item in body["ranking"]:
            assert "rank" in item
            assert "title" in item
            assert "url" in item
            assert "count" in item
            assert "created_at" in item

    def test_summary_has_required_fields(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/ranking/likes")
        summary = response.json()["summary"]
        assert "total_count" in summary
        assert "avg_count" in summary
        assert "max_count" in summary

    def test_total_matches_article_count(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/ranking/likes")
        assert response.json()["total"] == len(articles_data)

    def test_no_token_returns_503(self, client_no_token):
        response = client_no_token.get("/api/ranking/likes")
        assert response.status_code == 503

    def test_api_error_returns_401(self, client):
        with patch("app.fetch_all_articles", side_effect=QiitaAPIError("invalid")):
            response = client.get("/api/ranking/likes")
        assert response.status_code == 401

    def test_unexpected_error_returns_500(self, client):
        with patch("app.fetch_all_articles", side_effect=RuntimeError("oops")):
            response = client.get("/api/ranking/likes")
        assert response.status_code == 500


# ---------------------------------------------------------------------------
# /api/ranking/stocks
# ---------------------------------------------------------------------------

class TestApiRankingStocks:
    def test_returns_ranking_structure(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/ranking/stocks")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "ranking" in body

    def test_ranking_items_have_required_fields(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/ranking/stocks")
        for item in response.json()["ranking"]:
            assert "rank" in item
            assert "title" in item
            assert "count" in item

    def test_no_token_returns_503(self, client_no_token):
        response = client_no_token.get("/api/ranking/stocks")
        assert response.status_code == 503

    def test_api_error_returns_401(self, client):
        with patch("app.fetch_all_articles", side_effect=QiitaAPIError("invalid")):
            response = client.get("/api/ranking/stocks")
        assert response.status_code == 401

    def test_unexpected_error_returns_500(self, client):
        with patch("app.fetch_all_articles", side_effect=RuntimeError("oops")):
            response = client.get("/api/ranking/stocks")
        assert response.status_code == 500


# ---------------------------------------------------------------------------
# /api/monthly
# ---------------------------------------------------------------------------

class TestApiMonthly:
    def test_returns_monthly_structure(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/monthly")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "monthly" in body
        assert isinstance(body["monthly"], list)

    def test_monthly_items_have_month_and_count(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/monthly")
        for item in response.json()["monthly"]:
            assert "month" in item
            assert "count" in item

    def test_monthly_total_matches_article_count(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/monthly")
        body = response.json()
        assert body["total"] == len(articles_data)

    def test_no_token_returns_503(self, client_no_token):
        response = client_no_token.get("/api/monthly")
        assert response.status_code == 503

    def test_api_error_returns_401(self, client):
        with patch("app.fetch_all_articles", side_effect=QiitaAPIError("invalid")):
            response = client.get("/api/monthly")
        assert response.status_code == 401

    def test_unexpected_error_returns_500(self, client):
        with patch("app.fetch_all_articles", side_effect=RuntimeError("oops")):
            response = client.get("/api/monthly")
        assert response.status_code == 500


# ---------------------------------------------------------------------------
# /api/prompt
# ---------------------------------------------------------------------------

class TestApiPrompt:
    def test_returns_prompt_string(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/prompt")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "prompt" in body
        assert isinstance(body["prompt"], str)
        assert len(body["prompt"]) > 0

    def test_no_token_returns_503(self, client_no_token):
        response = client_no_token.get("/api/prompt")
        assert response.status_code == 503

    def test_api_error_returns_401(self, client):
        with patch("app.fetch_all_articles", side_effect=QiitaAPIError("invalid")):
            response = client.get("/api/prompt")
        assert response.status_code == 401

    def test_unexpected_error_returns_500(self, client):
        with patch("app.fetch_all_articles", side_effect=RuntimeError("oops")):
            response = client.get("/api/prompt")
        assert response.status_code == 500


# ---------------------------------------------------------------------------
# /api/delete
# ---------------------------------------------------------------------------

class TestApiDelete:
    def test_delete_single_article_returns_ok(self, client):
        with patch("app.delete_article", return_value=None):
            response = client.post("/api/delete", json={"item_ids": ["abc1234567890abc0001"]})
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["deleted_count"] == 1
        assert "abc1234567890abc0001" in body["deleted"]

    def test_delete_multiple_articles(self, client):
        with patch("app.delete_article", return_value=None):
            response = client.post(
                "/api/delete",
                json={"item_ids": ["abc1234567890abc0001", "abc1234567890abc0002"]},
            )
        body = response.json()
        assert body["status"] == "ok"
        assert body["deleted_count"] == 2

    def test_empty_item_ids_returns_400(self, client):
        response = client.post("/api/delete", json={"item_ids": []})
        assert response.status_code == 400
        assert response.json()["status"] == "error"

    def test_no_token_returns_503(self, client_no_token):
        response = client_no_token.post("/api/delete", json={"item_ids": ["some_id"]})
        assert response.status_code == 503

    def test_api_error_is_collected_in_errors(self, client):
        with patch("app.delete_article", side_effect=QiitaAPIError("forbidden")):
            response = client.post("/api/delete", json={"item_ids": ["abc1234567890abc0001"]})
        body = response.json()
        assert body["status"] == "ok"
        assert body["deleted_count"] == 0
        assert len(body["errors"]) == 1

    def test_partial_failure_returns_partial_result(self, client):
        def side_effect(token, item_id):
            if item_id == "abc1234567890abc0002":
                raise QiitaAPIError("not found")

        with patch("app.delete_article", side_effect=side_effect):
            response = client.post(
                "/api/delete",
                json={"item_ids": ["abc1234567890abc0001", "abc1234567890abc0002"]},
            )
        body = response.json()
        assert body["deleted_count"] == 1
        assert len(body["errors"]) == 1

    def test_response_contains_errors_field(self, client):
        with patch("app.delete_article", return_value=None):
            response = client.post("/api/delete", json={"item_ids": ["abc1234567890abc0001"]})
        assert "errors" in response.json()


# ---------------------------------------------------------------------------
# /api/trend-article
# ---------------------------------------------------------------------------

class TestApiTrendArticle:
    def test_returns_markdown(self, client, trend_articles_data):
        with patch("app.fetch_trend_articles", return_value=trend_articles_data):
            response = client.post(
                "/api/trend-article",
                json={"query": "AI", "min_likes": 0, "min_stocks": 0},
            )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "markdown" in body
        assert isinstance(body["markdown"], str)

    def test_returns_total_fetched_and_filtered(self, client, trend_articles_data):
        with patch("app.fetch_trend_articles", return_value=trend_articles_data):
            response = client.post(
                "/api/trend-article",
                json={"query": "AI", "min_likes": 0, "min_stocks": 0},
            )
        body = response.json()
        assert "total_fetched" in body
        assert "total_filtered" in body
        assert body["total_fetched"] == len(trend_articles_data)

    def test_min_likes_filter_reduces_results(self, client, trend_articles_data):
        with patch("app.fetch_trend_articles", return_value=trend_articles_data):
            response_low = client.post(
                "/api/trend-article",
                json={"query": "AI", "min_likes": 0, "min_stocks": 0},
            )
        with patch("app.fetch_trend_articles", return_value=trend_articles_data):
            response_high = client.post(
                "/api/trend-article",
                json={"query": "AI", "min_likes": 999, "min_stocks": 0},
            )
        assert response_high.json()["total_filtered"] <= response_low.json()["total_filtered"]

    def test_empty_query_returns_400(self, client):
        response = client.post("/api/trend-article", json={"query": "   "})
        assert response.status_code == 400
        assert response.json()["status"] == "error"

    def test_no_token_returns_503(self, client_no_token):
        response = client_no_token.post("/api/trend-article", json={"query": "Python"})
        assert response.status_code == 503

    def test_api_error_returns_401(self, client):
        with patch("app.fetch_trend_articles", side_effect=QiitaAPIError("invalid")):
            response = client.post("/api/trend-article", json={"query": "Python"})
        assert response.status_code == 401

    def test_unexpected_error_returns_500(self, client):
        with patch("app.fetch_trend_articles", side_effect=RuntimeError("oops")):
            response = client.post("/api/trend-article", json={"query": "Python"})
        assert response.status_code == 500

    def test_no_matching_articles_returns_markdown_with_message(self, client):
        with patch("app.fetch_trend_articles", return_value=[]):
            response = client.post(
                "/api/trend-article",
                json={"query": "nonexistent_keyword", "min_likes": 0, "min_stocks": 0},
            )
        body = response.json()
        assert body["status"] == "ok"
        assert "該当記事なし" in body["markdown"]

    def test_with_date_range(self, client, trend_articles_data):
        with patch("app.fetch_trend_articles", return_value=trend_articles_data):
            response = client.post(
                "/api/trend-article",
                json={
                    "query": "AI",
                    "date_from": "2024-01-01",
                    "date_to": "2024-12-31",
                    "min_likes": 0,
                    "min_stocks": 0,
                },
            )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# /api/snapshot/diff
# ---------------------------------------------------------------------------

class TestApiSnapshotDiff:
    def test_no_snapshot_returns_snapshot_exists_false(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/snapshot/diff")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["snapshot_exists"] is False
        assert body["diffs"] == []

    def test_no_snapshot_saved_at_is_none(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/snapshot/diff")
        assert response.json()["saved_at"] is None

    def test_with_snapshot_returns_diffs(self, client, articles_data, monkeypatch, tmp_path):
        import src.snapshot as snapshot_module

        snapshot_path = tmp_path / "snapshot.json"
        snapshot_data = {
            "saved_at": "2024-01-01T00:00:00+09:00",
            "articles": {
                a["id"]: {
                    "title": a["title"],
                    "likes_count": a["likes_count"],
                    "stocks_count": a["stocks_count"],
                }
                for a in articles_data
            },
        }
        snapshot_path.write_text(
            json_module.dumps(snapshot_data, ensure_ascii=False), encoding="utf-8"
        )
        monkeypatch.setattr(snapshot_module, "SNAPSHOT_PATH", snapshot_path)

        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/snapshot/diff")

        body = response.json()
        assert body["status"] == "ok"
        assert body["snapshot_exists"] is True
        assert isinstance(body["diffs"], list)
        assert len(body["diffs"]) == len(articles_data)

    def test_diffs_have_required_fields(self, client, articles_data, monkeypatch, tmp_path):
        import src.snapshot as snapshot_module

        snapshot_path = tmp_path / "snapshot.json"
        snapshot_data = {
            "saved_at": "2024-01-01T00:00:00+09:00",
            "articles": {
                a["id"]: {
                    "title": a["title"],
                    "likes_count": a["likes_count"],
                    "stocks_count": a["stocks_count"],
                }
                for a in articles_data
            },
        }
        snapshot_path.write_text(
            json_module.dumps(snapshot_data, ensure_ascii=False), encoding="utf-8"
        )
        monkeypatch.setattr(snapshot_module, "SNAPSHOT_PATH", snapshot_path)

        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.get("/api/snapshot/diff")

        for diff in response.json()["diffs"]:
            assert "id" in diff
            assert "title" in diff
            assert "likes_count" in diff
            assert "stocks_count" in diff

    def test_no_token_returns_503(self, client_no_token):
        response = client_no_token.get("/api/snapshot/diff")
        assert response.status_code == 503

    def test_api_error_returns_401(self, client):
        with patch("app.fetch_all_articles", side_effect=QiitaAPIError("invalid")):
            response = client.get("/api/snapshot/diff")
        assert response.status_code == 401

    def test_unexpected_error_returns_500(self, client):
        with patch("app.fetch_all_articles", side_effect=RuntimeError("oops")):
            response = client.get("/api/snapshot/diff")
        assert response.status_code == 500


# ---------------------------------------------------------------------------
# /api/snapshot/save
# ---------------------------------------------------------------------------

class TestApiSnapshotSave:
    def test_save_returns_ok_with_count(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.post("/api/snapshot/save")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["count"] == len(articles_data)
        assert body["snapshot_exists"] is True
        assert "saved_at" in body

    def test_save_returns_diffs_list(self, client, articles_data):
        with patch("app.fetch_all_articles", return_value=articles_data):
            response = client.post("/api/snapshot/save")
        body = response.json()
        assert "diffs" in body
        assert isinstance(body["diffs"], list)

    def test_save_persists_snapshot(self, client, articles_data, monkeypatch, tmp_path):
        import src.snapshot as snapshot_module

        snapshot_path = tmp_path / "snapshot.json"
        monkeypatch.setattr(snapshot_module, "SNAPSHOT_PATH", snapshot_path)

        with patch("app.fetch_all_articles", return_value=articles_data):
            client.post("/api/snapshot/save")

        assert snapshot_path.exists()

    def test_no_token_returns_503(self, client_no_token):
        response = client_no_token.post("/api/snapshot/save")
        assert response.status_code == 503

    def test_api_error_returns_401(self, client):
        with patch("app.fetch_all_articles", side_effect=QiitaAPIError("invalid")):
            response = client.post("/api/snapshot/save")
        assert response.status_code == 401

    def test_unexpected_error_returns_500(self, client):
        with patch("app.fetch_all_articles", side_effect=RuntimeError("oops")):
            response = client.post("/api/snapshot/save")
        assert response.status_code == 500
