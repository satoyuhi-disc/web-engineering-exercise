# Blog Post Creation Website

Web Engineering 課題用の Django プロジェクト。ユーザーがブログ投稿を
作成・閲覧できる、シンプルな共有ブログサイト。

## 目次

- [プロジェクト概要](#プロジェクト概要)
- [環境構築](#環境構築)
- [開発ツール](#開発ツール)
- [プロジェクト構成](#プロジェクト構成)
- [API / URL 一覧](#api--url-一覧)
- [デプロイ](#デプロイ)

## プロジェクト概要

詳細な仕様は [`openspec/project.md`](openspec/project.md) を参照。

主な機能:

- 全投稿の一覧表示(新しい順・ページネーション付き)
- 投稿者一覧 → 投稿者ごとの投稿一覧
- 日付での絞り込み表示
- タイトル部分一致検索
- ユーザー登録・ログイン
- ログイン済みユーザーによる投稿作成
- 検索/絞り込み結果はHTMXで部分更新(ページ全体をリロードしない)

## 環境構築

### 必要なもの

- Python 3.12
- [uv](https://docs.astral.sh/uv/)(Pythonパッケージ/仮想環境マネージャ)

### セットアップ

```bash
git clone https://github.com/satoyuhi-disc/web-engineering-exercise.git
cd web-engineering-exercise

# 依存関係のインストール(本番+開発用)+ 仮想環境作成
uv sync --dev

# 環境変数ファイルを用意
cp .env.example .env

# DBマイグレーション
uv run python manage.py migrate

# 管理者アカウント作成(任意)
uv run python manage.py createsuperuser

# 開発サーバー起動
uv run python manage.py runserver
```

`http://127.0.0.1:8000/` にアクセス。

## 開発ツール

| 用途 | ツール | コマンド |
|---|---|---|
| パッケージ/venv管理 | uv | `uv sync --dev` |
| フォーマット | black | `uv run black .` |
| Lint | ruff | `uv run ruff check .` |
| テスト | pytest / pytest-django | `uv run pytest` |
| カバレッジ | coverage.py | `uv run coverage run -m pytest && uv run coverage report -m` |

設定は `pyproject.toml` の `[tool.ruff]` / `[tool.black]` /
`[tool.pytest.ini_options]` / `[tool.coverage.*]` に記載。

## プロジェクト構成

```
blogsite/           Djangoプロジェクト設定(settings, urls, wsgi/asgi)
blog/                アプリ本体
  models.py          データモデル(Post)
  views.py           ビュー関数
  forms.py           フォーム(投稿作成, 登録, 検索)
  admin.py           管理画面設定
  urls.py            アプリのURL設定
  templates/blog/    アプリ固有テンプレート
  tests/             ユニットテスト
templates/           共通テンプレート(base.html, ログイン/登録画面)
static/css/          スタイルシート
openspec/            機能設計・変更管理(OpenSpec)
AGENTS.md            コーディングエージェント向けルール
```

## API / URL 一覧

| メソッド | パス | 説明 | ログイン |
|---|---|---|---|
| GET | `/` | 投稿一覧(検索 `?q=`, 日付 `?date=YYYY-MM-DD`, ページ `?page=`) | 不要 |
| GET | `/posts/partial/` | 投稿一覧の部分更新用フラグメント(HTMX) | 不要 |
| GET | `/posts/<int:pk>/` | 投稿詳細 | 不要 |
| GET/POST | `/posts/new/` | 投稿作成フォーム(POSTで保存) | 必要 |
| GET | `/authors/` | 投稿者一覧 | 不要 |
| GET | `/authors/<str:username>/` | 特定投稿者の投稿一覧(ページ `?page=`) | 不要 |
| GET/POST | `/signup/` | ユーザー登録 | 不要 |
| GET/POST | `/accounts/login/` | ログイン(Django標準) | 不要 |
| POST | `/accounts/logout/` | ログアウト(Django標準) | 必要 |
| — | `/admin/` | Django管理画面 | スーパーユーザー |

## デプロイ

本番向け構成:

- アプリケーションサーバー: `gunicorn`(`Procfile` 参照)
- 静的ファイル: `whitenoise`(`CompressedManifestStaticFilesStorage`)
- データベース: `DATABASE_URL` 環境変数で切替(未設定時はSQLite、
  本番ではPostgresを想定)

### render.com へのデプロイ手順(例)

1. GitHubリポジトリをrender.comに連携
2. "Web Service" を作成し、リポジトリを選択
3. Build Command: `uv sync --no-dev` (または `pip install -r requirements.txt`)
4. Start Command: `gunicorn blogsite.wsgi`
5. 環境変数を設定:
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=<your-app>.onrender.com`
   - `DATABASE_URL`(RenderのPostgresを追加した場合、自動で注入される)
6. デプロイ後、`python manage.py collectstatic --noinput` と
   `python manage.py migrate` を実行(release phaseまたはShellから)

## CI

`.github/workflows/ci.yml` により、`main` への push / PR ごとに
ruff・black --check・pytest(coverage付き)を自動実行する。

## 開発ワークフロー

- Issueでバックログ管理 → `feature/<name>` ブランチで開発
- 機能設計は OpenSpec(`openspec/changes/`)で proposal を作成してから実装
- コーディングエージェントのルールは [`AGENTS.md`](AGENTS.md) を参照

## Live demo
https://web-engineering-exercise.onrender.com
