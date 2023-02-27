from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import NewUserForm


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
