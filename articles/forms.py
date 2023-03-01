from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Article


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class NewArticleForm(forms.ModelForm):

    def __init__(self, data: dict, *args, **kwargs):
        self.user = data['user']
        if 'article' in data:
            self.article = data['article']
        else:
            self.article = None
        super(NewArticleForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Article
        exclude = ['author', 'pub_date']

    def save(self):
        if not self.article:
            topic = self.cleaned_data['topic']
            content = self.cleaned_data['content']
            author = self.user
            article = Article(topic=topic, content=content, author=author)
            article.save()
        else:
            topic = self.cleaned_data['topic']
            content = self.cleaned_data['content']
            author = self.user
            article = Article.objects.get(pk=self.article)
            article.topic = topic
            article.content = content
            article.author = author
            article.save()
