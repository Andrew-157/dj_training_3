from datetime import timedelta
from django.views import View
from django.utils import timezone
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from taggit.models import Tag
from .forms import NewUserForm, PublishArticleForm, LeaveCommentForm, SearchForm
from .models import Article, Comment, Reaction, ArticleReading, Channel, Subscription


class Register(View):
    form_class = NewUserForm
    template_name = 'articles/registration.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a channel entity while creating new users
            # this avoids excessive queries and if conditions
            # in another views when dealing with subscription
            channel = Channel(owner=user)
            channel.save()
            login(request, user)
            username = form.cleaned_data['username']
            messages.info(request, f'Welcome to the Ligma, {username}')
            return redirect('articles:index')

        return render(request, self.template_name, {'form': form})


class Login(View):
    form_class = AuthenticationForm
    template_name = 'articles/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.info(request, f"Welcome back to Ligma, {username}")
                return redirect('articles:index')
        return render(request, self.template_name, {'form': form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('articles:index')


class PublishArticle(View):
    form_class = PublishArticleForm
    template_name = 'articles/publish_article.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            form.instance.author = request.user
            obj.save()
            form.save_m2m()
            messages.info(
                request, 'You successfully published new article')
            return HttpResponseRedirect(reverse('articles:personal-page'))
        return render(request, 'articles/publish_article.html', {'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@login_required()
def update_article(request, article_id):
    current_user = request.user
    article = Article.objects.filter(id=article_id).first()
    if not article:
        return render(request, 'articles/not_exists.html')
    else:
        if article.author_id != current_user.id:
            return render(request, 'articles/not_yours.html')
        if request.method == 'POST':
            form = PublishArticleForm(
                request.POST, request.FILES, instance=article)
            if form.is_valid():
                obj = form.save(commit=False)
                form.instance.author = request.user
                obj.save()
                form.save_m2m()
                messages.info(
                    request, 'You successfully updated this article')
                return HttpResponseRedirect(reverse('articles:personal-article', args=(article_id, )))
        else:
            form = PublishArticleForm(instance=article)
            return render(request, 'articles/update_article.html', {'form': form, 'article_id': article_id})


def public_page(request):
    articles_list = Article.objects.select_related('author').\
        prefetch_related('tags').order_by('-pub_date').all()
    paginator = Paginator(articles_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'articles/public_page.html', {'page_obj': page_obj})


@login_required()
def personal_page(request):
    current_user = request.user
    articles_list = Article.objects.filter(author_id=current_user.id).\
        prefetch_related('tags').order_by('-pub_date')
    total_readings = 0
    for article in articles_list:
        article_times_read = article.articlereading_set.all()
        if len(article_times_read) < 1:
            continue
        else:
            total_readings += article_times_read[0].times_read
    paginator = Paginator(articles_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'articles/personal_page.html', {'page_obj': page_obj,
                                                           'total_readings': total_readings})


@login_required()
def personal_article(request, article_id):
    current_user = request.user
    article = Article.objects.filter(
        id=article_id).first()
    if not article:
        return render(request, 'articles/not_exists.html')
    else:
        if article.author_id != current_user.id:
            return render(request, 'articles/not_yours.html')
        likes = Reaction.objects.filter(
            article=article).filter(value=1).count()
        dislikes = Reaction.objects.filter(
            article=article).filter(value=-1).count()
        article_read = ArticleReading.objects.filter(article=article).first()
        times_read = 0
        if article_read:
            times_read = article_read.times_read
        message_to_user = 0
        reaction = Reaction.objects.filter(
            Q(article=article) & Q(author=current_user)).first()
        if reaction:
            if reaction.value == -1:
                message_to_user = "You disliked your article"
            elif reaction.value == 1:
                message_to_user = "You liked your article"
        return render(request, 'articles/personal_article.html', {'article': article,
                                                                  'likes': likes,
                                                                  'dislikes': dislikes,
                                                                  'message_to_user': message_to_user,
                                                                  'times_read': times_read})


def public_article(request, article_id):
    current_user = request.user
    article = Article.objects.select_related('author').\
        filter(id=article_id).first()

    if not article:
        return render(request, 'articles/not_exists.html')
    else:
        # comments = Comment.objects.select_related('commentator').filter(
        #     article=article).order_by('-pub_date').all()
        likes = Reaction.objects.filter(
            article=article).filter(value=1).count()
        dislikes = Reaction.objects.filter(
            article=article).filter(value=-1).count()
        message_to_user = None
        article_read = ArticleReading.objects.filter(article=article).first()
        times_read = 0
        subscription_status = 'You are not subscribed to this author'
        channel = Channel.objects.filter(owner=article.author).first()
        subscription = Subscription.objects.filter(
            Q(subscriber=current_user) &
            Q(channel=channel)
        ).first()
        if subscription:
            subscription_status = 'You are subscribed to this author'
        if article.author == current_user:
            subscription_status = 'This article belongs to you'
        if not article_read:
            if current_user.is_authenticated:
                article_read = ArticleReading(times_read=1, article=article)
                article_read.save()
                times_read = article_read.times_read
        else:
            if current_user.is_authenticated:
                article_read.times_read += 1
                article_read.save()
            times_read = article_read.times_read
        if current_user.is_authenticated:
            reaction = Reaction.objects.filter(
                Q(article=article) & Q(author=current_user)).first()
            if reaction:
                if reaction.value == -1:
                    message_to_user = "You disliked this article"
                elif reaction.value == 1:
                    message_to_user = "You liked this article"
        return render(request, 'articles/public_article.html', {'article': article,
                                                                # 'comments': comments,
                                                                'likes': likes,
                                                                'dislikes': dislikes,
                                                                'message_to_user': message_to_user,
                                                                'times_read': times_read,
                                                                'subscription_status': subscription_status
                                                                })


@ login_required()
def delete_article(request,  article_id):
    current_user = request.user
    article = Article.objects.filter(id=article_id).first()
    if not article:
        return render(request, 'articles/not_exists.html')
    else:
        if article.author_id != current_user.id:
            return render(request, 'articles/not_yours.html')
        else:
            article.delete()
            messages.info(request, 'Article was successfully deleted')
            return HttpResponseRedirect(reverse('articles:personal-page'))


@login_required()
def leave_comment(request, article_id):
    current_user = request.user
    article = Article.objects.filter(
        pk=article_id).select_related('author').first()
    if not article:
        return render(request, 'articles/not_exists.html')
    else:
        if request.method == 'POST':
            form = LeaveCommentForm(request.POST)
            if form.is_valid():
                form.instance.commentator = current_user
                form.instance.article = article
                form.save()
                return HttpResponseRedirect(reverse('articles:public-article', args=(article_id, )))
        else:
            form = LeaveCommentForm()
            return render(request, 'articles/leave_comment.html', {'form': form, 'article': article})


@login_required()
def author_comment(request, article_id):
    current_user = request.user
    article = Article.objects.filter(pk=article_id).first()
    if not article:
        return render(request, 'articles/not_exists.html')
    else:
        if article.author_id != current_user.id:
            return render(request, 'articles/not_yours.html')
        else:
            if request.method == 'POST':
                form = LeaveCommentForm(request.POST)
                if form.is_valid():
                    form.instance.commentator = current_user
                    form.instance.article = article
                    form.save()
                    return HttpResponseRedirect(reverse('articles:personal-article', args=(article_id, )))
            else:
                form = LeaveCommentForm()
                return render(request, 'articles/author_comment.html', {'form': form, 'article': article})


@login_required()
def leave_like(request, article_id):
    current_user = request.user
    article = Article.objects.filter(pk=article_id).first()
    if not article:
        return render(request, 'articles/not_exists.html')
    else:
        reaction = Reaction.objects.filter(
            Q(article=article) & Q(author=current_user)
        ).first()
        if reaction:
            if reaction.value == 1:
                # if someone hits like button, but it is already like, we delete this reaction
                reaction.delete()
                # this solves the bug
                article_read = ArticleReading.objects.filter(
                    article=article).first()
                article_read.times_read -= 1
                article_read.save()
                return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
            elif reaction.value == -1:
                # if value of reaction for current user is dislike (-1),
                # then hitting like button value of reaction becomes 1 (like value)
                reaction.value = 1
                reaction.save()
                # this solves the bug
                article_read = ArticleReading.objects.filter(
                    article=article).first()
                article_read.times_read -= 1
                article_read.save()
                return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
        else:
            # if user hasn't left any reaction up to this moment
            # then hitting like button makes reaction like with value 1
            like = Reaction(author=current_user, article=article, value=1)
            like.save()
            article_read = ArticleReading.objects.filter(
                article=article).first()
            article_read.times_read -= 1
            article_read.save()
            return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))


@login_required()
def leave_dislike(request, article_id):
    current_user = request.user
    article = Article.objects.filter(pk=article_id).first()
    if not article:
        return render(request, 'articles/not_exists.html')
    else:
        reaction = Reaction.objects.filter(
            Q(article=article) & Q(author=current_user)
        ).first()
        if reaction:
            if reaction.value == -1:
                # if someone hits dislike button, but it is already like, we delete this reaction
                reaction.delete()
                article_read = ArticleReading.objects.filter(
                    article=article).first()
                article_read.times_read -= 1
                article_read.save()
                return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
            elif reaction.value == 1:
                # if value of reaction for current user is like (1),
                # then hitting dislike button value of reaction becomes -1 (dislike value)
                reaction.value = -1
                reaction.save()
                article_read = ArticleReading.objects.filter(
                    article=article).first()
                article_read.times_read -= 1
                article_read.save()
                return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
        else:
            # if user hasn't left any reaction up to this moment
            # then hitting like button makes reaction dislike with value -1
            dislike = Reaction(author=current_user, article=article, value=-1)
            dislike.save()
            article_read = ArticleReading.objects.filter(
                article=article).first()
            article_read.times_read -= 1
            article_read.save()
            return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))


def trending_tags(request):
    # find 5 newest articles and order them by how many times they were read
    # articlereading is ordered through metaclass of model ArticleReading
    # by times read in DESC order
    past_date = timezone.now() - timedelta(days=3)
    future_date = timezone.now() + timedelta(days=3)
    articles = Article.objects.select_related('author').\
        filter(
        Q(pub_date__gt=past_date) &
        Q(pub_date__lt=future_date)
    ).order_by('articlereading').all()[:10]
    tags = []
    for article in articles:
        for tag in article.tags.all():
            tags.append(tag)
    return render(request, 'articles/trending_tags.html', {'tags': tags})


def trending_articles(request):
    past_date = timezone.now() - timedelta(days=3)
    future_date = timezone.now() + timedelta(days=3)
    articles_list = Article.objects.select_related('author').\
        filter(
        Q(pub_date__gt=past_date) &
        Q(pub_date__lt=future_date)
    ).order_by('articlereading').all()[:10]
    paginator = Paginator(articles_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    message_to_user = f'You are seeing articles trending in recent time'
    return render(request, 'articles/public_page.html', {'page_obj': page_obj,
                                                         'message_to_user': message_to_user})


def articles_through_tag(request, tag):
    tag_object = Tag.objects.filter(name=tag).first()
    if not tag_object:
        return render(request, 'articles/not_exists.html')
    else:
        articles_list = Article.objects.filter(
            tags=tag_object).order_by('-pub_date').all()
        paginator = Paginator(articles_list, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        message_to_user = f'You are seeing articles with tag #{tag}'

        return render(request, 'articles/public_page.html', {'page_obj': page_obj,
                                                             'message_to_user': message_to_user})


def author_page(request, author):
    current_user = request.user
    author = User.objects.filter(username=author).first()
    if not author:
        return render(request, 'articles/not_exists.html')
    if current_user == author:
        subscription_status = None
    else:
        subscription_status = 'Subscribe'
        channel = Channel.objects.filter(owner=author).first()
        subscription = Subscription.objects.filter(
            Q(subscriber=current_user) &
            Q(channel=channel)
        ).first()
        if subscription:
            subscription_status = 'Subscribed'
    articles = Article.objects.filter(
        author=author).order_by('-pub_date').all()
    total_readings = 0
    for article in articles:
        article_times_read = article.articlereading_set.all()
        if len(article_times_read) < 1:
            continue
        else:
            total_readings += article_times_read[0].times_read
    message_to_user = f'You are seeing all articles published by author {author} \
        that were totally read {total_readings} times'
    return render(request, 'articles/author_page.html', {'author': author,
                                                         'message_to_user': message_to_user,
                                                         'subscription_status': subscription_status,
                                                         'articles_number': len(articles),
                                                         'articles': articles,
                                                         'total_readings': total_readings})


def subscribe(request, author):
    current_user = request.user
    author = User.objects.filter(username=author).first()
    if not author:
        return render(request, 'articles/not_exists.html')
    channel = Channel.objects.filter(owner=author).first()
    if channel.owner == current_user:
        return HttpResponseRedirect(reverse('articles:articles-author', args=(author, )))
    subscription = Subscription.objects.filter(
        Q(subscriber=current_user) &
        Q(channel=channel)
    )
    if subscription:
        subscription.delete()
    else:
        subscription = Subscription(subscriber=current_user, channel=channel)
        subscription.save()
    return HttpResponseRedirect(reverse('articles:articles-author', args=(author, )))


def search_article(request):
    if request.method == 'POST':
        data = request.POST
        form = SearchForm(request.POST)
        if form.is_valid():
            data = request.POST['search_string']
            if data[0] == '#':
                tag = data[1:].lower()
                tag_object = Tag.objects.filter(name=tag).first()
                articles_list = Article.objects.filter(
                    tags=tag_object).order_by('-pub_date').all()
                message_to_user = f'{len(articles_list)} articles with #{tag} were found'
            else:
                articles_list = Article.objects.select_related('author').\
                    filter(
                        Q(title__icontains=data) |
                        Q(content__icontains=data) |
                        Q(author__username__contains=data)
                ).order_by('-pub_date').all()

                message_to_user = f"{len(articles_list)} articles were found that contain '{data}' in its title, \
                    content or author's name"
            paginator = Paginator(articles_list, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            return render(request, 'articles/public_page.html', {'page_obj': page_obj,
                                                                 'message_to_user': message_to_user})
    elif request.method == 'GET':
        form = SearchForm()
        return render(request, 'articles/search_article.html', {'form': form})
