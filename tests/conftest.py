import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def articles_data() -> list[dict]:
    """tests/fixtures/articles.json を読み込んで返す"""
    return json.loads((FIXTURES_DIR / "articles.json").read_text(encoding="utf-8"))


@pytest.fixture
def trend_articles_data() -> list[dict]:
    """tests/fixtures/trend_articles.json を読み込んで返す"""
    return json.loads((FIXTURES_DIR / "trend_articles.json").read_text(encoding="utf-8"))


@pytest.fixture
def client(monkeypatch, tmp_path):
    """
    TestClient を返す。
    - QIITA_TOKEN を差し替えてトークン未設定による 503 を防ぐ
    - src.snapshot.SNAPSHOT_PATH を tmp_path 配下に差し替えてファイル汚染を防ぐ
    """
    monkeypatch.setenv("QIITA_TOKEN", "FAKE_TOKEN_FOR_TEST_DO_NOT_USE")

    import src.snapshot as snapshot_module
    monkeypatch.setattr(snapshot_module, "SNAPSHOT_PATH", tmp_path / "snapshot.json")

    from app import app
    return TestClient(app)


@pytest.fixture
def client_no_token(monkeypatch, tmp_path):
    """QIITA_TOKEN が未設定の状態の TestClient"""
    monkeypatch.delenv("QIITA_TOKEN", raising=False)

    import src.snapshot as snapshot_module
    monkeypatch.setattr(snapshot_module, "SNAPSHOT_PATH", tmp_path / "snapshot.json")

    from app import app
    return TestClient(app)
