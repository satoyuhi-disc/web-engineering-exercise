from django.urls import path

from . import views

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
