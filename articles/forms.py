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

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(NewArticleForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Article
        exclude = ['author', 'pub_date']

    def save(self):
        topic = self.cleaned_data['topic']
        content = self.cleaned_data['content']
        author = self.user
        article = Article(topic=topic, content=content, author=author)
        article.save()
