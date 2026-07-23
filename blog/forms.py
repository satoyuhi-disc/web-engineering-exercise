from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Post


class SignUpForm(UserCreationForm):
    """Registration form for a new author (unique username + password)."""

    class Meta:
        model = User
        fields = ["username"]


class PostForm(forms.ModelForm):
    """Form used to create or edit a blog post."""

    class Meta:
        model = Post
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Post title"}),
            "content": forms.Textarea(attrs={"rows": 10}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty.")
        return title


class SearchForm(forms.Form):
    """GET-based search box for filtering post titles."""

    q = forms.CharField(
        label="Search",
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Search posts..."}),
    )
