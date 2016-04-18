from django.shortcuts import render, redirect, render_to_response
from django.contrib import auth
from loginsys.form import ModifyFrofile


def home(request):
    if auth.get_user(request).username:
        return render_to_response('pages/index.html', {'username': auth.get_user(request).username})
    else:
        return redirect('/auth/login/')


def profile(request):
    args = {}
    if auth.get_user(request):
        args['username'] = auth.get_user(request).username
        args['email'] = auth.get_user(request).email
        args['first_name'] = auth.get_user(request).first_name
        args['last_name'] = auth.get_user(request).last_name

        return render_to_response('pages/profile.html', args)


def profile_modify(request):
    args = {}
    args['form'] = ModifyFrofile()
    if auth.get_user(request):
        return render_to_response('pages/profile_modify.html', args)