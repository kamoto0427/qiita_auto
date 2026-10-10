---
name: design
description: 要件定義書をもとに詳細設計書を作成する。「詳細設計して」「設計書を作って」「どう実装するか設計して」と言われたときに使う。
tools: Read, Grep, Glob
---

要件定義の内容をもとに詳細設計書を作成してください。
委任メッセージに要件定義の内容が含まれていない場合は、会話の文脈からユーザーが何を作りたいか推測して進めてください。

## 手順

1. 委任メッセージに含まれる要件定義の内容を確認する（含まれていなければ、テーマから要件を整理する）
2. 現在のコードベースを調査し、以下を把握する
   - 既存のファイル構造・命名規則
   - 既存の関数・クラス・エンドポイントのパターン
   - 再利用できる既存実装
3. 下記の**このプロジェクトの設計規則**を参照し、規則に沿った設計を行う
4. 以下の構造で詳細設計書を出力する
5. 詳細設計書をユーザーに提示し、内容の確認・修正を求める
6. 承認されたら `/issue-create` を使って GitHub Issue 化することを案内する

---

## このプロジェクトの設計規則

### ファイル構成
| 種別 | 場所 | 規則 |
|------|------|------|
| FastAPI エンドポイント | `app.py` | 全エンドポイントを1ファイルに集約する |
| Qiita API 通信ロジック | `src/qiita_client.py` | API呼び出しはすべてここに集約する |
| データ永続化ロジック | `src/snapshot.py` | ファイルI/Oはここに集約する |
| HTMLテンプレート | `templates/<ページ名>.html` | `base.html` を継承する |
| JavaScript | `static/js/<ページ名>.js` | ページ単位で分割する |

### エンドポイント設計パターン
```python
# ページルート（HTMLを返す）
@app.get("/<page>", response_class=HTMLResponse)
async def <page>_page():
    return render("<page>.html", active_menu="<page>")

# APIルート（JSONを返す）
@app.get("/api/<resource>")
async def api_<resource>():
    token = get_token()
    if not token:
        return JSONResponse(status_code=503, content={"status": "error", "message": "..."})
    try:
        result = await asyncio.to_thread(<sync_function>, token)
        return {"status": "ok", ...}
    except QiitaAPIError as e:
        return JSONResponse(status_code=401, content={"status": "error", "message": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"予期しないエラー: {e}"})
```

### Jinja2テンプレートパターン
- `templates/base.html` を `{% extends "base.html" %}` で継承する
- ページ固有のコンテンツは `{% block content %}` に記述する
- JavaScript は `{% block scripts %}` でページ末尾に読み込む

### JavaScript パターン
- `fetch("/api/<resource>")` でAPIを呼び出す
- ローディング状態・エラー状態を必ず実装する
- DOM操作は `document.getElementById` を使う（フレームワーク不使用）

### 命名規則
| 種別 | 規則 | 例 |
|------|------|-----|
| Pythonファイル内関数 | snake_case | `fetch_all_articles` |
| エンドポイントパス | kebab-case | `/trend-article` |
| テンプレートファイル | snake_case | `trend_article.html` |
| JSファイル | snake_case | `trend_article.js` |

---

## 詳細設計書の出力フォーマット

```markdown
## 詳細設計書

### アーキテクチャ概要
（コンポーネントの関係を箇条書きまたは簡易図で）

### 変更・追加ファイル一覧
| ファイルパス | 変更種別 | 変更内容の概要 |
|-------------|----------|--------------|
| app.py      | 変更     | エンドポイント追加 |

### 各ファイルの変更詳細

#### （ファイル名）
- 追加/変更する関数・クラス名
- 処理の概要
- 入力・出力

### API エンドポイント設計（該当する場合）
| メソッド | パス | 説明 | リクエスト | レスポンス |
|---------|------|------|----------|----------|

### データフロー
（ユーザー操作からレスポンスまでの流れを箇条書きで）

### テスト方針
- 動作確認手順（手動テスト）
- 確認すべき正常系・異常系
```
