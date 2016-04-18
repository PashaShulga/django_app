from django.shortcuts import render, redirect, render_to_response
from django.contrib import auth


def home(request):
    if auth.get_user(request).username:
        return render_to_response('pages/index.html', {'username': auth.get_user(request).username})
    else:
        return redirect('/auth/login/')


def profile(request):
    if auth.get_user(request).username:
        return render_to_response('pages/profile.html')
