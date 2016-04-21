from django.shortcuts import render, redirect, render_to_response
from django.contrib import auth
from loginsys.form import *
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
    args = {}
    if auth.get_user(request).username:
        user_db = UserBD.objects.filter(username=auth.get_user(request).username)
        if user_db.exists():
            c = connections[auth.get_user(request).username].cursor()
            try:
                c.execute("select column_name from information_schema.columns WHERE table_name = 'product'")
                buf = []
                for it in c.fetchall()[1:]:
                    buf.append(it[0])
                args['titles'] = buf

                c.execute("select * from product")

                items = []
                for it in c.fetchall()[0][1:]:
                    items.append(it)
                args['items'] = items
            except Exception as e:
                print(e)
            finally:
                c.close()
        if request.POST:
            pass
        print(args)
        return render_to_response('pages/product.html', args)
    return redirect('/auth/login/')


def upload_file(request):
    args = {}
    args.update(csrf(request))
    args['user'] = ''
    if auth.get_user(request).is_staff:
        args['user'] = 'is_staff'
        args['form'] = AdditionalForm()
        form = AdditionalForm(request.POST)
        if form.is_valid():
            name_column, type_column = form.cleaned_data['name_column'], form.cleaned_data['type_column']
            c = connections[form.cleaned_data['user']].cursor()
            c.execute("ALTER TABLE product ADD COLUMN %s %s" % (name_column, type_column))
    return render_to_response('pages/upload_file.html', args)