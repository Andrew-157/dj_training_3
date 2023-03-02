from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import NewUserForm, UpdateArticleForm, UpdateArticleForm
from .models import Article


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
            form = UpdateArticleForm(request.user, request.POST,)
            if form.is_valid():
                form.save()
                messages.info(
                    request, 'You successfully published new article')
                return HttpResponseRedirect(reverse('articles:personal-page', args=(request.user.id, )))

        else:
            form = UpdateArticleForm(request.user)
        return render(request, 'articles/publish_article.html', {'form': form})

    else:
        messages.info(
            request, "You cannot publish articles as you are not authenticated")
        return render(request, 'articles/become_user.html')


def personal(request, user_id):
    current_user = request.user
    if current_user.is_authenticated and current_user.id == user_id:
        articles = Article.objects.filter(author_id=current_user.id)
        return render(request, 'articles/personal_page.html', {'articles': articles})

    else:
        return render(request, 'articles/not_yours.html')


def personal_article(request, user_id, article_id):
    current_user = request.user
    if current_user.is_authenticated and current_user.id == user_id:
        article = Article.objects.filter(id=article_id).first()
        if article:
            if article.author_id != current_user.id:
                return render(request, 'articles/not_yours.html')
            return render(request, 'articles/personal_article.html', {'article': article})
        else:
            return render(request, 'articles/not_exists.html')


def delete_article(request, user_id, article_id):
    current_user = request.user
    if current_user.is_authenticated and current_user.id == user_id:
        article = Article.objects.filter(id=article_id).first()
        if article:
            if article.author_id != current_user.id:
                return render(request, 'articles/not_yours.html')
            article.delete()
            messages.info(request, 'Article was successfully deleted')
            return HttpResponseRedirect(reverse('articles:personal-page', args=(current_user.id, )))
        else:
            return render(request, 'articles/not_exists.html')


def update_article(request, user_id, article_id):
    current_user = request.user
    if current_user.is_authenticated and current_user.id == user_id:
        article = Article.objects.filter(id=article_id).first()
        if article:
            if article.author_id != current_user.id:
                return render(request, 'articles/not_yours.html')
            if request.method == 'POST':
                form = UpdateArticleForm(
                    current_user,
                    article_id,
                    request.POST,
                    instance=article)
                if form.is_valid():
                    form.save()
                    messages.info(
                        request, 'You successfully updated this article')
                    return HttpResponseRedirect(reverse('articles:personal-article', args=(current_user.id,
                                                                                           article_id, )))
            else:
                form = UpdateArticleForm(current_user,
                                         article_id, instance=article)
                return render(request, 'articles/update_article.html', {'form': form, 'article_id': article_id})


def public(request):
    articles_list = Article.objects.select_related(
        'author').order_by('pub_date').all()
    paginator = Paginator(articles_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'articles/public.html', {'page_obj': page_obj})
