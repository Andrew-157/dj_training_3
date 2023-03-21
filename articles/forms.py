from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Article, Comment


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PublishArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        exclude = ['author', 'pub_date']


class LeaveCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['commentator', 'article', 'pub_date']


class SearchForm(forms.Form):
    search_string = forms.CharField(max_length=255)
