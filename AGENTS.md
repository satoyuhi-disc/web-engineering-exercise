# AGENTS.md

このファイルはコーディングエージェント(OpenCode等)がこのリポジトリで
作業する際に従うべきルールをまとめたものです。

## プロジェクト概要

- 名前: `blogsite`(Djangoプロジェクト)/ `blog`(アプリ)
- 内容: ブログ投稿共有サイト(Web Engineering課題)
- 詳細仕様: `README.md` および `openspec/project.md` を参照

## 環境

- パッケージ管理: `uv`(`pyproject.toml` / `uv.lock`)
- セットアップ: `uv sync --dev`
- 実行: `uv run python manage.py runserver`
- テスト: `uv run pytest`
- カバレッジ: `uv run coverage run -m pytest && uv run coverage report -m`
- Lint: `uv run ruff check .`
- フォーマット: `uv run black .`

## 期待される作業手順

1. 新機能に着手する前に、GitHub Issue を作成しバックログ化すること。
2. 各機能は `feature/<short-name>` ブランチで作業すること。`main` に直接
   コミットしない。
3. 機能設計には OpenSpec を使うこと(`openspec/changes/` にproposal
   を作成してからコードを書く)。
4. **新しい関数・ビューを追加/変更したら、必ず対応するユニットテストも
   同時に生成・実行すること。** テストを書かずに「完了」と報告しない。
5. コミットメッセージには、対応するIssueを自動クローズするキーワード
   (例: `Closes #12`, `Fixes #7`)を含めること。
6. 機能が完成したら:
   - リファクタリングを行う
   - Pull Request を作成する
   - コード生成に使ったモデルとは別のAIモデルでコードレビューを行う
   - レビュー内容を分析し、対応するかどうかは開発者自身が判断する
   - 満足したら `/opsx-archive` でOpenSpec変更をアーカイブし、
     `main` にマージしてfeatureブランチを削除する

## コーディング規約

- 行長: 100文字(`ruff`/`black`設定に準拠)
- Python 3.12 / Django 6.x
- ビューは `blog/views.py` に薄く保ち、ロジックが複雑になったら
  モデルメソッドやフォームの `clean_*` に寄せる
- テンプレートは `templates/`(共通)と `blog/templates/blog/`
  (アプリ固有)に分ける
- 全モデルに `__str__()` を実装すること(admin表示のため)

## やってはいけないこと

- `.env` や秘密情報をコミットしない
- `main` ブランチへの直接pushをしない
- テストが失敗した状態でPRを作らない
