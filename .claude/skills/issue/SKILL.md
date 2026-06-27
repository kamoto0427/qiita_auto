---
name: issue
description: issue番号 $ARGUMENTS のissueを読み取り、実装してPRを作成する。
---

## 手順
1. GitHub MCPを使い、リポジトリ kamoto0427/qiita_auto の Issue $ARGUMENTS を取得する
2. Issueのタイトル・本文・ラベルを確認して要件を把握する
3. 現在のブランチを確認し、`feature/issue-$ARGUMENTS` ブランチを作成して切り替える
4. 要件に基づいてコードを実装する
5. git add → git commit（日本語メッセージ、Issue番号を含める）
6. 実装内容をユーザーに報告し、承認を得る
7. 承認されたら git push し、PRを作成する（本文に `Closes #$ARGUMENTS` を含める）
