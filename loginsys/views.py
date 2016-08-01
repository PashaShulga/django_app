from django.shortcuts import redirect, render_to_response
from web.views import get_perm
from django.contrib import auth
from .form import *
from django.template.context_processors import csrf
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from untitled2.settings import DEFAULT_FROM_EMAIL
from django.views.generic import *
from django.contrib import messages
from django.contrib.auth.models import User, Permission
from django.db.models.query_utils import Q
from web.create_user_db import create_db
from django.utils.translation import ugettext_lazy as _
from web.models import CustomUser, Company, Client, UserBD, update_settings
from django.template import RequestContext


def registration(request):
    args = {}
    args.update(csrf(request))
    args['form'] = UserCreationForm()
    if request.POST:
        new_user_form = UserCreationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password2']
        email = request.POST['email1']
        c_type = int(request.POST['company_type'])
        c_title = request.POST['company_title']
        if username is not None and password is not None and email is not None\
                and c_title is not None and c_type is not None:
            try:
                create_db("db_%s" % (username,), password, username)
            except:
                args['error'] = _("Warning! Database is not create, try again or inform staff")
            u_db = UserBD.objects.filter(username=username)
            if u_db.exists():
                new_user = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                          company_type=c_type, user_id=u_db[0].id,
                                                          primary_root=True)
                company = Client(company_name=c_title, user_id=new_user.id)
                company.save()
                CustomUser.objects.filter(id=new_user.id).update(company_id=company.id)
                new_user.save()

            u = CustomUser.objects.get(username=username)
            permission = None
            if c_type == 1:
                permission = Permission.objects.get(codename='user_short')
            elif c_type == 2:
                permission = Permission.objects.get(codename='user_admin')
            u.user_permissions.add(permission)
            new_user = auth.authenticate(username=username, password=password)
            auth.login(request, new_user)
            update_settings()
            return redirect('/')
        else:
            args['form'] = new_user_form
    return render_to_response("reg.html", args)


def add_new_user(request):
    args = {}
    args.update(csrf(request))
    args['form'] = AddNewUser()
    if auth.get_user(request):
        perm = get_perm(request)
        args.update(perm)
        if request.POST:
            d = request.POST
            # au = AddNewUser(request.POST)
            user_obj = auth.get_user(request)
            c_title = Client.objects.get(user_id=user_obj.id)
            u_db = UserBD.objects.filter(username=user_obj.username)

            if u_db.exists():
                if d['password1'] != d['password2']:
                    args['messages'] = "Password incorrect"
                    return render_to_response('add_user.html', args)

                CustomUser.objects.create_user(username=d['username'], password=d['password2'],
                                                          email=d['email'],
                                                      company_type = 1 if perm['company_type'] == 'L Company' else 2,
                                                      company_id=c_title.id, user_id=u_db[0].id)
            u = CustomUser.objects.get(username=d['username'])
            permission = None
            if d['roles'] == "E":
                permission = Permission.objects.get(codename='user_short')
            if d['roles'] == "M":
                permission = Permission.objects.get(codename='admin')
            # if perm['company_type'] == 'L Package':
            #     permission = Permission.objects.get(codename='user_short')
            # elif perm['company_type'] == 'XL Package':
            #     permission = Permission.objects.get(codename='admin')
            u.user_permissions.add(permission)
    return render_to_response('add_user.html', args)


def add_admin_user(request):
    args = {}
    args.update(csrf(request))
    args['form'] = AddAdminUser()
    if auth.get_user(request):
        perm = get_perm(request)
        args.update(perm)
        if request.POST:
            d = request.POST
            user_obj = auth.get_user(request)
            c_title = Client.objects.get(user_id=user_obj.id)

            if d['password1'] != d['password2']:
                args['messages'] = "Password incorrect"
                return render_to_response('add_admin_user.html', args)
            CustomUser.objects.create_user(username=d['username'], password=d['password2'], is_superuser=True,
                                           is_staff=True)

    return render_to_response('add_admin_user.html', args, context_instance=RequestContext(request))


class LoginUser(FormView):
    template_name = 'login.html'
    success_url = '/'
    form_class = AuthenticationForm

    def post(self, request, *args, **kwargs):
        args = {}
        args.update(csrf(request))
        args['form'] = self.form_class
        if request.POST:
            user_form = AuthenticationForm(request.POST)
            if user_form.is_valid():
                user = auth.authenticate(username=user_form.cleaned_data['username'],
                                         password=user_form.cleaned_data['password'])
                if user is not None:
                    auth.login(request, user)
                else:
                    messages.error(request, "Warning! User or password incorrect")
                return redirect('/')
            else:
                args['error'] = 'User not found or incorrect password/username'
                return render_to_response('login.html',  args)
        else:
            return render_to_response('login.html', args)


def logout(request):
    auth.logout(request)
    return redirect('/auth/login/')


class ResetPasswordRequestView(FormView):
    template_name = "test_template.html"  # code for template is given below the view's code
    success_url = '/auth/login/'
    form_class = PasswordResetRequestForm

    @staticmethod
    def validate_email_address(email):
        '''
        This method here validates the if the input is an email address or not. Its return type is boolean, True if the input is a email address or False if its not.
        '''
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def post(self, request, *args, **kwargs):
        '''
        A normal post request which takes input from field "email_or_username" (in ResetPasswordRequestForm).
        '''
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data["email_or_username"]
            if self.validate_email_address(data) is True:  # uses the method written above
                '''
                If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
                '''
                associated_users = User.objects.filter(Q(email=data) | Q(username=data))
                if associated_users.exists():
                    for user in associated_users:
                        c = {
                            'email': user.email,
                            'domain': request.META['HTTP_HOST'],
                            'site_name': 'your site',
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'user': user,
                            'token': default_token_generator.make_token(user),
                            'protocol': 'http',
                        }
                        subject_template_name = 'password_reset_subject.txt'
                        # copied from django/contrib/admin/templates/registration/password_reset_subject.txt to templates directory
                        email_template_name = 'password_reset_email.html'
                        # copied from django/contrib/admin/templates/registration/test_template.html to templates directory
                        subject = loader.render_to_string(subject_template_name, c)
                        # Email subject *must not* contain newlines
                        subject = ''.join(subject.splitlines())
                        email = loader.render_to_string(email_template_name, c)
                        send_mail(subject, email, DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                        result = self.form_valid(form)
                        messages.success(request,
                                     'An email has been sent to ' + data + ". Please check it's inbox to continue reseting password.")
                        return result
                result = self.form_invalid(form)
                messages.error(request, 'No user is associated with this email address')
                return result
            else:
                '''
                If the input is an username, then the following code will lookup for users associated with that user. If found then an email will be sent to the user's address, else an error message will be printed on the screen.
                '''
                associated_users = User.objects.filter(username=data)
                if associated_users.exists():
                    for user in associated_users:
                        c = {
                            'email': user.email,
                            'domain': request.META['HTTP_HOST'],  # or your domain
                            'site_name': 'your site',
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'user': user,
                            'token': default_token_generator.make_token(user),
                            'protocol': 'http',
                        }
                        subject_template_name = 'password_reset_subject.txt'
                        email_template_name = 'password_reset_email.html'
                        subject = loader.render_to_string(subject_template_name, c)
                        # Email subject *must not* contain newlines
                        subject = ''.join(subject.splitlines())
                        email = loader.render_to_string(email_template_name, c)
                        send_mail(subject, email, DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    result = self.form_valid(form)
                    messages.success(request,
                                     'Email has been sent to ' + data + "'s email address. Please check its inbox to continue reseting password.")
                    return result
                result = self.form_invalid(form)
                messages.error(request, 'This username does not exist in the system.')
                return result
        messages.error(request, 'Invalid Input')
        return self.form_invalid(form)


class PasswordResetConfirmView(FormView):
    template_name = "test_template.html"
    success_url = '/auth/login/'
    form_class = SetPasswordForm

    def post(self, request, uidb64=None, token=None, *arg, **kwargs):
        """
        View that checks the hash in a password reset link and presents a
        form for entering a new password.
        """
        UserModel = get_user_model()
        form = self.form_class(request.POST)
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if form.is_valid():
                new_password = form.cleaned_data['new_password2']
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset.')
                return self.form_valid(form)
            else:
                messages.error(request, 'Password reset has not been unsuccessful.')
                return self.form_invalid(form)
        else:
            messages.error(request,'The reset password link is no longer valid.')
            return self.form_invalid(form)


class ChangePassword(FormView):
    template_name = "change_password.html"
    success_url = '/auth/change_password/'
    form_class = ChangePassForm

    def get(self, request, *args, **kwargs):
        args = {}
        args.update(get_perm(request))
        args['form'] = self.form_class
        return render_to_response("change_password.html", args)

    def post(self, request, *args, **kwargs):
        UserModel = get_user_model()
        form = self.form_class(request.POST)
        user_object = auth.get_user(request)
        try:
            user = UserModel._default_manager.get(pk=user_object.id)
        except:
            user = None
        if user:
            if form.is_valid():
                old_password = form.cleaned_data['old_password']
                c_p = user_object.check_password(old_password)
                if c_p:
                    user.set_password(form.clean_new_password2())
                    user.save()
                    messages.success(request, "Password has been changed.")
                    return self.form_valid(form)
                else:
                    messages.error(request, "Warning! You old password incorrect, please try againe.")
                    return self.form_invalid(form)
            else:
                messages.error(request, "Warning! Password change has not been unsuccessful.")
                return self.form_invalid(form)


class AdminChangePassword(FormView):
    template_name = "change_password.html"
    success_url = '/'
    form_class = ChangeAdminPassword

    def get(self, request, *args, **kwargs):
        args = {}
        args.update(get_perm(request))
        args['form'] = self.form_class
        return render_to_response("change_password.html", args)

    def post(self, request, *args, **kwargs):
        UserModel = get_user_model()
        form = self.form_class(request.POST)
        try:
            user = UserModel._default_manager.get(pk=form.data['username'])
        except:
            user = None
        if user:
            if form.is_valid():
                user.set_password(form.clean_new_password2())
                user.save()
                messages.success(request, "Password has been changed.")
                return self.form_valid(form)
            else:
                messages.error(request, "Warning! Password change has not been unsuccessful.")
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)