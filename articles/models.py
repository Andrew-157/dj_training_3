from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    topic = models.CharField(max_length=255, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(null=False)
    pub_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    commentator = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE)
    content = models.TextField(null=False)
    pub_date = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    like = models.BooleanField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class Dislike(models.Model):
    dislike = models.BooleanField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
