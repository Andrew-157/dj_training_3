from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import NewUserForm, UpdateArticleForm, PublishArticleForm, LeaveCommentForm
from .models import Article, Comment, Reaction, ArticleReading


def index(request):
    return render(request, 'articles/index.html')


def register_request(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            login(request, user)
            messages.info(request, f'Welcome to the Ligma, {username}')
            return redirect('articles:index')

    elif request.method == 'GET':
        form = NewUserForm()

    return render(request, 'articles/registration.html', {'form': form})


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.info(request, f"Welcome back to Ligma, {username}")
                return redirect('articles:index')
    else:
        form = AuthenticationForm()

    return render(request, 'articles/login.html', {'form': form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('articles:index')


@login_required()
def publish_article(request):
    if request.method == 'POST':
        form = PublishArticleForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            form.instance.author = request.user
            obj.save()
            form.save_m2m()
            messages.info(
                request, 'You successfully published new article')
            return HttpResponseRedirect(reverse('articles:personal-page'))

    else:
        form = PublishArticleForm()
    return render(request, 'articles/publish_article.html', {'form': form})


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
    paginator = Paginator(articles_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'articles/personal_page.html', {'page_obj': page_obj})


@login_required()
def personal_article(request, article_id):
    current_user = request.user
    article = Article.objects.filter(id=article_id).first()
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
        message_to_user = None
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
                                                                  'times_read': article_read.times_read})


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
        if current_user.is_authenticated:
            if not article_read:
                article_read = ArticleReading(times_read=1, article=article)
                article_read.save()
            else:
                article_read.times_read += 1
                article_read.save()
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
                                                                'times_read': article_read.times_read})


@login_required()
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
def update_article(request, article_id):
    current_user = request.user
    article = Article.objects.filter(id=article_id).first()
    if not article:
        return render(request, 'articles/not_exists.html')
    else:
        if article.author_id != current_user.id:
            return render(request, 'articles/not_yours.html')
        if request.method == 'POST':
            form = UpdateArticleForm(request.POST, instance=article)
            if form.is_valid():
                form.instance.author = request.user
                form.instance.article = article_id
                form.save()
                messages.info(
                    request, 'You successfully updated this article')
                return HttpResponseRedirect(reverse('articles:personal-article', args=(article_id, )))
        else:
            form = UpdateArticleForm(instance=article)
            return render(request, 'articles/update_article.html', {'form': form, 'article_id': article_id})


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
    article = Article.objects.filter(
        pk=article_id).select_related('author').first()
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


def become_user(request):
    return render(request, 'articles/become_user.html')


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
                return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
            elif reaction.value == -1:
                # if value of reaction for current user is dislike (-1),
                # then hitting like button value of reaction becomes 1 (like value)
                reaction.value = 1
                reaction.save()
                return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
        else:
            # if user hasn't left any reaction up to this moment
            # then hitting like button makes reaction like with value 1
            like = Reaction(author=current_user, article=article, value=1)
            like.save()
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
                return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
            elif reaction.value == 1:
                # if value of reaction for current user is like (1),
                # then hitting dislike button value of reaction becomes -1 (dislike value)
                reaction.value = -1
                reaction.save()
                return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
        else:
            # if user hasn't left any reaction up to this moment
            # then hitting like button makes reaction dislike with value -1
            dislike = Reaction(author=current_user, article=article, value=-1)
            dislike.save()
            return HttpResponseRedirect(reverse('articles:public-article', args=(article_id,)))
