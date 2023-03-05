from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import NewUserForm, UpdateArticleForm, PublishArticleForm, LeaveCommentForm
from .models import Article, Comment, Like, Dislike


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


def publish_article(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PublishArticleForm(request.user, request.POST,)
            if form.is_valid():
                form.save()
                messages.info(
                    request, 'You successfully published new article')
                return HttpResponseRedirect(reverse('articles:personal-page', args=(request.user.id, )))

        else:
            form = PublishArticleForm(request.user)
        return render(request, 'articles/publish_article.html', {'form': form})

    else:
        messages.info(
            request, "You cannot publish articles as you are not authenticated")
        return render(request, 'articles/become_user.html')



def public_page(request):
    articles_list = Article.objects.select_related(
        'author').order_by('-pub_date').all()
    paginator = Paginator(articles_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'articles/public_page.html', {'page_obj': page_obj})


def public_article(request, article_id):
    article = Article.objects.select_related(
        'author').filter(id=article_id).first()
    comments = Comment.objects.select_related('commentator').filter(
        article=article).order_by('-pub_date').all()
    if not article:
        return render(request, 'articles/not_exists.html')

    else:
        return render(request, 'articles/public_article.html', {'article': article, 'comments': comments})


@login_required()
def personal_page(request):
    current_user = request.user
    articles_list = Article.objects.filter(
        author_id=current_user.id).order_by('-pub_date')
    paginator = Paginator(articles_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'articles/personal_page.html', {'page_obj': page_obj})


@login_required()
def personal_article(request, article_id):
    current_user = request.user
    article = Article.objects.filter(id=article_id).first()
    if article:
        if article.author_id != current_user.id:
            return render(request, 'articles/not_yours.html')
        return render(request, 'articles/personal_article.html', {'article': article})
    else:
        return render(request, 'articles/not_exists.html')


@login_required()
def delete_article(request,  article_id):
    current_user = request.user
    article = Article.objects.filter(id=article_id).first()
    if article:
        if article.author_id != current_user.id:
            return render(request, 'articles/not_yours.html')
        else:
            article.delete()
            messages.info(request, 'Article was successfully deleted')
            return HttpResponseRedirect(reverse('articles:personal-page'))
    else:
        return render(request, 'articles/not_exists.html')
    

@login_required()
def update_article(request, article_id):
    current_user = request.user
    article = Article.objects.filter(id=article_id).first()
    if article:
        if article.author_id != current_user.id:
            return render(request, 'articles/not_yours.html')
        if request.method == 'POST':
            form = UpdateArticleForm(current_user, article_id, request.POST, instance=article)
            if form.is_valid():
                form.save()
                messages.info(
                    request, 'You successfully updated this article')
                return HttpResponseRedirect(reverse('articles:personal-article', args=(article_id, )))
        else:
            form = UpdateArticleForm(current_user,
                                        article_id, instance=article)
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
            form = LeaveCommentForm(current_user, article, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('articles:public-article', args=(article_id, )))
        else:
            form = LeaveCommentForm(current_user, article)
            return render(request, 'articles/leave_comment.html', {'form': form, 'article': article})
            

def become_user(request):
    return render(request, 'articles/become_user.html')


def leave_like(request, article_id):
    current_user = request.user
    if not current_user.is_authenticated:
        messages.info(
            request, 'You cannot like this article , you are not authenticated')
        return render(request, 'articles/become_user.html')
    else:
        article = Article.objects.filter(pk=article_id).first()
        if article:
            ...
