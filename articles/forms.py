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


class UpdateArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        exclude = ['author', 'pub_date', 'tags']

    def save(self):
        title = self.cleaned_data['title']
        content = self.cleaned_data['content']
        author = self.instance.author
        article_to_update = Article.objects.get(pk=self.instance.article)
        article_to_update.topic = title
        article_to_update.content = content
        article_to_update.author = author
        article_to_update.save()


class LeaveCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['commentator', 'article', 'pub_date']

    def save(self):
        commentator = self.instance.commentator
        article = self.instance.article
        content = self.cleaned_data['content']
        comment = Comment(commentator=commentator,
                          article=article, content=content)
        comment.save()
