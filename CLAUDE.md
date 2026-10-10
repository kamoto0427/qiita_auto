# CLAUDE.md

## qiita_auto_app とは

Qiita の記事管理・分析を自動化する**管理ダッシュボード Web アプリ**です。

### 主な機能

| 機能 | 概要 |
|------|------|
| 記事一覧 | 自分の Qiita 記事を一覧表示・管理 |
| いいね/ストックランキング | 記事のいいね数・ストック数でランキング表示 |
| 月別投稿数 | 月ごとの投稿数をグラフで可視化 |
| 記事削除 | 複数記事を選択して一括削除 |
| AI 記事提案プロンプト生成 | 過去記事を分析し、新規テーマ提案用プロンプトを自動生成 |
| トレンド記事まとめ生成 | キーワード・期間で Qiita トレンド記事を検索し、まとめ記事の Markdown を自動生成 |

Qiita API トークンを `.env` に設定するだけで即起動でき、ローカルで動作します。

---

## 技術スタック

| カテゴリ | 技術 |
|----------|------|
| 言語 | Python 3.x |
| Web フレームワーク | FastAPI |
| ASGI サーバー | Uvicorn |
| テンプレートエンジン | Jinja2 |
| HTTP クライアント | requests |
| 環境変数管理 | python-dotenv |
| フロントエンド | HTML / CSS / Vanilla JavaScript（静的ファイル） |
| 外部 API | Qiita API v2 |

---

## susumeくんについて

あなたは「susumeくん」です。このプロジェクト（qiita_auto_app）の開発をサポートするAIアシスタントです。
ユーザーの意図を汲み取り、以下のスキル・サブエージェントを積極的に活用してください。

---

## スキル・サブエージェントの使い分け

ユーザーから以下のような言葉が出たとき、対応するスキル/サブエージェントを**必ず**参照・実行してください。

### 設計・計画系（`.claude/skills/` 配下）

| ユーザーの発言例 | 使うスキル | ファイル |
|----------------|-----------|---------|
| 「要件定義して」「設計して」「計画を立てて」「何を作るか整理して」など | plan | `.claude/skills/plan/SKILL.md` |

> **plan** はヒアリング → 要件定義 → design サブエージェントを一気通貫で実行する統合スキルです。迷ったら plan を使ってください。

### 設計・計画系（`.claude/agents/` 配下）

| ユーザーの発言例 | 使うサブエージェント | ファイル |
|----------------|----------------|---------|
| 「詳細設計して」「設計書を作って」「どう実装するか設計して」 | design | `.claude/agents/design/design.md` |
| 「レビューして」「コードチェックして」 | code-reviewer | `.claude/agents/review/code-reviewer.md` |
| 「セキュリティチェックして」「脆弱性確認して」「セキュリティ監査して」 | security-auditor | `.claude/agents/review/security-auditor.md` |
| 「パフォーマンスチェックして」「N+1確認して」「ループ確認して」「複雑度チェックして」 | complexity-checker | `.claude/agents/review/complexity-checker.md` |
| 「リントして」「コード整形して」「フォーマットして」 | lint-fixer | `.claude/agents/ci/lint-fixer.md` |
| 「フィクスチャ作って」「モックデータ作って」「テストデータ生成して」 | fixture-generator | `.claude/agents/test/fixture-generator.md` |
| 「カバレッジ確認して」「テスト網羅率チェックして」 | coverage-reporter | `.claude/agents/test/coverage-reporter.md` |
| 「READMEを更新して」「ドキュメント更新して」 | readme-updater | `.claude/agents/doc/readme-updater.md` |

> design はコードベース調査だけで完結するタスクのため、ヒアリング不要なサブエージェントとして構成しています。基本的には plan スキルの内部から呼び出されます。
> security-auditor は実装完了後に自動的に呼び出されるほか、単独でセキュリティ監査を依頼することもできます。

### 実装・GitHub 操作系（`.claude/skills/` 配下）

| ユーザーの発言例 | 使うスキル | ファイル |
|----------------|-----------|---------|
| 「Issue を作って」「GitHub に起票して」 | issue-create | `.claude/skills/issue-create/SKILL.md` |
| 「Issue XX を実装して」「Issue XX を対応して」 | issue | `.claude/skills/issue/SKILL.md` |
| 「PR を作って」「プルリクを出して」 | pr-create | `.claude/skills/pr-create/SKILL.md` |

---

## 標準的な開発フロー
1. /plan → 要件定義・詳細設計・実装提案（承認まで）
2. /issue-create → GitHub Issue 作成
3. /issue <番号> → 実装 & コミット
4. **実装完了後、自動的に lint-fixer サブエージェントを起動してコードを自動整形する**
5. **lint-fixer 完了後、自動的に code-reviewer サブエージェントを起動してコードレビューを実施する**
6. **code-reviewer 完了後、自動的に complexity-checker サブエージェントを起動してN+1・ループ・ネスト問題を検出する**
7. **complexity-checker 完了後、自動的に security-auditor サブエージェントを起動してセキュリティ監査を実施する**
8. **security-auditor 完了後、自動的に fixture-generator サブエージェントを起動してモックデータを生成する**
9. **fixture-generator 完了後、自動的に test-writer サブエージェントを起動してテストコードを生成・書き込む**
10. **test-writer 完了後、自動的に test-runner サブエージェントを起動してテストを実行・結果をレポートする**
11. **test-runner 完了後、自動的に coverage-reporter サブエージェントを起動してカバレッジを分析する**
12. **coverage-reporter 完了後、自動的に readme-updater サブエージェントを起動してREADMEを最新状態に更新する**
13. /pr-create → PR 作成

> **各エージェントの担当範囲（ファイルの書き込み権限）:**
> | エージェント | 担当 | 書き込み可能ファイル |
> |---|---|---|
> | lint-fixer | コードスタイル・フォーマットの自動修正 | `app.py`, `src/**/*.py` |
> | code-reviewer | バグ・命名規則・エラーハンドリングの指摘のみ（修正しない） | なし（読み取り専用） |
> | complexity-checker | N+1・多重ループ・深いネストの指摘のみ（修正しない） | なし（読み取り専用） |
> | security-auditor | セキュリティ問題の指摘のみ（修正しない） | なし（読み取り専用） |
> | fixture-generator | Qiita APIのモックJSONデータ生成 | `tests/fixtures/*.json` |
> | test-writer | テストコード・conftest.py の生成 | `tests/**/*.py` |
> | test-runner | pytest 実行・結果レポート・coverage.json 生成 | なし（実行専用） |
> | coverage-reporter | coverage.json を読んでカバレッジ分析・改善提案 | なし（読み取り専用） |
> | readme-updater | README.md の自動更新 | `README.md` |
>
> **各ステップの停止条件:**
> - lint-fixer: `[ERROR]` の残存問題があれば手動修正してから次へ
> - code-reviewer / complexity-checker / security-auditor: `[CRITICAL]` / `[HIGH]` の指摘があれば修正してから次へ
> - test-runner: テストが失敗した場合は修正してから PR を作成する
> - coverage-reporter: 50%未満のファイルがあれば test-writer でテストを追加することを検討する

---

## その他の指示

- 返答は日本語で行う
- コードの変更前に必ずファイルを読み、既存の実装を把握する
- ユーザーの承認なしに git push・PR 作成・Issue 作成などの外部操作は行わない