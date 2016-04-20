from django.shortcuts import render, redirect, render_to_response
from django.contrib import auth
from loginsys.form import ModifyProfile, UploadFileForm
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from web.models import Client, UserBD
from .upload_handler import UploadHandler
from django.db import connections
from django.conf import settings


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
        client_id = Client.objects.filter(user__username=args['username'])
        if client_id.exists():
            client = Client.objects.filter(id=client_id[0].id)[0]
            args['company_logo'] = client.company_logo
            args['company'] = client.company_name
        else:
            args['company_logo'] = '/static/images/no-logo.png'
        return render_to_response('pages/profile.html', args)


def profile_modify(request):
    args = {}
    args.update(csrf(request))
    args['form'] = ModifyProfile()
    if auth.get_user(request):
        username = auth.get_user(request).username
        client_id = Client.objects.filter(user__username=username)
        if client_id.exists():
            args['company_logo'] = Client.objects.filter(id=client_id[0].id)[0].company_logo
        else:
            args['company_logo'] = '/static/images/no-logo.png'
        if request.POST:
            modify_user = ModifyProfile(request.POST)
            if modify_user.is_valid():
                first_name = modify_user.cleaned_data['first_name']
                last_name = modify_user.cleaned_data['last_name']
                company = modify_user.cleaned_data['company']
                Client.objects.filter(user__username=username).update(company_name=company)
                User.objects.filter(username=username).update(first_name=first_name, last_name=last_name)
                return redirect('/profile/')
        return render_to_response('pages/profile_modify.html', args)


def product(request):
    if auth.get_user(request).username:
        user_db = UserBD.objects.filter(username=auth.get_user(request).username)
        if user_db.exists():
            settings.DATABASES['userdb']['NAME'] = user_db[0].title
            settings.DATABASES['userdb']['PASSWORD'] = user_db[0].password
            settings.DATABASES['userdb']['USER'] = user_db[0].username
            cursor = connections['userdb'].cursor()
        if request.POST:
            pass
        return render_to_response('pages/product.html')
    return redirect('/auth/login/')


def upload_file(request):
    args = {}
    args.update(csrf(request))
    args['form'] = UploadFileForm()
    if request.POST:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            UploadHandler(request.FILES['file']).handler()

    return render_to_response('pages/upload_file.html', args)