from django.shortcuts import render, redirect, render_to_response, HttpResponse
from django.contrib import auth
from loginsys.form import *
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from web.models import Client, UserBD
from .upload_handler import UploadHandler
from django.db import connections
from .xls_parse import XLSParse
import datetime
import json
from django.http import QueryDict


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


@csrf_exempt
def product_update(request):
    if request.is_ajax():
        c = connections[auth.get_user(request).username].cursor()
        if request.method == "PUT":
            obj = QueryDict(request.body)
            obj = dict(obj)
            obj.pop('csrfmiddlewaretoken')
            id = obj.pop('id')
            keys = obj.keys()
            values = [i[0] for i in obj.values()]
            rem = []
            res = None
            for u in keys:
                for y in values:
                    res = "{}='{}'".format(u, y)
                    del values[0]
                    break
                rem.append(res)
            q = str(tuple(rem)).replace("(", '').replace(")", '').replace('"', '')
            query = "update product set {} WHERE id = {}".format(q, id[0])
            c.execute(query)
    return HttpResponse("Ok")


@csrf_exempt
def product_insert(request):
    if request.is_ajax():
        c = connections[auth.get_user(request).username].cursor()
        try:
            obj = request.POST
            obj = dict(obj)
            obj.pop('csrfmiddlewaretoken')
            obj.pop('id')
            keys = obj.keys()
            values = [i[0] for i in obj.values()]
            s1 = "insert into product {}".format(tuple(keys)).replace("'", '"')
            s2 = " values {}".format(tuple(values))
            print(s1+s2)
            c.execute(s1+s2)
        except Exception as e:
            print(e)
        finally:
            c.close()
    return HttpResponse("ok")


@csrf_exempt
def product_delete(request):
    if request.is_ajax():
        c = connections[auth.get_user(request).username].cursor()
        if request.method == 'DELETE':
            try:
                obj = QueryDict(request.body)
                c.execute("delete from product WHERE id = %s" % (obj['id']))
            except Exception as e:
                print(e)
    return HttpResponse("ok")


@ensure_csrf_cookie
def product(request):
    args = {}
    args.update(csrf(request))
    title_list = []
    # upform = UploadFileForm
    args['form'] = UploadFileForm()
    if auth.get_user(request).username:
        user_db = UserBD.objects.filter(username=auth.get_user(request).username)
        c = connections[auth.get_user(request).username].cursor()
        if user_db.exists():
            try:
                c.execute("select column_name from information_schema.columns WHERE table_name = 'product'")
                result = c.fetchall()
                for it in result:
                    title_list.append(it[0])
                args['titles'] = title_list
                args['id'] = result[0]
                args['inputs'] = range(0, len(title_list))
                if request.POST:
                    upform = UploadFileForm(request.POST, request.FILES)
                    if upform.is_valid():
                        UploadHandler(request.FILES['file']).handler()

                        XLSParse(request.FILES['file'], request).parse()
                    list_ = []
                    for iter in range(0, len(title_list)):
                        list_.append(request.POST['column'+str(iter)])
                    s = 'insert into product {}'.format(tuple(title_list)).replace("'", '"')
                    s2 = ' VALUES {}'.format(tuple(list_))
                    c.execute(s+s2)
                c.execute("select * from product")
                l = []
                data = c.fetchall()
                for conversion in data:
                    l.append(list(conversion))
                counter = 0
                res = {}
                ls = []
                while counter < len(data):
                    for i in title_list:
                        for k in l[counter]:
                            if type(k) == datetime.date:
                                res[i] = k.strftime("%Y-%m-%d") #  %H:%M:%S
                            else:
                                res[i] = k
                            del l[counter][0]
                            break
                    counter += 1
                    b = json.dumps(res.copy())
                    ls.append(json.loads(b))
                args['items'] = json.dumps(ls)

                fields = []
                c.execute("SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'product'")
                fi = {}
                for i in c.fetchall():
                    i = list(i)
                    if i[1] == "character" or i[1] == "date":
                        i[1] = "text"
                    elif i[1] == "integer":
                        i[1] = "number"
                    if i[0] == "id":
                        fi = {
                        "name": i[0],
                        "type": i[1],
                        "width": 30,
                        "validate": "required"
                        }
                        b = json.dumps(fi)
                        fields.append(json.loads(b))
                        continue
                    fi.update({
                        "name": i[0],
                        "type": i[1],
                        "width": 80,
                        "validate": "required"
                    })
                    b = json.dumps(fi)
                    fields.append(json.loads(b))
                fields.append({"type": "control"})
                args['fields'] = json.dumps(fields)
            except Exception as e:
                print(e)
            finally:
                c.close()
            return render_to_response('pages/product.html', args)
    return redirect('/auth/login/')


def upload_file(request):
    args = {}
    args.update(csrf(request))
    args['form'] = UploadFileForm()
    if request.POST:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            UploadHandler(request.FILES['file']).handler()

    return render_to_response('pages/xls_uploader.html', args)


def add_column(request):
    args = {}
    args.update(csrf(request))
    args['user'] = ''
    if auth.get_user(request).is_staff:
        args['user'] = 'is_staff'
        args['form'] = AdditionalForm()
        form = AdditionalForm(request.POST)
        if request.POST and form.is_valid():
            name_column, type_column = form.cleaned_data['name_column'], form.cleaned_data['type_column']
            c = connections[form.cleaned_data['user']].cursor()
            c.execute("ALTER TABLE product ADD COLUMN %s %s" % (name_column, type_column))
    return render_to_response('pages/add_column.html', args)


from django.http import JsonResponse
from django.views.generic.edit import CreateView

