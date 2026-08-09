# コード解説(全ファイル) / Code Walkthrough

先生に「このファイルは何?」と聞かれたとき、実際のコードを見ながら
説明できるようにするための解説書。ファイルごとに「何をしているか」
「なぜそう書いたか」をまとめている。

---

## `blog/models.py` — データの設計図

```python
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.author})"
```

**説明**:
- `Post`という1つのテーブル(データの入れ物)を定義している。
- `title`(タイトル)、`content`(本文)、`created_at`(作成日時、
  自動で記録)、`author`(投稿者、`User`への外部キー)の4項目。
- `author`は自作せず、Djangoが標準で持っている`User`モデルを
  そのまま使っている(`settings.AUTH_USER_MODEL`で参照)。
- `on_delete=models.CASCADE`: そのユーザーが削除されたら、その人の
  投稿も一緒に削除される、という設定。
- `Meta.ordering`: 何もしなくても常に新しい順に並ぶようにする設定。
- `indexes`: 日付順の並べ替えや投稿者での絞り込みが速くなるよう、
  データベースに索引(インデックス)を張っている。
- `__str__()`: 管理画面(`/admin/`)やシェルで、この投稿が
  「タイトル(投稿者名)」という読みやすい形で表示されるようにする
  ためのメソッド(Exercise 5の要件)。

---

## `blog/forms.py` — 入力フォームとバリデーション

```python
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username"]

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty.")
        return title

class SearchForm(forms.Form):
    q = forms.CharField(required=False, max_length=200)
```

**説明**:
- `SignUpForm`: ユーザー登録フォーム。Django標準の
  `UserCreationForm`を継承し、パスワードの強度チェックなどは
  Django任せにしている。
- `PostForm`: 投稿作成フォーム。`author`はここに**含めていない**
  ―― フォームの値ではなく、ビュー側でログイン中のユーザーから
  自動設定するため(なりすまし防止、`views.py`の`post_create`参照)。
- `clean_title`: タイトルが空白だけの場合を弾くカスーダする。
- `SearchForm`: 検索ボックス用。`required=False`なので、何も入力
  しなくてもエラーにならない(全件表示になる)。

---

## `blog/views.py` — 各画面の処理

```python
def _post_list_context(request):
    posts = Post.objects.select_related("author").all()
    search_form = SearchForm(request.GET or None)
    ...
    date_str = request.GET.get("date", "")
    if date_str:
        posts = posts.filter(created_at__date=date_str)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    ...

def post_list(request):
    return render(request, "blog/post_list.html", _post_list_context(request))

def post_list_partial(request):
    return render(request, "blog/_post_list_fragment.html", _post_list_context(request))
```

**説明**:
- `_post_list_context`という共通関数に、検索・日付フィルタ・
  ページネーションのロジックをまとめている(重複を避けるため)。
- `select_related("author")`: 投稿を表示するたびに投稿者情報を
  別クエリで取りに行かない(N+1問題の回避)ための最適化。
- `post_list`(通常のページ全体)と`post_list_partial`
  (HTMX用の部分だけ)が**同じロジック**を使い、テンプレートだけ
  出し分けている ―― これがEx.10のHTMX実装の核。

```python
@login_required
@require_http_methods(["GET", "POST"])
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user   # ← フォームの値ではなくログインユーザーから設定
            post.save()
```

**説明**:
- `@login_required`: ログインしていない人はログイン画面に飛ばされる。
- `post.author = request.user`: これが「なりすまし防止」の実装。
  フォームで著者名を送らせず、サーバー側でセッションを持ち主から
  設定している。

---

## `blog/urls.py` — URLと処理の対応表

```python
app_name = "blog"
urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("posts/partial/", views.post_list_partial, name="post_list_partial"),
    path("posts/<int:pk>/", views.post_detail, name="post_detail"),
    path("posts/new/", views.post_create, name="post_create"),
    path("authors/", views.author_list, name="author_list"),
    path("authors/<str:username>/", views.author_posts, name="author_posts"),
    path("signup/", views.signup, name="signup"),
]
```

**説明**: URL(例: `/posts/3/`)が来たら、どの関数(`views.py`の
どれ)を呼ぶかを決める対応表。`app_name = "blog"`により、
テンプレート内では`{% url 'blog:post_detail' post.pk %}`のように
「名前」でリンクを生成でき、URLの文字列を直書きしなくて済む。

---

## `blog/admin.py` — 管理画面の設定

```python
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at")
    list_filter = ("author", "created_at")
    search_fields = ("title", "content")
    date_hierarchy = "created_at"
```

**説明**: `/admin/`にアクセスしたときの一覧画面の見た目を設定。
`list_display`で一覧に出す列、`search_fields`で検索対象、
`date_hierarchy`で日付ドリルダウン(年→月→日)ナビが付く。

---

## `blogsite/settings.py` — プロジェクト全体の設定

**説明が必要な箇所だけ抜粋**:

```python
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
```
→ `DEBUG`はローカルでは`True`(エラー詳細を表示)、本番では環境変数
`DJANGO_DEBUG=False`で切り替える。本番でTrueのままだと、
エラー画面から内部のコードやシークレットキーが見えてしまい危険。

```python
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}
```
→ 環境変数`DATABASE_URL`が無ければSQLite、あれば(本番のRenderの
ように)そのURLの指すDB(PostgreSQL)に自動的に切り替わる。

```python
STORAGES = {
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}
```
→ 本番ではCSSファイルを圧縮し、ファイル名にハッシュを付けて
キャッシュを効かせる(`whitenoise`というライブラリ経由)。

```python
INSTALLED_APPS = [..., "django_htmx", "blog"]
MIDDLEWARE = [..., "django_htmx.middleware.HtmxMiddleware"]
```
→ HTMXからのリクエストかどうかをDjango側で判定できるようにする
ためのライブラリ`django-htmx`を組み込んでいる。

---

## テンプレート(`templates/`, `blog/templates/blog/`)

- `templates/base.html`: 全ページ共通の土台(ナビゲーション、
  `<head>`、CSS読み込み)。他のテンプレートはこれを
  `{% extends "base.html" %}`で継承する。
- `blog/templates/blog/post_list.html`: ホーム画面。検索フォームと
  日付フィルタ(`hx-get`属性でHTMXの動作を指定)を持つ。
- `blog/templates/blog/_post_list_fragment.html`: アンダースコア
  始まりの**部分テンプレート**。投稿一覧の中身だけを持ち、
  `base.html`を継承しない。通常表示では`{% include %}`で
  `post_list.html`の中に埋め込まれ、HTMX経由のリクエストが来た時は
  この断片だけが直接返される。

---

## `static/css/style.css` — スタイル

- レスポンシブ対応: `@media`クエリでスマホ幅でもレイアウトが崩れ
  ないようにしている。
- アクセシビリティ対応: フォーカス時の枠線(キーボード操作の
  可視化)、skip-link(スクリーンリーダー向けの本文への
  ショートカット)などを入れている。

---

## `blog/tests/` — テスト

`test_models.py`は`Post`モデルの`__str__()`や並び順を、
`test_views.py`は一覧表示・検索・日付フィルタ・ログイン必須の
挙動などをテストしている。合計9件、カバレッジ約89%
(`uv run coverage report -m`で確認可能)。

---

## `pyproject.toml` — 依存関係とツール設定

```toml
[project]
dependencies = ["django==6.0.*", "gunicorn", "whitenoise", "dj-database-url", ...]

[dependency-groups]
dev = ["pytest", "pytest-django", "coverage", "ruff", "black"]

[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "F", "I", "B", "DJ"]

[tool.black]
line-length = 100
```

**説明**: 本番で必要なパッケージ(`dependencies`)と、開発時だけ
必要なパッケージ(`dependency-groups.dev`、テスト・lint系)を
分けている。`uv sync --dev`は両方、`uv sync --no-dev`
(本番デプロイ時)は本番用だけをインストールする。

---

## `Procfile` — 本番の起動コマンド

```
web: gunicorn blogsite.wsgi --log-file -
```

**説明**: 本番環境でアプリを起動するコマンド。Djangoの開発用
サーバー(`manage.py runserver`)は本番では使わず、`gunicorn`
という本番向けのアプリケーションサーバーを使う。

---

## `.github/workflows/ci.yml` — 自動テスト(CI)

`main`ブランチへのpush/PRのたびに、GitHub Actions上で
`ruff check` → `black --check` → `pytest`(coverage付き)を
自動実行する。壊れたコードが`main`に混ざるのを防ぐための仕組み。

---

## `AGENTS.md` / `.opencode/skill/` / `openspec/` — AIエージェント関連

- `AGENTS.md`: コーディングエージェント(OpenCode)に守らせる
  ルール(テスト必須、ブランチ運用、コミット規約など)。
- `.opencode/skill/`: `django-expert`など5つのスキル。エージェントが
  作業する際に読み込む「ベストプラクティス集」。
- `openspec/`: 機能の仕様(`project.md`)と、変更提案の記録
  (`changes/0001-review-agentic-setup/`)。「何を」「なぜ」変えた
  かを追跡するための仕組み。
