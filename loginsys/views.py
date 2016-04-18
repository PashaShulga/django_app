from django.shortcuts import render, redirect, render_to_response
from django.contrib import auth
from .form import UserCreationForm, PasswordResetRequestForm, SetPasswordForm, AuthenticationForm
from django.core.context_processors import csrf
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
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from web.create_user_db import create_db


def registration(request):
    args = {}
    args.update(csrf(request))
    args['form'] = UserCreationForm()
    if request.POST:
        new_user_form = UserCreationForm(request.POST)
        if new_user_form.is_valid():
            new_user_form.save()
            new_user = auth.authenticate(username=new_user_form.cleaned_data['username'],
                                         password=new_user_form.cleaned_data['password2'])
            auth.login(request, new_user)
            try:
                create_db("DB_%s" % (new_user_form.cleaned_data['username'],))
            except:
                pass
            return redirect('/')
        else:
            args['form'] = new_user_form
    return render_to_response("reg.html", args)


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
                auth.login(request, user)
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
                            'domain': 'example.com',  # or your domain
                            'site_name': 'example',
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'user': user,
                            'token': default_token_generator.make_token(user),
                            'protocol': 'http',
                        }
                        subject_template_name = 'password_reset_subject.txt'
                        email_template_name = 'test_template.html'
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

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class PasswordResetConfirmView(FormView):
    template_name = "test_template.html"
    success_url = '/auth/login/'
    form_class = SetPasswordForm

    @method_decorator(login_required)
    def post(self, request, uidb64=None, token=None, *arg, **kwargs):
        """
        View that checks the hash in a password reset link and presents a
        form for entering a new password.
        """
        UserModel = get_user_model()
        form = self.form_class(request.POST)
        # args = {}
        # args.update(csrf(request))
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
                # return redirect('/', args)
            else:
                messages.error(request, 'Password reset has not been unsuccessful.')
                return self.form_invalid(form)
        else:
            messages.error(request,'The reset password link is no longer valid.')
            return self.form_invalid(form)