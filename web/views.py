from django.shortcuts import render, redirect, render_to_response
from django.contrib import auth
from loginsys.form import ModifyFrofile
from django.contrib.auth.models import User
from django.core.context_processors import csrf


def home(request):
    args = {}
    args['sitename'] = 'You site'
    if auth.get_user(request).username:
        return render_to_response('pages/index.html', args)
    else:
        return redirect('/auth/login/')


def profile(request):
    args = {}
    args['sitename'] = 'You site'
    if auth.get_user(request):
        args['username'] = auth.get_user(request).username
        args['email'] = auth.get_user(request).email
        args['first_name'] = auth.get_user(request).first_name
        args['last_name'] = auth.get_user(request).last_name

        return render_to_response('pages/profile.html', args)


def profile_modify(request):
    args = {}
    args.update(csrf(request))
    args['form'] = ModifyFrofile()
    if auth.get_user(request):
        username = auth.get_user(request).username
        if request.POST:
            modify_user = ModifyFrofile(request.POST)
            if modify_user.is_valid():
                first_name = modify_user.cleaned_data['first_name']
                last_name = modify_user.cleaned_data['last_name']
                company = modify_user.cleaned_data['company']
                User.objects.filter(username=username).update(first_name=first_name, last_name=last_name)
                return redirect('/profile/')
        return render_to_response('pages/profile_modify.html', args)

def product(request):
    return render_to_response('pages/product.html')