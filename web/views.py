from django.shortcuts import redirect, render_to_response, HttpResponse
from django.contrib import auth
from loginsys.form import *
from django.core.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from web.models import Client, UserBD, CustomUser, Company
from .upload_handler import UploadHandler
from django.db import connections
from .xls_parse import XLSParse
import datetime
import json
from django.http import QueryDict
from django.contrib.auth.models import Permission


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
    if user:
        client = Client.objects.filter(user__username=user.username)
        if client.exists():
            args['brand'] = client[0].company_logo
        args.update(get_perm(request))
        # print(get_perm(request))
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
def product_update(request):
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
            query = "update product set {} WHERE id = {}".format(q, id[0])
            c.execute(query)
    return HttpResponse("Ok")


@csrf_exempt
def product_insert(request):
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
            keys = obj.keys()
            values = [i[0] for i in obj.values()]
            s1 = "insert into product {}".format(tuple(keys)).replace("'", '"')
            s2 = " values {}".format(tuple(values))
            c.execute(s1+s2)
        except Exception as e:
            print(e)
        finally:
            c.close()
    return HttpResponse("ok")


@csrf_exempt
def product_delete(request):
    if request.is_ajax():
        request_object = auth.get_user(request)
        c_u = CustomUser.objects.filter(username=request_object.username)
        user_db = UserBD.objects.filter(id=c_u[0].user_id)
        c = connections[user_db[0].username].cursor()
        if request.method == 'DELETE':
            try:
                obj = QueryDict(request.body)
                c.execute("delete from product WHERE id = %s" % (obj['id']))
            except Exception as e:
                print(e)
    return HttpResponse("ok")


def delete_all(request):
    args = {}
    args.update(csrf(request))
    # if request.is_ajax():
    request_object = auth.get_user(request)
    c_u = CustomUser.objects.filter(username=request_object.username)
    user_db = UserBD.objects.filter(id=c_u[0].user_id)
    c = connections[user_db[0].username].cursor()
    if request.method == 'POST':
        try:
            c.execute("delete from product")
        except Exception as e:
            print(e)
        return redirect('/product/')
    return redirect('/')


def custom_product(request, id):
    args = {}
    title_list = []
    request_object = auth.get_user(request)
    if request_object:
        args.update(get_perm(request))
        c_u = CustomUser.objects.get(company_id=id)
        user_db = UserBD.objects.filter(id=c_u.user_id)
        c = connections[user_db[0].username].cursor()
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
                    for ite in range(0, len(title_list)):
                        list_.append(request.POST['column'+str(ite)])
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
                        "width": 22,
                        "validate": "required"
                        }
                        b = json.dumps(fi)
                        fields.append(json.loads(b))
                        continue
                    fi.update({
                        "name": i[0],
                        "type": i[1],
                        "width": 80,
                        "validate": "required",
                        # "selecting": True
                    })
                    b = json.dumps(fi)
                    fields.append(json.loads(b))
                # fields.append({"type": "control"})
                args['fields'] = json.dumps(fields)
            except Exception as e:
                print(e)
            finally:
                c.close()
            return args


@ensure_csrf_cookie
def product(request):
    args = {}
    args.update(csrf(request))
    args['form'] = UploadFileForm()
    title_list = []
    request_object = auth.get_user(request)
    if request_object:
        args.update(get_perm(request))
        c_u = CustomUser.objects.filter(username=request_object.username)
        user_db = UserBD.objects.filter(id=c_u[0].user_id)
        c = connections[user_db[0].username].cursor()
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
                    for ite in range(0, len(title_list)):
                        list_.append(request.POST['column'+str(ite)])
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
                        "width": 22,
                        "validate": "required"
                        }
                        b = json.dumps(fi)
                        fields.append(json.loads(b))
                        continue
                    fi.update({
                        "name": i[0],
                        "type": i[1],
                        "width": 80,
                        "validate": "required",
                        "selecting": True
                    })
                    b = json.dumps(fi)
                    fields.append(json.loads(b))
                fields.append({"type": "control"})
                args['fields'] = json.dumps(fields)
            except Exception as e:
                print(e)
            finally:
                c.close()
        return render_to_response('pages/data_collect.html', args)
    return redirect('/auth/login/')


def upload_file(request):
    args = {}
    args.update(csrf(request))
    args['form'] = UploadFileForm()
    client = Client.objects.filter(user__username=auth.get_user(request).username)
    if client.exists():
        args['brand'] = client[0].company_logo
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
        args.update(get_perm(request))
        client = Client.objects.filter(user__username=auth.get_user(request).username)
        if client.exists():
            args['brand'] = client[0].company_logo
        args['user'] = 'is_staff'
        args['form'] = AdditionalForm()
        form = AdditionalForm(request.POST)
        if request.POST and form.is_valid():
            name_column, type_column = form.cleaned_data['name_column'], form.cleaned_data['type_column']
            c = connections[form.cleaned_data['user']].cursor()
            c.execute("ALTER TABLE product ADD COLUMN %s %s" % (name_column, type_column))
    return render_to_response('pages/add_column.html', args)


def modify_company(request):
    args = {}
    args.update(csrf(request))
    args['form'] = EditCompany()
    request_object = auth.get_user(request)
    if request_object:
        args.update(get_perm(request))
        custom_user = CustomUser.objects.get(id=request_object.id)
        company = Client.objects.filter(id=custom_user.company_id)
        if company.exists():
            args['brand'] = company[0].company_logo
        if company.exists():
            args['company'] = company[0]
        if request.POST:
            edit_company = EditCompany(request.POST, request.FILES)
            if edit_company.is_valid():
                Client.objects.filter(user_id=auth.get_user(request).id).update(
                    company_name=edit_company.cleaned_data['company_name'],
                    address=edit_company.cleaned_data['address'],
                    phone=edit_company.cleaned_data['phone'],
                    website=edit_company.cleaned_data['website'],
                    postal_code=edit_company.cleaned_data['postal_code'])
                return redirect('/edit_company/modify')
    return render_to_response('pages/edit_company_modify.html', args)


def list_company(request):
    args = {}
    request_object = auth.get_user(request)
    if request_object:
        args.update(get_perm(request))
        company = Client.objects.all()
        args['company'] = company
    return render_to_response('pages/list_company.html', args)


def data_analytics(request):
    args = {}
    request_object = auth.get_user(request)
    if request_object:
        args.update(get_perm(request))
        custom_user = CustomUser.objects.get(id=request_object.id)
    return render_to_response('pages/data_analytics.html', args)


def company_users(request):
    args = {}
    request_object = auth.get_user(request)
    args.update(csrf(request))
    args['form'] = EditUser()
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

    return render_to_response('pages/company_users.html', args)


@csrf_exempt
def company_delete_user(request):
    if request.is_ajax():
        if request.method == 'DELETE':
            try:
                print(QueryDict(request.body)['id'])
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
    # args['pp_form'] = PackagePermissions
    # args['us_form'] = UserSettings
    if request_object:
        if request.POST:
            new_company = AddCompany(request.POST)
            try:
                create_db("db_%s" % (new_company.data['username'],), new_company.data['password2'], new_company.data['username'])
            except:
                args['error'] = ("Warning! Database is not create, try again or inform staff")
            u_db = UserBD.objects.filter(username=new_company.data['username'])
            new_user = CustomUser.objects.create_user(username=new_company.data['username'],
                                                      email=new_company.data['email'],
                                                      password=new_company.data['password2'],
                                                      company_type= 1 if new_company.data['package'] == "L" else 2,
                                                      user_id=int(u_db[0].id)
                                                      )
            new_user.save()
            new_client = Client(user_id=new_user.id,
                   phone=new_company.data['phone'], company_name=new_company.data['company_name'],
                   contact_name=new_company.data['contact_name'],
                   email=new_company.data['email'], address=new_company.data['address'])
            new_client.save()
            CustomUser.objects.filter(id=new_user.id).update(company_id=new_client.id)
    return render_to_response('pages/add_company.html', args)


def list_company_change(request, id):
    args = {}
    args.update(csrf(request))
    args.update(get_perm(request))
    if "auth.add_user" in get_perm(request)['user_permission']:
        client = Client.objects.get(id=id)
        args['company'] = client
        args['form'] = ChangeCompany(initial=
                                     {"company_name": client.company_name,
                                      "contact_name": client.contact_name.strip() if client.contact_name is not None else client.contact_name,
                                      "email": client.email.strip() if client.email is not None else client.email,
                                      "address": client.address,
                                      "phone": client.phone}
                                     )
        args['pp_form'] = ChangeCompanyPackage()
        args['user'] = 'is_staff'
        args['table_form'] = AdditionalForm()
        if request.POST:
            cc_package = ChangeCompanyPackage(request.POST)
            if cc_package.is_valid():
                CustomUser.objects.filter(company_id=id).update(
                    company_type=cc_package.data['package'])

            form = AdditionalForm(request.POST)
            if form.is_valid():
                name_column, type_column = form.cleaned_data['name_column'], form.cleaned_data['type_column']
                c = connections[form.cleaned_data['user']].cursor()
                c.execute("ALTER TABLE product ADD COLUMN %s %s" % (name_column, type_column))

            change_conpany = ChangeCompany(request.POST)
            if change_conpany.is_valid():
                Client.objects.filter(id=id).update(email=change_conpany.data['email'],
                                                    address=change_conpany.data['address'],
                                                    company_name=change_conpany.data['company_name'],
                                                    contact_name=change_conpany.data['contact_name'],
                                                    phone=change_conpany.data['phone'])
                redirect('/list_company/change/%s/', id)
        try:
            args.update(custom_product(request, id))
        except:
            pass

    return render_to_response('pages/list_company_change.html', args)