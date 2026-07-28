# Project: Blog Post Creation Website

## 概要

ユーザーがブログ投稿を作成・閲覧できる共有ブログ空間を提供するWebアプリ
ケーション。シンプルなCMSとして、投稿者ごと・日付ごとの絞り込み表示を
サポートする。

## 主なユーザー操作

未登録・登録ユーザー共通:

- 全ブログ投稿を日付順(新しい順)で一覧表示
- 投稿者一覧を表示し、選択した投稿者の投稿一覧を表示
- カレンダーで日付を選択し、その日の投稿を表示
- (任意)タイトルの部分一致検索

認証済みユーザーのみ:

- ユーザー登録(一意のユーザー名+パスワード)
- ログインして投稿を作成・公開

## データモデル

- **User(Author)**: `django.contrib.auth.models.User` を使用
  (ユーザー名, パスワードのハッシュ)
- **Post**: `title`, `content`, `created_at`, `author`(FK→User)

## インターフェース方針

- 投稿者名はハイパーリンク(その投稿者の投稿一覧へ遷移)
- 日付フィルタ用のカレンダーUI/日付ピッカー
- ページネーション(1ページあたり最大 `POSTS_PER_PAGE` 件、Next/Previous
  リンク)
- 検索・日付絞り込みの再描画はHTMXで部分更新(Ex.10)

## 技術スタック

- Django 6.x / Python 3.12 / uv
- django-htmx(部分ページ更新)
- whitenoise(静的ファイル配信)+ gunicorn(本番サーバー)
- テスト: pytest + pytest-django、カバレッジ計測: coverage.py
- Lint/format: ruff / black

## 変更の進め方(OpenSpec)

新機能や大きな変更は、まず `openspec/changes/<change-id>/` に
proposal(何を・なぜ変えるか)を作成してからコードに着手する。
完了したら `/opsx-archive` でアーカイブする。

## 状態管理の設計方針(Ex.7)

- **DB**: 恒久データのみ(`User`, `Post`)。
- **URLクエリパラメータ**: 一覧のフィルタ状態(検索キーワード`q`、日付`date`)。
  セッションではなくGETパラメータに持たせることで、URLの共有・
  ブラウザの戻る/進むがそのまま機能する。
- **Django標準の session / messages**: ログイン状態(`django.contrib.sessions`)
  とフラッシュ通知(`django.contrib.messages`)はDjango標準機構に委譲し、
  独自のセッション設計は行わない。
- 現時点の規模では、上記3層で状態管理は完結しており、
  アプリ独自のセッションデータ(下書き保存など)は導入していない。

## テンプレート構造の設計方針(Ex.7)

- `templates/base.html`: 共通レイアウト(ナビゲーション、`<head>`、CSS読込)。
  全ページテンプレートがこれを `{% extends %}` する。
- `templates/registration/`: ログイン・サインアップページ(`base.html`継承)。
- `blog/templates/blog/`: 一覧・詳細・投稿フォーム・投稿者一覧など
  (いずれも`base.html`継承)。
- `_post_list_fragment.html`: アンダースコア始まりの部分テンプレート。
  `base.html`を継承せず、通常表示では`{% include %}`で埋め込み、
  HTMXリクエスト時はこの断片単体を返す(Ex.10のHTMX部分更新の基盤)。
