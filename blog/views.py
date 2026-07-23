from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import PostForm, SearchForm, SignUpForm
from .models import Post

POSTS_PER_PAGE = 5


def _post_list_context(request):
    """Shared filtering logic for the home page and its HTMX partial."""
    posts = Post.objects.select_related("author").all()

    search_form = SearchForm(request.GET or None)
    query = ""
    if search_form.is_valid():
        query = search_form.cleaned_data.get("q", "")
        if query:
            posts = posts.filter(title__icontains=query)

    date_str = request.GET.get("date", "")
    if date_str:
        posts = posts.filter(created_at__date=date_str)

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return {
        "page_obj": page_obj,
        "search_form": search_form,
        "query": query,
        "selected_date": date_str,
    }


def post_list(request):
    """Home page: all posts, most recent first, with search/date filters."""
    context = _post_list_context(request)
    return render(request, "blog/post_list.html", context)


def post_list_partial(request):
    """HTMX endpoint: re-renders only the post list fragment (Ex.10)."""
    context = _post_list_context(request)
    return render(request, "blog/_post_list_fragment.html", context)


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related("author"), pk=pk)
    return render(request, "blog/post_detail.html", {"post": post})


def author_list(request):
    authors = User.objects.filter(posts__isnull=False).distinct().order_by("username")
    return render(request, "blog/author_list.html", {"authors": authors})


def author_posts(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    return render(request, "blog/author_posts.html", {"author": author, "page_obj": page_obj})


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("blog:post_list")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("blog:post_detail", pk=post.pk)
    else:
        form = PostForm()
    return render(request, "blog/post_form.html", {"form": form})
