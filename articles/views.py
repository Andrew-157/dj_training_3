from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from .forms import NewUserForm


def index(request):
    return render(request, 'articles/index.html')


def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'articles/success_registration.html',
                          {'username': form.cleaned_data['username']})

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
                return render(request, 'articles/success_login.html', {'username': username})
    else:
        form = AuthenticationForm()

    return render(request, 'articles/login.html', {'form': form})
