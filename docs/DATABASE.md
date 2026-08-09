# データベース詳細解説 / Database Deep Dive

「データベースについて何を聞かれても答えられる」ためのドキュメント。

## 1. 使っているデータベースの種類

| 環境 | DB | 理由 |
|---|---|---|
| ローカル開発 | SQLite | インストール不要、ファイル1つで完結。個人の開発環境を汚さず、すぐ`migrate`できる手軽さが開発初期に向いている |
| 本番(render.com) | PostgreSQL | 本格的なリレーショナルDB。同時アクセス・排他制御・拡張性がSQLiteより本番向き。Renderが無料枠でホスティングを提供している |

**なぜ両方使い分けるのか**: SQLiteは「1ファイル」なので手軽だが、複数プロセスからの同時書き込みに弱く、本番の複数リクエスト同時処理には向かない。逆にPostgresはセットアップが要るので、ローカル開発でわざわざ立てるのは面倒。そこでDjangoの`DATABASES`設定を環境変数で切り替え、それぞれの得意な場面で使い分けている。

## 2. どこで切り替えているか(`blogsite/settings.py`)

```python
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}
```

- `dj_database_url`というライブラリが、環境変数`DATABASE_URL`の
  文字列(例: `postgresql://user:pass@host/dbname`)を解析して、
  Djangoが理解できる設定形式に変換してくれる。
- 環境変数`DATABASE_URL`が**無ければ**、`default=`に指定した
  SQLite(`db.sqlite3`)が使われる ―― これがローカル開発時の動作。
- 環境変数`DATABASE_URL`が**あれば**(render.comのように)、その
  URLが指すPostgresに自動的に接続する。
- `conn_max_age=600`: データベース接続を10分間使い回す設定
  (毎リクエストで接続を張り直さない、パフォーマンス最適化)。

**コード自体は一切変更していない**、という点が重要。ローカルと
本番でPythonコードは完全に同じで、環境変数だけが違う。これは
「12 Factor App」という設計原則(設定は環境変数で外出しする)に
沿った作り方。

## 3. テーブル設計(スキーマ)

このプロジェクトのテーブルは大きく分けて2種類:

**① 自作したテーブル: `Post`(`blog/models.py`)**

| カラム名 | 型 | 説明 |
|---|---|---|
| `id` | 整数(自動採番) | 主キー。Djangoが自動で付与(明示的に書いていない) |
| `title` | 文字列(最大200文字) | 投稿タイトル |
| `content` | テキスト(長さ無制限) | 投稿本文 |
| `created_at` | 日時 | 作成日時。`auto_now_add=True`で新規作成時に自動記録、以後変更不可 |
| `updated_at` | 日時 | 更新日時。`auto_now=True`で保存のたびに自動更新 |
| `author_id` | 整数(外部キー) | `auth_user`テーブルの`id`を参照 |

**② Django標準で用意されているテーブル**(自分では設計していない)

- `auth_user`: ユーザー情報(ユーザー名、ハッシュ化されたパスワード等)
- `django_session`: ログインセッション情報
- `django_admin_log`: 管理画面での操作履歴
- `django_content_type` / `auth_permission`: 権限管理の内部テーブル

「自分で設計したのは`Post`テーブルだけで、ユーザー管理まわりは
Django標準の仕組みをそのまま使っている」と説明できればOK。

## 4. なぜこの設計にしたか(設計判断)

- **`author`を外部キーにした理由**: 1人のユーザーが複数の投稿を
  書けるようにするため(一対多の関係)。投稿ごとにユーザー名を
  文字列でコピーして持つのではなく、`auth_user`テーブルへの
  参照(ID)だけを持つことで、ユーザー名変更にも自動で追従する。
- **`on_delete=models.CASCADE`**: そのユーザーアカウントが
  削除されたら、そのユーザーが書いた投稿も一緒に削除される設定。
  (代替案として、投稿だけ残す`SET_NULL`もあるが、今回は
  「著者のいない投稿」を許可しない設計にした)
- **`related_name="posts"`**: `user.posts.all()`のように、
  ユーザーオブジェクトから「その人の投稿一覧」を直接たどれる
  ようにするための名前付け(`author_posts`ビューで使用)。
- **インデックス(`Meta.indexes`)**:
  ```python
  indexes = [
      models.Index(fields=["-created_at"]),
      models.Index(fields=["author"]),
  ]
  ```
  一覧表示は必ず日付順に並べ替える(`-created_at`)ので、その列に
  索引を張ることで並べ替えが速くなる。同様に、著者ごとの絞り込み
  (`author_posts`)も頻繁に使うため、`author`にも索引を張っている。
  データ量が少ないうちは体感差はないが、「将来投稿数が増えても
  性能が落ちにくい設計にした」という説明ができる。

## 5. マイグレーション(設計図→実体、の変換の仕組み)

Djangoでは「モデル(Pythonコード)」と「実際のDBの中身」を、
**マイグレーションファイル**という中間ファイルで繋いでいる。

```bash
uv run python manage.py makemigrations   # ①
uv run python manage.py migrate           # ②
```

- **① makemigrations**: `models.py`の内容を見て、「テーブルを
  作る」「カラムを追加する」といった変更手順を、
  `blog/migrations/0001_initial.py`のようなPythonファイルとして
  自動生成する。**まだDBには何も反映されない**。
- **② migrate**: そのマイグレーションファイルを実際に実行し、
  DBにテーブルやカラムを作る。

**なぜこの2段階なのか**: マイグレーションファイルをGitで管理する
ことで、「いつ・誰が・どんなスキーマ変更をしたか」の履歴が残る。
チーム開発や、ローカルと本番のスキーマを一致させるのに必須の仕組み。

実際にこのプロジェクトでは、`blog/migrations/0001_initial.py`が
リポジトリに含まれている(`git ls-files | grep migrations`で確認可)。
render.comへのデプロイ時も、Build Commandの中で
`uv run python manage.py migrate`を実行し、本番のPostgresに
同じスキーマを反映している。

## 6. データを読み書きしている場所(ORM)

DjangoはSQL文を直接書かず、Pythonのコードでデータベース操作を
表現できる「ORM(Object-Relational Mapping)」という仕組みを持つ。

```python
# 一覧取得(投稿者情報も一緒に、効率よく取得)
posts = Post.objects.select_related("author").all()

# 検索(タイトルの部分一致)
posts = posts.filter(title__icontains=query)

# 日付での絞り込み
posts = posts.filter(created_at__date=date_str)

# 新規作成
post = form.save(commit=False)
post.author = request.user
post.save()
```

これらは裏側で自動的にSQL文(`SELECT`, `WHERE`, `INSERT`など)に
変換されて実行される。`select_related("author")`は、投稿と
投稿者を**1回のクエリでまとめて**取得するための最適化
(これをしないと、投稿10件を表示するのに投稿者情報だけ別途10回
問い合わせる、という無駄が発生する。「N+1問題」と呼ばれる)。

## 7. データの中身を実際に見る方法

**ローカル(SQLite)**
```bash
uv run python manage.py dbshell
# SQLシェルに入る。以下のようなSQLが打てる
# SELECT * FROM blog_post;
# .quit で抜ける
```

**本番(Django管理画面、ブラウザから)**
```
https://web-engineering-exercise.onrender.com/admin/
```
(管理者アカウントでログインすると、投稿・ユーザーをGUIで見られる)

## 8. セキュリティ面(データベース関連)

- **SQLインジェクション対策**: SQL文を自分で組み立てず、常にORM
  経由でクエリを発行しているため、Djangoが自動的にパラメータを
  エスケープしてくれる。文字列連結でSQLを組み立てる書き方は
  一切していない。
- **著者のなりすまし防止**: `post.author`はフォームの入力値からは
  設定せず、`request.user`(サーバー側で検証済みのログイン中の
  ユーザー)から設定している(`views.py`の`post_create`)。
- **接続情報の管理**: 本番DBのパスワードを含む接続文字列
  (`DATABASE_URL`)はコードに直接書かず、Renderの環境変数として
  設定している。`.env.example`にはダミー値のみを記載し、実際の
  `.env`ファイルは`.gitignore`でGit管理から除外している。

## 9. よくある追加質問への回答例

**Q. データが消えることはある?**
→ 「render.comの無料PostgreSQLは一定期間(90日など)で自動的に
期限切れになる制限があります。学習用の検証環境という位置づけです」

**Q. バックアップは?**
→ 「今回は授業課題の範囲なので設定していませんが、本番運用なら
Renderの自動バックアップ機能や`pg_dump`によるエクスポートが
必要になります」

**Q. 将来テーブルを増やすなら?**
→ 「`models.py`に新しいモデルクラスを追加し、`makemigrations`→
`migrate`を実行すれば、既存データを保ったままスキーマを拡張
できます。例えばコメント機能を足すなら`Comment`モデルを追加し、
`Post`への外部キーを持たせる形になります」
