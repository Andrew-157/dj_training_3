from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager


class Article(models.Model):
    title = models.CharField(max_length=255, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(null=False)
    pub_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='store/images/', null=False)
    tags = TaggableManager()

    def __str__(self):
        return self.title


class Comment(models.Model):
    commentator = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE)
    content = models.TextField(null=False)
    pub_date = models.DateTimeField(auto_now_add=True)


class Reaction(models.Model):
    """ 
    if value == 1, this means user liked an article;
    if value == -1, this means user disliked an article;
    """
    value = models.SmallIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class ArticleReading(models.Model):
    """
    Model for tracking how many times an article was read
    """
    times_read = models.PositiveBigIntegerField(default=0)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-times_read']


class Channel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
