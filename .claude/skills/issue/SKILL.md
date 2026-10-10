---
name: issue
description: issue番号 $ARGUMENTS のissueを読み取り、実装してコミットする。PRの作成は行わない。
---

## 手順
1. GitHub MCPを使い、リポジトリ kamoto0427/qiita_auto の Issue $ARGUMENTS を取得する
2. Issueのタイトル・本文・ラベルを確認して要件を把握する
3. 現在のブランチを確認し、`feature/issue-$ARGUMENTS` ブランチを作成して切り替える
4. 要件に基づいてコードを実装する
5. 実装内容をユーザーに報告し、承認を得る
6. 承認されたら以下の順でサブエージェントを自動起動する：
   - **lint-fixer** → コードを自動整形する
   - **code-reviewer** → バグ・命名規則・エラーハンドリングをレビューする
   - **complexity-checker** → N+1・ループ・ネスト問題を検出する
   - **security-auditor** → セキュリティ問題を監査する
   - 各エージェントで `[CRITICAL]` / `[HIGH]` の指摘があれば修正してから次に進む
7. `git add`（変更ファイルを個別に指定）→ `git commit`（日本語メッセージ、Issue番号を含める）
8. コミット完了後、ユーザーに以下を案内する：
   ```
   実装・コミットが完了しました。
   次のステップ：
     - テストを追加する場合は fixture-generator → test-writer → test-runner → coverage-reporter を実行してください
     - PRを作成する場合は /pr-create を実行してください
   ```

## 注意
- `git push` および PR の作成はこのスキルでは行わない
- `.env` などの機密ファイルを `git add` しないこと
