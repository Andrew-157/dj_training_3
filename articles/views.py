from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from .forms import NewUserForm


def index(request):
    return render(request, 'articles/index.html')


def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponse(f'success {request.user}')

    elif request.method == 'GET':
        form = NewUserForm()

    return render(request, 'articles/registration.html', {'form': form})
