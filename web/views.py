from .charts_heandler import *
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response, HttpResponse
from django.contrib import auth
from loginsys.form import *
from django.core.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from web.models import Client, UserBD, CustomUser, Company, Charts
from .upload_handler import UploadHandler
from django.db import connections
from .xls_parse import XLSParse
import datetime
import json
from django.http import QueryDict
from django.contrib.auth.models import Permission
from itertools import groupby
import ast
import os, os.path


def get_perm(request):
    args = {}
    request_object = auth.get_user(request)
    get_custom_user = CustomUser.objects.filter(id=request_object.id)
    if get_custom_user.exists():
        company = Company.objects.filter(id=get_custom_user[0].company_type)
        if company.exists():
            args['company_type'] = str(company[0].title)
        args['user_permission'] = request.user.get_all_permissions()
    return args


def home(request):
    args = {}
    user = auth.get_user(request)
    if str(user) != 'AnonymousUser':
        user_db = UserBD.objects.filter(username=request.user.username)
        c = connections[user_db[0].username].cursor()
        c.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='public'")
        count_of_datacollect = c.fetchall()
        if count_of_datacollect != []:
            args['count_of_datacollect'] = len(count_of_datacollect)
        else:
            args['count_of_datacollect'] = 0

        client = CustomUser.objects.filter(id=request.user.id)
        args['count_of_clients'] = client.count()
        # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # len([name for name in os.listdir(BASE_DIR+'/static/files')
            #                                 if os.path.isfile(os.path.join(BASE_DIR+'/static/files', name))])
        args['count_of_charts'] = Charts.objects.filter(company__user_id=request.user.id).count()
        packages = CustomUser.objects.filter(id=request.user.id)
        if packages.exists():
            args['count_of_packages'] = Company.objects.get(id=packages[0].company_type).title
        args['realise'] = "2016.05.11"
        args['version'] = "1.0"
        args['count_of_connection'] = 0
        args.update(get_perm(request))
        return render_to_response('pages/index.html', args)
    else:
        return redirect('/auth/login/')


def profile(request):
    args = {}
    request_object = auth.get_user(request)
    if request_object:
        args.update(get_perm(request))
        args['username'] = request_object.username
        args['email'] = request_object.email
        args['first_name'] = request_object.first_name
        args['last_name'] = request_object.last_name
        client_id = Client.objects.filter(user__username=request_object.username)
        if client_id.exists():
            client = Client.objects.filter(id=client_id[0].id)[0]
            args['company_logo'] = client.company_logo
            args['company'] = client.company_name
            args['brand'] = client.company_logo
        else:
            args['company_logo'] = '/static/images/no-logo.png'
        return render_to_response('pages/profile.html', args)


def profile_modify(request):
    args = {}
    args.update(csrf(request))
    args['form'] = ModifyProfile()
    request_object = auth.get_user(request)
    if request_object:
        args.update(get_perm(request))
        args['username'] = request_object.username
        client_id = Client.objects.filter(user__username=request_object.username)
        if client_id.exists():
            client = Client.objects.filter(id=client_id[0].id)[0]
            args['company_logo'] = client.company_logo
            args['brand'] = client.company_logo
        else:
            args['company_logo'] = '/static/images/no-logo.png'
        if request.POST:
            modify_user = ModifyProfile(request.POST)
            if modify_user.is_valid():
                first_name = modify_user.cleaned_data['first_name']
                last_name = modify_user.cleaned_data['last_name']
                company = modify_user.cleaned_data['company']
                Client.objects.filter(user__username=request_object.username).update(company_name=company)
                User.objects.filter(username=request_object.username).update(first_name=first_name, last_name=last_name)
                return redirect('/profile/')
        return render_to_response('pages/profile_modify.html', args)


@csrf_exempt
def product_update(request, page_slug):
    if request.is_ajax():
        request_object = auth.get_user(request)
        c_u = CustomUser.objects.filter(username=request_object.username)
        user_db = UserBD.objects.filter(id=c_u[0].user_id)
        c = connections[user_db[0].username].cursor()
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
            query = "update {} set {} WHERE id = {}".format(page_slug, q, id[0])
            c.execute(query)
    return HttpResponse("Ok")


@csrf_exempt
def product_insert(request, page_slug):
    if request.is_ajax():
        request_object = auth.get_user(request)
        c_u = CustomUser.objects.filter(username=request_object.username)
        user_db = UserBD.objects.filter(id=c_u[0].user_id)
        c = connections[user_db[0].username].cursor()
        try:
            obj = request.POST
            obj = dict(obj)
            obj.pop('csrfmiddlewaretoken')
            obj.pop('id')
            obj.pop('')
            keys = obj.keys()
            values = [i[0] for i in obj.values()]
            s1 = "insert into {} {}".format(page_slug, tuple(keys)).replace("'", '"')
            s2 = " values {}".format(tuple(values))
            c.execute(s1 + s2)
        except Exception as e:
            print(e)
        finally:
            c.close()
    return HttpResponse("ok")


@csrf_exempt
def product_delete(request, page_slug):
    if request.is_ajax():
        request_object = auth.get_user(request)
        c_u = CustomUser.objects.filter(username=request_object.username)
        user_db = UserBD.objects.filter(id=c_u[0].user_id)
        c = connections[user_db[0].username].cursor()
        if request.method == 'DELETE':
            try:
                obj = QueryDict(request.body)
                c.execute("delete from %s WHERE id = %s" % (page_slug, obj['id']))
            except Exception as e:
                print(e)
    return HttpResponse("ok")


@csrf_exempt
def delete_all(request, page_slug):
    if request.is_ajax():
        request_object = auth.get_user(request)
        c_u = CustomUser.objects.filter(username=request_object.username)
        user_db = UserBD.objects.filter(id=c_u[0].user_id)
        c = connections[user_db[0].username].cursor()
        if request.method == 'DELETE':
            try:
                c.execute("delete from %s" % (page_slug,))
            except Exception as e:
                print(e)
        return HttpResponse(status=200)


def custom_product(request, id):
    args = {}
    request_object = auth.get_user(request)
    if request_object:
        args.update(get_perm(request))
        c_u = Client.objects.get(id=id)
        c_u = CustomUser.objects.get(id=c_u.user_id)
        user_db = UserBD.objects.filter(id=c_u.user_id)
        c = connections[user_db[0].username].cursor()
        if user_db.exists():
            try:
                c.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='public'")
                table_names = []
                for table_name in c.fetchall():
                    table_names.append(table_name[0])
                args['tables'] = table_names
                title_list = []
                for table in table_names:
                    t_l = []
                    c.execute("select column_name from information_schema.columns WHERE table_name = '%s'" % (table,))
                    result = c.fetchall()
                    k = 0

                    while k < len(result):
                        for it in result:
                            t_l.append(it[0])
                        title_list.append(t_l)
                        k += 1
                        break
                args['titles'] = title_list
                # args['id'] = result[0]
                # args['inputs'] = range(0, len(title_list))
                mail_list = []
                try:
                    for table in table_names:
                        ls = []
                        l = []
                        c.execute("select * from %s" % (table,))
                        data = c.fetchall()
                        for conversion in data:
                            l.append(list(conversion))
                        res = {}
                        for i in title_list:
                            for k in l:
                                for q in i:
                                    for o in k:
                                        if type(o) == datetime.date:
                                            res.update({q: o.strftime("%Y-%m-%d")})  # %H:%M:%S
                                        else:
                                            res.update({q: o})
                                        del k[0]
                                        break
                                ls.append(res.copy())
                            del title_list[0]
                            del l[0]
                            mail_list.append(ls)
                except Exception as e:
                    print(e)
                b = json.dumps(mail_list)
                # print(b)
                args['items'] = b
                fields_main = []
                for table in table_names:
                    fi = {}
                    c.execute(
                        "SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s'" % (
                            table,))
                    fields = []
                    for i in c.fetchall():
                        i = list(i)
                        if i[1] == "character" or i[1] == "date":
                            i[1] = "text"
                        elif i[1] == "integer":
                            i[1] = "number"
                        fi.update({
                            "name": i[0],
                            "type": i[1],
                            "width": 'auto',
                            "validate": "required",
                            "selecting": 'true'
                        })
                        fields.append(fi.copy())
                    fields.append({"type": "control", "width": 70,})
                    fields_main.append(fields)

                args['flds'] = json.dumps(fields_main)
            except Exception as e:
                print(e)
            finally:
                c.close()
            # print(args['items'])
            # print(args['fields'])
            return args


@ensure_csrf_cookie
def product(request, page_slug):
    args = {}
    args.update(csrf(request))
    args['form'] = UploadFileForm()
    title_list = []
    request_object = auth.get_user(request)
    if request_object:
        args.update(get_perm(request))
        c_u = CustomUser.objects.filter(username=request_object.username).first()
        user_db = UserBD.objects.filter(id=c_u.user_id)
        c = connections[user_db.first().username].cursor()
        if user_db.exists():
            try:
                c.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='public'")
                table_names = []
                for table_name in c.fetchall():
                    table_names.append(table_name[0])
                args['tables'] = table_names
                if request.POST:
                    upform = UploadFileForm(request.POST, request.FILES)
                    if upform.is_valid():
                        UploadHandler(request.FILES['file']).handler()
                        if upform.cleaned_data['file_type'] == 'xls':
                            XLSParse(request.FILES['file'], request,
                                     str(upform.cleaned_data['table_name']).lower()).xls_parse()
                        elif upform.cleaned_data['file_type'] == 'csv':
                            XLSParse(request.FILES['file'], request,
                                     str(upform.cleaned_data['table_name']).lower()).csv_parse()
                        return redirect('/product/%s/' % (page_slug,))

                    if upform.cleaned_data['table_name'] in table_names:
                        list_ = []
                        for ite in range(0, len(title_list)):
                            list_.append(request.POST['column' + str(ite)])
                        s = 'insert into {} {}'.format(upform.cleaned_data['table_name'], tuple(title_list)).replace(
                            "'", '"')
                        s2 = ' VALUES {}'.format(tuple(list_))
                        c.execute(s + s2)

                c.execute("select column_name from information_schema.columns WHERE table_name = '%s'" % (page_slug,))
                result = c.fetchall()
                for it in result:
                    title_list.append(it[0])
                args['titles'] = title_list
                args['id'] = result[0]
                args['inputs'] = range(0, len(title_list))

                c.execute("select * from %s" % (page_slug,))
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
                                res[i] = k.strftime("%Y-%m-%d")  # %H:%M:%S
                            else:
                                res[i] = k
                            del l[counter][0]
                            break
                    counter += 1
                    b = json.dumps(res.copy())
                    ls.append(json.loads(b))
                args['items'] = json.dumps(ls)

                fields = []
                c.execute("SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s'" % (
                page_slug,))
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
                            "width": 50,
                            "validate": "required"
                        }
                        b = json.dumps(fi)
                        fields.append(json.loads(b))
                        continue
                    fi.update({
                        "name": i[0],
                        "type": i[1],
                        "width": 'auto',
                        "validate": "required",
                        "selecting": True
                    })
                    b = json.dumps(fi)
                    fields.append(json.loads(b))
                fields.append({"type": "control", "width": 70,})
                args['fields'] = json.dumps(fields)
            except Exception as e:
                print(e)
            finally:
                c.close()
        return render_to_response('pages/data_collect.html', args, context_instance=RequestContext(request))
    return redirect('/auth/login/')


# def upload_file(request):
#     args = {}
#     args.update(csrf(request))
#     args['form'] = UploadFileForm()
#     client = Client.objects.filter(user__username=auth.get_user(request).username)
#     if client.exists():
#         args['brand'] = client[0].company_logo
#     if request.POST:
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 UploadHandler(request.FILES['file']).handler()
#                 return redirect('/')
#             except:
#                 return redirect('/')
#     return render_to_response('pages/xls_uploader.html', args)


# def add_column(request):
#     args = {}
#     args.update(csrf(request))
#     args['user'] = ''
#     if auth.get_user(request).is_staff:
#         args.update(get_perm(request))
#         client = Client.objects.filter(user__username=auth.get_user(request).username)
#         if client.exists():
#             args['brand'] = client[0].company_logo
#         args['user'] = 'is_staff'
#         args['form'] = AdditionalForm()
#         form = AdditionalForm(request.POST)
#         if request.POST and form.is_valid():
#             name_column, type_column = form.cleaned_data['name_column'], form.cleaned_data['type_column']
#             c = connections[form.cleaned_data['user']].cursor()
#             c.execute("ALTER TABLE product ADD COLUMN %s %s" % (name_column, type_column))
#     return render_to_response('pages/add_column.html', args)


def modify_company(request):
    args = {}
    args.update(csrf(request))
    c = Client.objects.get(user_id=auth.get_user(request).id)
    args['form'] = EditCompany(
        initial={"company_name": c.company_name, "address": c.address, "postal_code": c.postal_code,
                 "phone": c.phone, "website": c.website})
    request_object = auth.get_user(request)
    if request_object:
        args.update(get_perm(request))
        custom_user = CustomUser.objects.get(id=request_object.id)
        company = Client.objects.filter(id=custom_user.company_id)
        if company.exists():
            args['brand'] = company[0].company_logo
        if company.exists():
            args['company'] = company[0]
        if request.is_ajax():
            Client.objects.filter(user_id=auth.get_user(request).id).update(
                company_name=request.POST['company_name'],
                address=request.POST['address'],
                phone=request.POST['phone'],
                website=request.POST['website'],
                postal_code=request.POST['postal_code'])
            # return redirect('/edit_company/modify')
    return render_to_response('pages/edit_company_modify.html', args)


def list_company(request):
    args = {}
    request_object = auth.get_user(request)
    if request_object:
        args.update(get_perm(request))
        company = Client.objects.all()
        args['company'] = company
    return render_to_response('pages/list_company.html', args)


def company_users(request):
    args = {}
    request_object = auth.get_user(request)
    args.update(csrf(request))
    args['form'] = EditUser
    # if request.is_ajax():
    #     initial_user = CustomUser.objects.get(id=request.POST['id'])
    #     args['form'] = EditUser(initial={"username": initial_user.username, "email": initial_user.email,
    #                                      "first_name": initial_user.first_name, "last_name": initial_user.last_name})
    if request_object:
        args.update(get_perm(request))
        company = Client.objects.filter(user_id=auth.get_user(request).id)
        if company.exists():
            args['company_name'] = company[0].company_name
            c_u = CustomUser.objects.filter(company_id=company[0].id)
            custom_user = [u.id for u in c_u]
            # if c_u.exists():
            #     pass
            if len(custom_user) > 1:
                args['users'] = Client.objects.raw("""SELECT auth_user.id, auth_user.username, auth_user.email,
                              auth_user.first_name, auth_user.last_name, auth_permission.codename FROM auth_user
                          LEFT JOIN auth_user_user_permissions ON auth_user.id = auth_user_user_permissions.user_id
                          LEFT JOIN auth_permission ON auth_user_user_permissions.permission_id = auth_permission.id
                        WHERE auth_user.id in {}""".format(tuple(custom_user)))
            elif len(custom_user) == 1:
                args['users'] = Client.objects.raw("""SELECT auth_user.id, auth_user.username, auth_user.email,
                          auth_user.first_name, auth_user.last_name, auth_permission.codename FROM auth_user
                      LEFT JOIN auth_user_user_permissions ON auth_user.id = auth_user_user_permissions.user_id
                      LEFT JOIN auth_permission ON auth_user_user_permissions.permission_id = auth_permission.id
                    WHERE auth_user.id = {}""".format(custom_user[0]))
            else:
                args['users'] = False

        if request.POST:
            edit_user = EditUser(request.POST)
            if edit_user.is_valid():
                CustomUser.objects.filter(id=int(edit_user.cleaned_data['set_user_id'])).update(
                    username=edit_user.cleaned_data['username'], email=edit_user.cleaned_data['email'],
                    first_name=edit_user.cleaned_data['first_name'], last_name=edit_user.cleaned_data['last_name']
                )
                c_user = CustomUser.objects.filter(id=int(edit_user.cleaned_data['set_user_id']))
                if edit_user.cleaned_data['roles'] == "E":
                    p = Permission.objects.get(codename='user_short')
                    c_user[0].user_permissions = [p.id]
                elif edit_user.cleaned_data['roles'] == "M":
                    p = Permission.objects.get(codename='admin')
                    c_user[0].user_permissions = [p.id]
    return render_to_response('pages/company_users.html', args)


@csrf_exempt
def company_delete_user(request):
    if request.is_ajax():
        if request.method == 'DELETE':
            try:
                CustomUser.objects.filter(id=QueryDict(request.body)['id']).delete()
            except Exception as e:
                print(e)
    return HttpResponse(status=200)


def add_new_company(request):
    from web.create_user_db import create_db
    args = {}
    args.update(get_perm(request))
    request_object = auth.get_user(request)
    args.update(csrf(request))
    args['form'] = AddCompany()
    if request_object:
        if request.is_ajax():
            new_company = AddCompany(request.POST)
            try:
                create_db("db_%s" % (new_company.data['username'],), new_company.data['password2'],
                          new_company.data['username'])
            except:
                args['error'] = ("Warning! Database is not create, try again or inform staff")
            u_db = UserBD.objects.filter(username=new_company.data['username'])
            new_user = CustomUser.objects.create_user(username=new_company.data['username'],
                                                      email=new_company.data['email'],
                                                      password=new_company.data['password2'],
                                                      company_type=1 if new_company.data['package'] == "L" else 2,
                                                      user_id=int(u_db[0].id)
                                                      )
            new_user.save()
            new_client = Client(user_id=new_user.id,
                                phone=new_company.data['phone'], company_name=new_company.data['company_name'],
                                contact_name=new_company.data['contact_name'],
                                email=new_company.data['email'], address=new_company.data['address'])
            new_client.save()
            CustomUser.objects.filter(id=new_user.id).update(company_id=new_client.id)
    return render_to_response('pages/add_company.html', args, context_instance=RequestContext(request))


def charts_save(query_dict, cursor, company_id):
    query_dict = dict(query_dict)
    query_dict.pop('csrfmiddlewaretoken')
    query_list = []
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='public'")
    tables_name = cursor.fetchall()
    tables_name = [tab_name[0] for tab_name in tables_name]
    for table in query_dict['table']:
        if table in tables_name:
            query_list.append(table)
            charts = Charts(table_name=table, columns_name=query_dict[table], chart_type=query_dict['chart_type'],
                   y_name="", company_id=company_id)
            charts.save()


@csrf_exempt
def get_table_columns_ajax(request):
    if request.is_ajax():
        if request.POST:
            company_id = request.POST['company_id'].split("/")[3]
            custom_user = CustomUser.objects.get(company_id=company_id)
            c = connections[custom_user.username].cursor()
            try:
                c.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s'" %
                          (request.POST['table'],))
                query_result = [x[0] for x in c.fetchall()][1:]
                query_result = json.dumps({"data": query_result})
                return HttpResponse(status=200, content=query_result)
            except Exception as e:
                print(e)
            finally:
                c.close()
    return HttpResponse(status=200)


def data_analytics_custom(request):
    args = {}
    request_object = auth.get_user(request)
    ar = None
    if request_object:
        args.update(get_perm(request))
        custom_user = CustomUser.objects.filter(id=request_object.id).first()
        userdb = UserBD.objects.filter(username=custom_user.username)
        c = connections[userdb[0].username].cursor()
        chart = Charts.objects.filter(company_id=custom_user.company_id)
        axis = {}
        result = []
        main_ = []
        result_query = []
        type_chart = []
        label_chart = []
        if chart.exists():
            args['exist'] = True
            for chart_object in list(chart):
                ar = chart_object.columns_name
                ar = ast.literal_eval(ar)
                label_chart.append(ar)
                if len(ar) == 1:
                    query = ("select %s from %s" % (ar[0], chart_object.table_name))
                else:
                    query = ("select %s from %s" % (tuple(ar), chart_object.table_name)).replace("'", '').\
                        replace("(", " ").replace(")", " ")
                c.execute(query)
                result_query.append(c.fetchall())
                type_chart.append(ast.literal_eval(chart_object.chart_type)[0])

            for res in result_query:
                result1 = []
                for k, group in groupby(res, lambda x: x[0]):
                    e = [r[1] for r in group]
                    e.insert(0, str(k))
                    result1.append(e)
                result.append(result1)
            j_data = json.dumps(result)
            chart = ChartsHandler().plotting(json_data=j_data, type_chart=type_chart)
            main_.append(chart)
            axis.update({
                "y": {
                    "label": {
                        "text": ar[0],
                        "position": "outer-middle"
                    }
                }
            })
            args['axis'] = axis
            args['main'] = [i for i in range(len(result))]
            args['j_data'] = main_
            args['label_chart'] = label_chart
        else:
            args['exist'] = False
    return args


def data_analytics_admin(request, cursor, id):
    args = {}
    request_object = auth.get_user(request)
    ar = None
    if request_object:
        args.update(get_perm(request))
        c = cursor
        custom_user = CustomUser.objects.filter(company_id=id).first()
        chart = Charts.objects.filter(company_id=custom_user.company_id)
        axis = {}
        label_chart = []
        result = []
        main_ = []
        result_query = []
        type_chart = []
        id_list = []
        if chart.exists():
            args['exist'] = True
            for chart_object in list(chart):
                id_list.append(chart_object.id)
                ar = chart_object.columns_name
                ar = ast.literal_eval(ar)
                label_chart.append(chart_object.table_name)
                if len(ar) == 1:
                    query = ("select %s from %s" % (ar[0], chart_object.table_name))
                else:
                    query = ("select %s from %s" % (tuple(ar), chart_object.table_name)).replace("'", '').replace("(", " ").replace(")", " ")
                c.execute(query)
                result_query.append(c.fetchall())
                type_chart.append(ast.literal_eval(chart_object.chart_type)[0])

            for res in result_query:
                result1 = []
                for k, group in groupby(res, lambda x: x[0]):
                    e = [r[1] for r in group]
                    e.insert(0, str(k))
                    result1.append(e)
                result.append(result1)
            j_data = json.dumps(result)
            chart = ChartsHandler().plotting(json_data=j_data, type_chart=type_chart)
            main_.append(chart)
            axis.update({
                "y": {
                    "label": {
                        "text": ar[0],
                        "position": "outer-middle"
                    }
                }
            })
            args['axis'] = axis
            args['main'] = id_list
            args['j_data'] = main_
            args['label_chart'] = label_chart
        else:
            args['exist'] = False
    return args


def data_analytics(request):
    args = data_analytics_custom(request)
    return render_to_response('pages/data_analytics.html', args)


def list_company_change(request, id):
    args = {}
    args.update(csrf(request))
    args.update(get_perm(request))
    if "auth.add_user" in get_perm(request)['user_permission']:
        client = Client.objects.get(id=id)
        args['company'] = client
        args['form_change_company'] = ChangeCompany(initial=
                                     {"company_name": client.company_name,
                                      "contact_name": client.contact_name.strip() if client.contact_name is not None else client.contact_name,
                                      "email": client.email.strip() if client.email is not None else client.email,
                                      "address": client.address,
                                      "phone": client.phone}
                                     )
        args['pp_form'] = ChangeCompanyPackage()
        args['user'] = 'is_staff'
        args['table_form'] = AdditionalForm()
        custom_user = CustomUser.objects.filter(company_id=id)
        c = connections[custom_user[0].username].cursor()
        if request.is_ajax():
            if request.POST['form_type'] == 'analytics':
                charts_save(request.POST, c, id)
            cc_package = ChangeCompanyPackage(request.POST)
            if cc_package.is_valid():
                CustomUser.objects.filter(company_id=id).update(
                    company_type=cc_package.data['package'])

            form = AdditionalForm(request.POST)
            if form.is_valid():
                name_column, type_column, table_name = form.cleaned_data['name_column'], \
                                                       form.cleaned_data['type_column'], form.cleaned_data['table_name']

                c.execute("ALTER TABLE %s ADD COLUMN %s %s" % (table_name, name_column, type_column))

            change_company = ChangeCompany(request.POST)
            if change_company.is_valid():
                Client.objects.filter(id=id).update(email=change_company.data['email'],
                                                    address=change_company.data['address'],
                                                    company_name=change_company.data['company_name'],
                                                    contact_name=change_company.data['contact_name'],
                                                    phone=change_company.data['phone'])
                redirect('/list_company/change/%s/', id)
        c.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='public'")
        tables_name = [tab_name[0] for tab_name in c.fetchall()]
        args['charts'] = ['line', 'scatter plot', 'bar', 'pie', 'combination']
        args['checkboxes'] = tables_name
        args.update(data_analytics_admin(request, c, id))
        args.update(custom_product(request, id))
        # try:
        # table_name = list().append(client.user_id)
        # args.update(custom_product(request, id))
        # except:
        #     pass
    # print(args['main'])
    return render_to_response('pages/list_company_change.html', args, context_instance=RequestContext(request))


@csrf_exempt
def chart_delete(request, company_id, chart_id):
    if request.is_ajax():
        if request.method == "DELETE":
            Charts.objects.filter(id=chart_id).delete()
